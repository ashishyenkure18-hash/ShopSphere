from datetime import datetime
from app import db


class Cart(db.Model):
    __tablename__ = "cart"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship("CartItem", backref="cart", cascade="all, delete-orphan", lazy="joined")

    @property
    def total(self):
        return round(sum(i.subtotal for i in self.items), 2)

    def to_dict(self):
        return {
            "id": self.id,
            "items": [i.to_dict() for i in self.items],
            "total": self.total,
        }


class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("cart.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    product = db.relationship("Product")

    @property
    def subtotal(self):
        return round(float(self.price) * self.quantity, 2)

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "name": self.product.name if self.product else None,
            "image_url": self.product.image_url if self.product else None,
            "price": float(self.price),
            "quantity": self.quantity,
            "subtotal": self.subtotal,
            "stock": self.product.stock if self.product else 0,
        }