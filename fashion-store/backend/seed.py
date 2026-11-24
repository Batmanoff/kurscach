"""Seed catalog, admin/customer users, and coupons. Upserts sportswear by SKU."""

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
            demo = User(
                email=cfg.DEMO_EMAIL,
                full_name="Demo Customer",
                role="customer",
                phone="+79001234567",
            )
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
            else:
                cat.name = c["name"]
                cat.description = c["description"]
                cat.sort_order = c["sort_order"]
            category_map[c["slug"]] = cat

        keep_skus: set[str] = set()
        for item in supplier.fetch_catalog():
            keep_skus.add(item.sku)
            images_payload = {
                "gallery": list(item.images),
                "by_color": {c.name: c.image for c in item.colors},
            }
            product = Product.query.filter_by(supplier_sku=item.sku).first()
            if not product:
                product = Product(
                    supplier_sku=item.sku,
                    slug=slugify(f"{item.brand}-{item.name}-{item.sku}"),
                    name=item.name,
                    brand=item.brand,
                    description=item.description,
                    composition=item.composition,
                    care="Стирка 30°C, не отбеливать",
                    category_id=category_map[item.category_slug].id,
                    base_price_rub=item.price_rub,
                    compare_at_price_rub=item.compare_at,
                    images=images_payload,
                    tags=item.tags,
                    is_featured=item.featured,
                    is_published=True,
                )
                db.session.add(product)
                db.session.flush()
            else:
                product.slug = slugify(f"{item.brand}-{item.name}-{item.sku}")
                product.name = item.name
                product.brand = item.brand
                product.description = item.description
                product.composition = item.composition
                product.care = "Стирка 30°C, не отбеливать"
                product.category_id = category_map[item.category_slug].id
                product.base_price_rub = item.price_rub
                product.compare_at_price_rub = item.compare_at
                product.images = images_payload
                product.tags = item.tags
                product.is_featured = item.featured
                product.is_published = True

            ProductVariant.query.filter_by(product_id=product.id).delete()
            for color in item.colors:
                for size in item.sizes:
                    sku = f"{item.sku}-{color.name[:3].upper()}-{size}"
                    db.session.add(
                        ProductVariant(
                            product_id=product.id,
                            sku=sku,
                            size=size,
                            color=color.name,
                            color_hex=color.hex,
                            stock=12,
                        )
                    )

        for old in Product.query.all():
            if not old.supplier_sku or old.supplier_sku not in keep_skus:
                db.session.delete(old)

        coupon = Coupon.query.filter_by(code="WELCOME10").first()
        if not coupon:
            db.session.add(
                Coupon(
                    code="WELCOME10",
                    description="Скидка 10% на заказ",
                    discount_percent=10,
                    min_order_rub=0,
                    is_active=True,
                )
            )
        else:
            coupon.min_order_rub = 0
            coupon.is_active = True
            coupon.description = "Скидка 10% на заказ"

        db.session.commit()
        print("Seed complete.")
        print(f"Admin: {cfg.ADMIN_EMAIL} / {cfg.ADMIN_PASSWORD}")
        print(f"Customer: {cfg.DEMO_EMAIL} / {cfg.DEMO_PASSWORD}")
        print(f"Products: {Product.query.count()}")


if __name__ == "__main__":
    seed()
