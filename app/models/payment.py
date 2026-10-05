from datetime import datetime
from app import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), unique=True, nullable=False)
    payment_method = db.Column(db.String(30), nullable=False)  # COD|UPI|Card
    transaction_reference = db.Column(db.String(100))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default="Pending")  # Pending|Paid|Failed|Refunded
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "payment_method": self.payment_method,
            "transaction_reference": self.transaction_reference,
            "amount": float(self.amount),
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }