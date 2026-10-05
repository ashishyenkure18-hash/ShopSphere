from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from decimal import Decimal

from app import db
from app.models.cart import Cart
from app.models.order import Order, OrderItem, ORDER_STATUSES
from app.models.product import Product
from app.utils.decorators import role_required

orders_bp = Blueprint("orders", __name__)


@orders_bp.post("")
@jwt_required()
def create_order():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    # Build shipping address
    required = ["full_name", "phone", "address", "city", "state", "pincode"]
    for f in required:
        if not data.get(f):
            return jsonify(error="Bad Request", message=f"{f} is required"), 400

    shipping_address = (
        f"{data['full_name']}, {data['phone']}\n"
        f"{data['address']}, {data['city']}, {data['state']} - {data['pincode']}"
    )

    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart or not cart.items:
        return jsonify(error="Bad Request", message="Cart is empty"), 400

    # Validate stock and compute total
    total = Decimal("0.00")
    order_items_data = []
    for item in cart.items:
        product = Product.query.get(item.product_id)
        if not product or product.stock < item.quantity:
            return jsonify(
                error="Bad Request",
                message=f"Insufficient stock for {product.name if product else 'item'}",
            ), 400
        subtotal = Decimal(str(item.price)) * item.quantity
        total += subtotal
        order_items_data.append((product, item.quantity, Decimal(str(item.price)), subtotal))

    order = Order(
        user_id=user_id,
        total_amount=total,
        shipping_address=shipping_address,
        payment_status="Pending",
        order_status="Pending",
    )
    db.session.add(order)
    db.session.flush()  # get order.id

    for product, qty, price, subtotal in order_items_data:
        db.session.add(OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=qty,
            price=price,
            subtotal=subtotal,
        ))
        product.stock -= qty  # reduce stock

    # clear cart
    for item in list(cart.items):
        db.session.delete(item)

    db.session.commit()
    return jsonify(message="Order placed", order=order.to_dict()), 201


@orders_bp.get("")
@jwt_required()
def list_my_orders():
    user_id = int(get_jwt_identity())
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    return jsonify(orders=[o.to_dict(with_items=False) for o in orders])


@orders_bp.get("/<int:oid>")
@jwt_required()
def get_order(oid):
    user_id = int(get_jwt_identity())
    order = Order.query.get(oid)
    if not order:
        return jsonify(error="Not Found", message="Order not found"), 404
    if order.user_id != user_id:
        # allow admins too — but role check is elsewhere; simple ownership here
        return jsonify(error="Forbidden", message="Not your order"), 403
    return jsonify(order=order.to_dict())


@orders_bp.put("/<int:oid>/status")
@role_required("admin")
def update_order_status(oid):
    order = Order.query.get(oid)
    if not order:
        return jsonify(error="Not Found", message="Order not found"), 404
    data = request.get_json() or {}
    new_status = data.get("order_status")
    if new_status not in ORDER_STATUSES:
        return jsonify(error="Bad Request", message=f"Invalid status. Allowed: {ORDER_STATUSES}"), 400
    order.order_status = new_status
    db.session.commit()
    return jsonify(message="Status updated", order=order.to_dict(with_items=False))


@orders_bp.post("/<int:oid>/cancel")
@jwt_required()
def cancel_order(oid):
    user_id = int(get_jwt_identity())
    order = Order.query.get(oid)
    if not order:
        return jsonify(error="Not Found", message="Order not found"), 404
    if order.user_id != user_id:
        return jsonify(error="Forbidden", message="Not your order"), 403
    if order.order_status in ("Shipped", "Out for Delivery", "Delivered"):
        return jsonify(error="Bad Request", message="Cannot cancel at this stage"), 400

    order.order_status = "Cancelled"
    # restock
    for item in order.items:
        product = Product.query.get(item.product_id)
        if product:
            product.stock += item.quantity
    db.session.commit()
    return jsonify(message="Order cancelled", order=order.to_dict(with_items=False))