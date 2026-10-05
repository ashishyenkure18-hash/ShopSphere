from datetime import datetime
from app import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    brand = db.Column(db.String(120), index=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    discount = db.Column(db.Numeric(5, 2), default=0)  # percentage
    stock = db.Column(db.Integer, default=0, nullable=False)
    image_url = db.Column(db.String(500))
    rating = db.Column(db.Numeric(3, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def final_price(self):
        price = float(self.price)
        discount = float(self.discount or 0)
        return round(price - (price * discount / 100), 2)

    def to_dict(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "category": self.category.name if self.category else None,
            "name": self.name,
            "description": self.description,
            "brand": self.brand,
            "price": float(self.price),
            "discount": float(self.discount or 0),
            "final_price": self.final_price,
            "stock": self.stock,
            "image_url": self.image_url,
            "rating": float(self.rating or 0),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }