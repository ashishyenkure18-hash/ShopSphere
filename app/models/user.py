from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default="user", nullable=False)  # user | admin
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    address = db.Column(db.String(255))
    city = db.Column(db.String(80))
    state = db.Column(db.String(80))
    pincode = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cart = db.relationship("Cart", backref="user", uselist=False, cascade="all, delete-orphan")
    orders = db.relationship("Order", backref="user", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "is_active": self.is_active,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "pincode": self.pincode,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }