from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity,
)
from email_validator import validate_email, EmailNotValidError

from app import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    required = ["name", "email", "password"]
    for f in required:
        if not data.get(f):
            return jsonify(error="Bad Request", message=f"{f} is required"), 400

    try:
        validate_email(data["email"])
    except EmailNotValidError as e:
        return jsonify(error="Bad Request", message=str(e)), 400

    if len(data["password"]) < 6:
        return jsonify(error="Bad Request", message="Password must be at least 6 characters"), 400

    if User.query.filter_by(email=data["email"].lower()).first():
        return jsonify(error="Conflict", message="Email already registered"), 409

    user = User(
        name=data["name"].strip(),
        email=data["email"].lower().strip(),
        phone=data.get("phone"),
        role="user",
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role},
    )
    return jsonify(message="Registered", user=user.to_dict(), access_token=token), 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").lower().strip()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify(error="Bad Request", message="Email and password required"), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify(error="Unauthorized", message="Invalid credentials"), 401

    if not user.is_active:
        return jsonify(error="Forbidden", message="Account deactivated"), 403

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role},
    )
    return jsonify(message="Login successful", user=user.to_dict(), access_token=token)


@auth_bp.post("/logout")
@jwt_required()
def logout():
    # With stateless JWT, logout is client-side (delete token).
    return jsonify(message="Logged out")


@auth_bp.get("/profile")
@jwt_required()
def get_profile():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify(error="Not Found", message="User not found"), 404
    return jsonify(user=user.to_dict())


@auth_bp.put("/profile")
@jwt_required()
def update_profile():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify(error="Not Found", message="User not found"), 404

    data = request.get_json() or {}
    for field in ["name", "phone", "address", "city", "state", "pincode"]:
        if field in data:
            setattr(user, field, data[field])

    if "email" in data and data["email"] != user.email:
        if User.query.filter_by(email=data["email"].lower()).first():
            return jsonify(error="Conflict", message="Email already in use"), 409
        user.email = data["email"].lower()

    if "password" in data and data["password"]:
        if len(data["password"]) < 6:
            return jsonify(error="Bad Request", message="Password too short"), 400
        user.set_password(data["password"])

    db.session.commit()
    return jsonify(message="Profile updated", user=user.to_dict())