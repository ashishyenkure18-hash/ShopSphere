"""Run: python seed.py  —  Populates categories, products, and an admin user."""
from app import create_app, db
from app.models.category import Category
from app.models.product import Product
from app.models.user import User

app = create_app()

with app.app_context():
    # --- Categories ---
    cat_data = ["Electronics", "Clothing", "Shoes", "Home & Kitchen", "Books", "Accessories"]
    for name in cat_data:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))
    db.session.commit()
    cats = {c.name: c.id for c in Category.query.all()}
    print("Categories ready:", cats)

    # --- Products ---
    products = [
        ("iPhone 15", "Apple", 79999, 5, 20, 4.7, "Electronics",
         "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=500"),
        ("Samsung Galaxy S24", "Samsung", 74999, 8, 15, 4.5, "Electronics",
         "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500"),
        ("Sony WH-1000XM5", "Sony", 29999, 12, 30, 4.8, "Electronics",
         "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=500"),
        ("Men's Cotton T-Shirt", "Levis", 999, 20, 100, 4.2, "Clothing",
         "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500"),
        ("Women's Denim Jacket", "Zara", 2999, 15, 40, 4.4, "Clothing",
         "https://images.unsplash.com/photo-1544022613-e87ca75a784a?w=500"),
        ("Nike Air Max", "Nike", 8999, 10, 25, 4.6, "Shoes",
         "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500"),
        ("Adidas Ultraboost", "Adidas", 12999, 15, 18, 4.7, "Shoes",
         "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=500"),
        ("Non-Stick Frying Pan", "Prestige", 1499, 25, 50, 4.3, "Home & Kitchen",
         "https://images.unsplash.com/photo-1584990347449-a2d4c2c8bcb0?w=500"),
        ("Coffee Maker", "Philips", 3499, 10, 12, 4.1, "Home & Kitchen",
         "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=500"),
        ("Atomic Habits", "Penguin", 499, 20, 80, 4.9, "Books",
         "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500"),
        ("Clean Code", "Prentice Hall", 1299, 10, 35, 4.8, "Books",
         "https://images.unsplash.com/photo-1532012197267-da84d127e765?w=500"),
        ("Leather Wallet", "Hidesign", 1999, 15, 60, 4.4, "Accessories",
         "https://images.unsplash.com/photo-1627123424574-724758594e93?w=500"),
        ("Smart Watch", "Noise", 2999, 30, 45, 4.0, "Accessories",
         "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500"),
    ]

    added = 0
    for name, brand, price, disc, stock, rating, cat, img in products:
        if not Product.query.filter_by(name=name).first():
            db.session.add(Product(
                name=name, brand=brand, price=price, discount=disc,
                stock=stock, rating=rating, category_id=cats[cat],
                image_url=img, description=f"{name} by {brand}"
            ))
            added += 1
    db.session.commit()
    print(f"Added {added} products. Total now: {Product.query.count()}")

    # --- Admin user ---
    if not User.query.filter_by(email="admin@shop.com").first():
        admin = User(name="Admin", email="admin@shop.com", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Admin created: admin@shop.com / admin123")
    else:
        print("Admin already exists")