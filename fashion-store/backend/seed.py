"""Seed demo catalog, admin/demo users, and coupons."""

from __future__ import annotations

import re

from app import create_app, db
from app.config import Config
from app.models import Category, Coupon, Product, ProductVariant, User
from app.services.supplier import DemoSupplierAdapter


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9а-яё]+", "-", value, flags=re.IGNORECASE)
    return value.strip("-")[:160] or "item"


def seed() -> None:
    app = create_app()
    cfg = Config()
    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(email=cfg.ADMIN_EMAIL).first()
        if not admin:
            admin = User(email=cfg.ADMIN_EMAIL, full_name="Store Admin", role="admin")
            admin.set_password(cfg.ADMIN_PASSWORD)
            db.session.add(admin)

        demo = User.query.filter_by(email=cfg.DEMO_EMAIL).first()
        if not demo:
            demo = User(email=cfg.DEMO_EMAIL, full_name="Demo Customer", role="customer", phone="+79001234567")
            demo.set_password(cfg.DEMO_PASSWORD)
            db.session.add(demo)

        supplier = DemoSupplierAdapter()
        category_map: dict[str, Category] = {}
        for c in supplier.CATEGORIES:
            cat = Category.query.filter_by(slug=c["slug"]).first()
            if not cat:
                cat = Category(**c)
                db.session.add(cat)
                db.session.flush()
            category_map[c["slug"]] = cat

        if Product.query.count() == 0:
            for item in supplier.fetch_catalog():
                product = Product(
                    slug=slugify(f"{item.brand}-{item.name}-{item.sku}"),
                    name=item.name,
                    brand=item.brand,
                    description=item.description,
                    composition=item.composition,
                    care="Химчистка / бережная стирка",
                    category_id=category_map[item.category_slug].id,
                    base_price_rub=item.price_rub,
                    compare_at_price_rub=item.compare_at,
                    images=item.images,
                    tags=item.tags,
                    is_featured=item.featured,
                    supplier_sku=item.sku,
                )
                db.session.add(product)
                db.session.flush()
                for color_name, color_hex in item.colors:
                    for size in item.sizes:
                        sku = f"{item.sku}-{color_name[:3].upper()}-{size}"
                        db.session.add(
                            ProductVariant(
                                product_id=product.id,
                                sku=sku,
                                size=size,
                                color=color_name,
                                color_hex=color_hex,
                                stock=12,
                            )
                        )

        if not Coupon.query.filter_by(code="WELCOME10").first():
            db.session.add(
                Coupon(
                    code="WELCOME10",
                    description="Скидка 10% на первый заказ",
                    discount_percent=10,
                    min_order_rub=5000,
                    is_active=True,
                )
            )

        db.session.commit()
        print("Seed complete.")
        print(f"Admin: {cfg.ADMIN_EMAIL} / {cfg.ADMIN_PASSWORD}")
        print(f"Demo:  {cfg.DEMO_EMAIL} / {cfg.DEMO_PASSWORD}")
        print(f"Products: {Product.query.count()}")


if __name__ == "__main__":
    seed()
