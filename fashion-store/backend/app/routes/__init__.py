from flask import Flask

from app.routes.admin import bp as admin_bp
from app.routes.auth import bp as auth_bp
from app.routes.cart import bp as cart_bp
from app.routes.favorites import bp as favorites_bp
from app.routes.orders import bp as orders_bp
from app.routes.payments import bp as payments_bp
from app.routes.products import bp as products_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(products_bp, url_prefix="/api/products")
    app.register_blueprint(cart_bp, url_prefix="/api/cart")
    app.register_blueprint(favorites_bp, url_prefix="/api/favorites")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")
    app.register_blueprint(payments_bp, url_prefix="/api/payments")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
