from flask import Blueprint, request, jsonify
from app import db
from app.models.category import Category
from app.utils.decorators import role_required

categories_bp = Blueprint("categories", __name__)


@categories_bp.get("")
def list_categories():
    cats = Category.query.order_by(Category.name).all()
    return jsonify(categories=[c.to_dict() for c in cats])


@categories_bp.post("")
@role_required("admin")
def create_category():
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify(error="Bad Request", message="Name required"), 400
    if Category.query.filter_by(name=data["name"]).first():
        return jsonify(error="Conflict", message="Category exists"), 409

    cat = Category(name=data["name"], description=data.get("description"))
    db.session.add(cat)
    db.session.commit()
    return jsonify(message="Category created", category=cat.to_dict()), 201


@categories_bp.put("/<int:cid>")
@role_required("admin")
def update_category(cid):
    cat = Category.query.get(cid)
    if not cat:
        return jsonify(error="Not Found", message="Category not found"), 404
    data = request.get_json() or {}
    if "name" in data:
        cat.name = data["name"]
    if "description" in data:
        cat.description = data["description"]
    db.session.commit()
    return jsonify(message="Category updated", category=cat.to_dict())


@categories_bp.delete("/<int:cid>")
@role_required("admin")
def delete_category(cid):
    cat = Category.query.get(cid)
    if not cat:
        return jsonify(error="Not Found", message="Category not found"), 404
    if cat.products.count() > 0:
        return jsonify(error="Conflict", message="Category has products"), 409
    db.session.delete(cat)
    db.session.commit()
    return jsonify(message="Category deleted")