from flask import Blueprint, jsonify, request

from app import db
from app.auth import admin_required
from app.models import ORDER_STATUSES, Order, Product, ProductVariant, User
from app.utils import require_fields

bp = Blueprint("admin", __name__)


@bp.get("/dashboard")
@admin_required
def dashboard(user: User):
    return jsonify(
        {
            "users": User.query.count(),
            "products": Product.query.count(),
            "orders": Order.query.count(),
            "revenue_paid_rub": float(
                sum(
                    float(o.total_rub)
                    for o in Order.query.filter(Order.status.in_(["paid", "processing", "shipped", "delivered"])).all()
                )
            ),
            "orders_by_status": {
                s: Order.query.filter_by(status=s).count() for s in ORDER_STATUSES
            },
        }
    )


@bp.get("/orders")
@admin_required
def admin_orders(user: User):
    status = request.args.get("status")
    q = Order.query.order_by(Order.created_at.desc())
    if status:
        q = q.filter_by(status=status)
    orders = q.limit(200).all()
    return jsonify({"items": [o.to_dict(include_payments=True) for o in orders]})


@bp.patch("/orders/<public_id>")
@admin_required
def update_order(user: User, public_id: str):
    order = Order.query.filter_by(public_id=public_id).first_or_404()
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if status:
        if status not in ORDER_STATUSES:
            return jsonify({"error": "invalid_status", "allowed": list(ORDER_STATUSES)}), 400
        order.status = status
        db.session.commit()
    return jsonify({"order": order.to_dict(include_payments=True)})


@bp.get("/products")
@admin_required
def admin_products(user: User):
    products = Product.query.order_by(Product.id.desc()).all()
    return jsonify({"items": [p.to_dict() for p in products]})


@bp.post("/products")
@admin_required
def create_product(user: User):
    data = request.get_json(silent=True) or {}
    err = require_fields(data, ["slug", "name", "base_price_rub"])
    if err:
        return err
    if Product.query.filter_by(slug=data["slug"]).first():
        return jsonify({"error": "slug_taken"}), 409
    product = Product(
        slug=data["slug"],
        name=data["name"],
        brand=data.get("brand", "ATELIER"),
        description=data.get("description"),
        category_id=data.get("category_id"),
        base_price_rub=data["base_price_rub"],
        compare_at_price_rub=data.get("compare_at_price_rub"),
        images=data.get("images") or [],
        tags=data.get("tags") or [],
        is_published=bool(data.get("is_published", True)),
        is_featured=bool(data.get("is_featured", False)),
    )
    db.session.add(product)
    db.session.flush()
    for v in data.get("variants") or []:
        variant = ProductVariant(
            product_id=product.id,
            sku=v["sku"],
            size=v.get("size", "ONE"),
            color=v.get("color", "Default"),
            color_hex=v.get("color_hex"),
            stock=int(v.get("stock", 0)),
            price_rub=v.get("price_rub"),
        )
        db.session.add(variant)
    db.session.commit()
    return jsonify({"product": product.to_dict()}), 201


@bp.patch("/products/<int:product_id>")
@admin_required
def update_product(user: User, product_id: int):
    product = Product.query.get_or_404(product_id)
    data = request.get_json(silent=True) or {}
    for field in (
        "name",
        "brand",
        "description",
        "composition",
        "care",
        "category_id",
        "base_price_rub",
        "compare_at_price_rub",
        "images",
        "tags",
        "is_published",
        "is_featured",
    ):
        if field in data:
            setattr(product, field, data[field])
    db.session.commit()
    return jsonify({"product": product.to_dict()})


@bp.patch("/variants/<int:variant_id>/stock")
@admin_required
def update_stock(user: User, variant_id: int):
    variant = ProductVariant.query.get_or_404(variant_id)
    data = request.get_json(silent=True) or {}
    err = require_fields(data, ["stock"])
    if err:
        return err
    stock = int(data["stock"])
    if stock < 0:
        return jsonify({"error": "invalid_stock"}), 400
    variant.stock = stock
    db.session.commit()
    return jsonify({"variant": variant.to_dict()})


@bp.get("/users")
@admin_required
def admin_users(user: User):
    users = User.query.order_by(User.id.desc()).limit(200).all()
    return jsonify({"items": [u.to_dict() for u in users]})
