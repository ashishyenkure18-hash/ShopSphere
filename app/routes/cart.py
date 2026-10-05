from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.cart import Cart, CartItem
from app.models.product import Product

cart_bp = Blueprint("cart", __name__)


def _get_or_create_cart(user_id):
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()
    return cart


@cart_bp.get("")
@jwt_required()
def view_cart():
    cart = _get_or_create_cart(int(get_jwt_identity()))
    return jsonify(cart=cart.to_dict())


@cart_bp.post("")
@jwt_required()
def add_to_cart():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    if not product_id or quantity < 1:
        return jsonify(error="Bad Request", message="product_id and quantity required"), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify(error="Not Found", message="Product not found"), 404

    cart = _get_or_create_cart(user_id)

    item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()
    current_qty = item.quantity if item else 0
    if current_qty + quantity > product.stock:
        return jsonify(error="Bad Request", message="Insufficient stock"), 400

    if item:
        item.quantity += quantity
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=quantity,
            price=product.final_price,
        )
        db.session.add(item)

    db.session.commit()
    return jsonify(message="Added to cart", cart=cart.to_dict()), 201


@cart_bp.put("/<int:item_id>")
@jwt_required()
def update_cart_item(item_id):
    user_id = int(get_jwt_identity())
    cart = _get_or_create_cart(user_id)
    item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if not item:
        return jsonify(error="Not Found", message="Cart item not found"), 404

    data = request.get_json() or {}
    quantity = int(data.get("quantity", item.quantity))
    if quantity < 1:
        return jsonify(error="Bad Request", message="Quantity must be >= 1"), 400
    if quantity > item.product.stock:
        return jsonify(error="Bad Request", message="Insufficient stock"), 400

    item.quantity = quantity
    item.price = item.product.final_price
    db.session.commit()
    return jsonify(message="Cart updated", cart=cart.to_dict())


@cart_bp.delete("/<int:item_id>")
@jwt_required()
def delete_cart_item(item_id):
    user_id = int(get_jwt_identity())
    cart = _get_or_create_cart(user_id)
    item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if not item:
        return jsonify(error="Not Found", message="Cart item not found"), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify(message="Item removed", cart=cart.to_dict())


@cart_bp.delete("")
@jwt_required()
def clear_cart():
    user_id = int(get_jwt_identity())
    cart = _get_or_create_cart(user_id)
    for item in cart.items:
        db.session.delete(item)
    db.session.commit()
    return jsonify(message="Cart cleared")