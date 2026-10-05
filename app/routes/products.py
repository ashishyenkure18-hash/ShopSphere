from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import or_, and_

from app import db
from app.models.product import Product
from app.models.category import Category
from app.utils.decorators import role_required

products_bp = Blueprint("products", __name__)


@products_bp.get("")
def list_products():
    q = Product.query

    # Search
    search = request.args.get("q")
    if search:
        like = f"%{search}%"
        q = q.filter(or_(
            Product.name.ilike(like),
            Product.brand.ilike(like),
            Product.description.ilike(like),
        ))

    # Filters
    category = request.args.get("category")
    if category:
        q = q.join(Category).filter(Category.name == category)

    brand = request.args.get("brand")
    if brand:
        q = q.filter(Product.brand == brand)

    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    if min_price is not None:
        q = q.filter(Product.price >= min_price)
    if max_price is not None:
        q = q.filter(Product.price <= max_price)

    if request.args.get("in_stock") == "true":
        q = q.filter(Product.stock > 0)

    min_rating = request.args.get("min_rating", type=float)
    if min_rating is not None:
        q = q.filter(Product.rating >= min_rating)

    # Sorting
    sort = request.args.get("sort", "newest")
    if sort == "price_asc":
        q = q.order_by(Product.price.asc())
    elif sort == "price_desc":
        q = q.order_by(Product.price.desc())
    elif sort == "popular":
        q = q.order_by(Product.rating.desc())
    else:
        q = q.order_by(Product.created_at.desc())

    # Pagination
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 12, type=int), 100)
    pagination = q.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify(
        products=[p.to_dict() for p in pagination.items],
        total=pagination.total,
        page=pagination.page,
        pages=pagination.pages,
    )


@products_bp.get("/<int:pid>")
def get_product(pid):
    product = Product.query.get(pid)
    if not product:
        return jsonify(error="Not Found", message="Product not found"), 404
    return jsonify(product=product.to_dict())


# ---------- Admin-only CRUD ----------

@products_bp.post("")
@role_required("admin")
def create_product():
    data = request.get_json() or {}
    required = ["name", "price", "stock", "category_id"]
    for f in required:
        if data.get(f) is None:
            return jsonify(error="Bad Request", message=f"{f} is required"), 400

    if not Category.query.get(data["category_id"]):
        return jsonify(error="Bad Request", message="Invalid category_id"), 400

    product = Product(
        name=data["name"],
        description=data.get("description"),
        brand=data.get("brand"),
        price=data["price"],
        discount=data.get("discount", 0),
        stock=data["stock"],
        image_url=data.get("image_url"),
        rating=data.get("rating", 0),
        category_id=data["category_id"],
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(message="Product created", product=product.to_dict()), 201


@products_bp.put("/<int:pid>")
@role_required("admin")
def update_product(pid):
    product = Product.query.get(pid)
    if not product:
        return jsonify(error="Not Found", message="Product not found"), 404

    data = request.get_json() or {}
    for field in ["name", "description", "brand", "price", "discount",
                  "stock", "image_url", "rating", "category_id"]:
        if field in data:
            setattr(product, field, data[field])

    db.session.commit()
    return jsonify(message="Product updated", product=product.to_dict())


@products_bp.delete("/<int:pid>")
@role_required("admin")
def delete_product(pid):
    product = Product.query.get(pid)
    if not product:
        return jsonify(error="Not Found", message="Product not found"), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify(message="Product deleted")