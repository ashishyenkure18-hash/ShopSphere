from datetime import datetime
from app import db


ORDER_STATUSES = [
    "Pending", "Confirmed", "Processing",
    "Shipped", "Out for Delivery", "Delivered", "Cancelled",
]


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    payment_status = db.Column(db.String(20), default="Pending")  # Pending|Paid|Failed|Refunded
    order_status = db.Column(db.String(30), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")
    payment = db.relationship("Payment", backref="order", uselist=False, cascade="all, delete-orphan")

    def to_dict(self, with_items=True):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "total_amount": float(self.total_amount),
            "shipping_address": self.shipping_address,
            "payment_status": self.payment_status,
            "order_status": self.order_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if with_items:
            data["items"] = [i.to_dict() for i in self.items]
            if self.payment:
                data["payment"] = self.payment.to_dict()
        return data


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    product = db.relationship("Product")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "name": self.product.name if self.product else None,
            "image_url": self.product.image_url if self.product else None,
            "quantity": self.quantity,
            "price": float(self.price),
            "subtotal": float(self.subtotal),
        }