from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Import models so Alembic/SQLAlchemy sees them
    from app.models import user, category, product, cart, order, payment  # noqa

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.products import products_bp
    from app.routes.categories import categories_bp
    from app.routes.cart import cart_bp
    from app.routes.orders import orders_bp
    from app.routes.payments import payments_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(products_bp, url_prefix="/api/products")
    app.register_blueprint(categories_bp, url_prefix="/api/categories")
    app.register_blueprint(cart_bp, url_prefix="/api/cart")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")
    app.register_blueprint(payments_bp, url_prefix="/api/payments")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # ---------- Error handlers ----------
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(error="Bad Request", message=str(e)), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify(error="Unauthorized", message=str(e)), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify(error="Forbidden", message=str(e)), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="Not Found", message=str(e)), 404

    @app.errorhandler(409)
    def conflict(e):
        return jsonify(error="Conflict", message=str(e)), 409

    @app.errorhandler(500)
    def server_error(e):
        return jsonify(error="Internal Server Error", message=str(e)), 500

    # ---------- Frontend page routes ----------
    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/login")
    def login_page():
        return render_template("login.html")

    @app.route("/register")
    def register_page():
        return render_template("register.html")

    @app.route("/products")
    def products_page():
        return render_template("products.html")

    @app.route("/product/<int:pid>")
    def product_details_page(pid):
        return render_template("product-details.html", product_id=pid)

    @app.route("/cart")
    def cart_page():
        return render_template("cart.html")

    @app.route("/checkout")
    def checkout_page():
        return render_template("checkout.html")

    @app.route("/payment")
    def payment_page():
        return render_template("payment.html")

    @app.route("/order-success")
    def order_success_page():
        return render_template("order-success.html")

    @app.route("/orders")
    def orders_page():
        return render_template("orders.html")

    @app.route("/order/<int:oid>")
    def order_details_page(oid):
        return render_template("order-details.html", order_id=oid)

    @app.route("/profile")
    def profile_page():
        return render_template("profile.html")

    @app.route("/admin")
    def admin_dashboard_page():
        return render_template("admin-dashboard.html")

    @app.route("/admin/products")
    def admin_products_page():
        return render_template("admin-products.html")

    @app.route("/admin/orders")
    def admin_orders_page():
        return render_template("admin-orders.html")

    @app.route("/admin/users")
    def admin_users_page():
        return render_template("admin-users.html")

    return app