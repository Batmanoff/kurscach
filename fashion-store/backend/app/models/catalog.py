from datetime import datetime, timezone

from app import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    sort_order = db.Column(db.Integer, default=0)

    parent = db.relationship("Category", remote_side=[id], backref="children")
    products = db.relationship("Product", back_populates="category")

    def to_dict(self, with_children: bool = False) -> dict:
        data = {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "description": self.description,
            "parent_id": self.parent_id,
            "sort_order": self.sort_order,
        }
        if with_children:
            data["children"] = [c.to_dict() for c in sorted(self.children, key=lambda x: x.sort_order)]
        return data


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(180), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(120), nullable=False, default="BAST")
    description = db.Column(db.Text, nullable=True)
    composition = db.Column(db.String(255), nullable=True)
    care = db.Column(db.String(255), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    base_price_rub = db.Column(db.Numeric(12, 2), nullable=False)
    compare_at_price_rub = db.Column(db.Numeric(12, 2), nullable=True)
    currency = db.Column(db.String(3), nullable=False, default="RUB")
    images = db.Column(db.JSON, nullable=False, default=list)
    tags = db.Column(db.JSON, nullable=False, default=list)
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    supplier_sku = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    category = db.relationship("Category", back_populates="products")
    variants = db.relationship(
        "ProductVariant", back_populates="product", cascade="all, delete-orphan", lazy="joined"
    )

    def _images_payload(self) -> dict:
        raw = self.images or []
        if isinstance(raw, dict):
            return {
                "gallery": list(raw.get("gallery") or []),
                "by_color": dict(raw.get("by_color") or {}),
            }
        if isinstance(raw, list):
            gallery = []
            by_color: dict = {}
            for item in raw:
                if isinstance(item, str):
                    gallery.append(item)
                elif isinstance(item, dict) and item.get("url"):
                    gallery.append(item["url"])
                    if item.get("color"):
                        by_color[item["color"]] = item["url"]
            return {"gallery": gallery, "by_color": by_color}
        return {"gallery": [], "by_color": {}}

    def primary_image(self, color: str | None = None) -> str | None:
        payload = self._images_payload()
        if color and color in payload["by_color"]:
            return payload["by_color"][color]
        if payload["gallery"]:
            return payload["gallery"][0]
        if payload["by_color"]:
            return next(iter(payload["by_color"].values()))
        return None

    def color_swatches(self) -> list[dict]:
        """Unique colors with hex + photo for UI swatches."""
        payload = self._images_payload()
        seen: dict[str, dict] = {}
        for v in self.variants:
            if v.color in seen:
                continue
            seen[v.color] = {
                "name": v.color,
                "hex": v.color_hex or "#888888",
                "image": payload["by_color"].get(v.color) or self.primary_image(v.color),
            }
        return list(seen.values())

    def to_dict(self, include_variants: bool = True) -> dict:
        data = {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "brand": self.brand,
            "description": self.description,
            "composition": self.composition,
            "care": self.care,
            "category_id": self.category_id,
            "category": self.category.to_dict() if self.category else None,
            "base_price_rub": float(self.base_price_rub),
            "compare_at_price_rub": float(self.compare_at_price_rub)
            if self.compare_at_price_rub is not None
            else None,
            "currency": self.currency,
            "images": self.images or [],
            "primary_image": self.primary_image(),
            "color_swatches": self.color_swatches(),
            "tags": self.tags or [],
            "is_published": self.is_published,
            "is_featured": self.is_featured,
            "supplier_sku": self.supplier_sku,
        }
        if include_variants:
            data["variants"] = [v.to_dict() for v in self.variants]
            data["in_stock"] = any(v.stock > 0 for v in self.variants)
        return data


class ProductVariant(db.Model):
    __tablename__ = "product_variants"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    sku = db.Column(db.String(120), unique=True, nullable=False)
    size = db.Column(db.String(32), nullable=False)
    color = db.Column(db.String(64), nullable=False, default="Default")
    color_hex = db.Column(db.String(16), nullable=True)
    stock = db.Column(db.Integer, nullable=False, default=0)
    price_rub = db.Column(db.Numeric(12, 2), nullable=True)

    product = db.relationship("Product", back_populates="variants")

    def effective_price(self) -> float:
        if self.price_rub is not None:
            return float(self.price_rub)
        return float(self.product.base_price_rub)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "product_id": self.product_id,
            "sku": self.sku,
            "size": self.size,
            "color": self.color,
            "color_hex": self.color_hex,
            "stock": self.stock,
            "price_rub": self.effective_price(),
            "in_stock": self.stock > 0,
        }
