from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid

from app import db
from app.models.order import Order
from app.models.payment import Payment

payments_bp = Blueprint("payments", __name__)


@payments_bp.post("")
@jwt_required()
def make_payment():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    order_id = data.get("order_id")
    method = data.get("payment_method")

    if not order_id or method not in ("COD", "UPI", "Card"):
        return jsonify(error="Bad Request", message="order_id and valid payment_method required"), 400

    order = Order.query.get(order_id)
    if not order or order.user_id != user_id:
        return jsonify(error="Not Found", message="Order not found"), 404

    if order.payment_status == "Paid":
        return jsonify(error="Conflict", message="Order already paid"), 409

    # Mock payment: COD -> Pending, others -> Paid immediately
    status = "Pending" if method == "COD" else "Paid"
    txn_ref = f"TXN-{uuid.uuid4().hex[:10].upper()}"

    payment = Payment.query.filter_by(order_id=order.id).first()
    if payment:
        payment.payment_method = method
        payment.status = status
        payment.transaction_reference = txn_ref
    else:
        payment = Payment(
            order_id=order.id,
            payment_method=method,
            amount=order.total_amount,
            status=status,
            transaction_reference=txn_ref,
        )
        db.session.add(payment)

    order.payment_status = status
    if status == "Paid" and order.order_status == "Pending":
        order.order_status = "Confirmed"

    db.session.commit()
    return jsonify(message="Payment processed", payment=payment.to_dict()), 201


@payments_bp.get("/<int:order_id>")
@jwt_required()
def get_payment(order_id):
    user_id = int(get_jwt_identity())
    order = Order.query.get(order_id)
    if not order:
        return jsonify(error="Not Found", message="Order not found"), 404
    if order.user_id != user_id:
        return jsonify(error="Forbidden", message="Not your order"), 403
    if not order.payment:
        return jsonify(error="Not Found", message="No payment for this order"), 404
    return jsonify(payment=order.payment.to_dict())