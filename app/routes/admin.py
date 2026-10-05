from flask import Blueprint, jsonify, request
from sqlalchemy import func

from app import db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order
from app.utils.decorators import role_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/stats")
@role_required("admin")
def stats():
    total_users = User.query.filter_by(role="user").count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter(Order.order_status.in_(
        ["Pending", "Confirmed", "Processing", "Shipped", "Out for Delivery"]
    )).count()
    completed_orders = Order.query.filter_by(order_status="Delivered").count()

    total_sales = db.session.query(
        func.coalesce(func.sum(Order.total_amount), 0)
    ).filter(Order.order_status != "Cancelled").scalar()

    return jsonify(
        total_users=total_users,
        total_products=total_products,
        total_orders=total_orders,
        pending_orders=pending_orders,
        completed_orders=completed_orders,
        total_sales=float(total_sales or 0),
    )


@admin_bp.get("/orders")
@role_required("admin")
def all_orders():
    q = Order.query
    status = request.args.get("status")
    if status:
        q = q.filter(Order.order_status == status)
    search = request.args.get("q")
    if search and search.isdigit():
        q = q.filter(Order.id == int(search))

    orders = q.order_by(Order.created_at.desc()).all()
    return jsonify(orders=[o.to_dict(with_items=False) for o in orders])


@admin_bp.get("/orders/<int:oid>")
@role_required("admin")
def order_detail(oid):
    order = Order.query.get(oid)
    if not order:
        return jsonify(error="Not Found", message="Order not found"), 404
    return jsonify(order=order.to_dict())


@admin_bp.get("/users")
@role_required("admin")
def all_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify(users=[u.to_dict() for u in users])


@admin_bp.put("/users/<int:uid>/toggle")
@role_required("admin")
def toggle_user(uid):
    user = User.query.get(uid)
    if not user:
        return jsonify(error="Not Found", message="User not found"), 404
    if user.role == "admin":
        return jsonify(error="Forbidden", message="Cannot deactivate admin"), 403
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify(message="User updated", user=user.to_dict())