from datetime import datetime, timezone
from decimal import Decimal

from app import db

ORDER_STATUSES = (
    "pending_payment",
    "paid",
    "processing",
    "shipped",
    "delivered",
    "cancelled",
    "refunded",
)

PAYMENT_STATUSES = ("pending", "waiting_for_capture", "succeeded", "canceled", "refunded")


class Cart(db.Model):
    __tablename__ = "carts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", back_populates="cart")
    items = db.relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        lines = [i.to_dict() for i in self.items]
        subtotal = sum(Decimal(str(i["line_total_rub"])) for i in lines)
        return {
            "id": self.id,
            "items": lines,
            "items_count": sum(i["quantity"] for i in lines),
            "subtotal_rub": float(subtotal),
            "currency": "RUB",
        }


class CartItem(db.Model):
    __tablename__ = "cart_items"
    __table_args__ = (db.UniqueConstraint("cart_id", "variant_id", name="uq_cart_variant"),)

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id"), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey("product_variants.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    cart = db.relationship("Cart", back_populates="items")
    variant = db.relationship("ProductVariant")

    def to_dict(self) -> dict:
        price = self.variant.effective_price() if self.variant else 0
        product = self.variant.product if self.variant else None
        return {
            "id": self.id,
            "variant_id": self.variant_id,
            "quantity": self.quantity,
            "unit_price_rub": price,
            "line_total_rub": float(Decimal(str(price)) * self.quantity),
            "variant": self.variant.to_dict() if self.variant else None,
            "product": {
                "id": product.id,
                "slug": product.slug,
                "name": product.name,
                "brand": product.brand,
                "images": product.images or [],
            }
            if product
            else None,
        }


class Favorite(db.Model):
    __tablename__ = "favorites"
    __table_args__ = (db.UniqueConstraint("user_id", "product_id", name="uq_fav_user_product"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="favorites")
    product = db.relationship("Product")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product": self.product.to_dict() if self.product else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Coupon(db.Model):
    __tablename__ = "coupons"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=True)
    discount_percent = db.Column(db.Integer, nullable=True)
    discount_amount_rub = db.Column(db.Numeric(12, 2), nullable=True)
    min_order_rub = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    is_active = db.Column(db.Boolean, default=True)
    valid_until = db.Column(db.DateTime, nullable=True)
    usage_limit = db.Column(db.Integer, nullable=True)
    used_count = db.Column(db.Integer, default=0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "code": self.code,
            "description": self.description,
            "discount_percent": self.discount_percent,
            "discount_amount_rub": float(self.discount_amount_rub)
            if self.discount_amount_rub is not None
            else None,
            "min_order_rub": float(self.min_order_rub or 0),
            "is_active": self.is_active,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
        }


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    status = db.Column(db.String(32), nullable=False, default="pending_payment")
    currency = db.Column(db.String(3), nullable=False, default="RUB")
    subtotal_rub = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    discount_rub = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    shipping_rub = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    total_rub = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    coupon_code = db.Column(db.String(64), nullable=True)
    shipping_name = db.Column(db.String(255), nullable=False)
    shipping_phone = db.Column(db.String(32), nullable=False)
    shipping_city = db.Column(db.String(120), nullable=False)
    shipping_address = db.Column(db.String(512), nullable=False)
    shipping_postal = db.Column(db.String(16), nullable=True)
    # courier | wb_pvz
    delivery_type = db.Column(db.String(32), nullable=False, default="courier")
    pvz_id = db.Column(db.String(64), nullable=True)
    pvz_meta = db.Column(db.JSON, nullable=True)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    paid_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = db.relationship("Payment", back_populates="order", cascade="all, delete-orphan")

    def to_dict(self, include_payments: bool = False) -> dict:
        data = {
            "id": self.id,
            "public_id": self.public_id,
            "user_id": self.user_id,
            "status": self.status,
            "currency": self.currency,
            "subtotal_rub": float(self.subtotal_rub),
            "discount_rub": float(self.discount_rub),
            "shipping_rub": float(self.shipping_rub),
            "total_rub": float(self.total_rub),
            "coupon_code": self.coupon_code,
            "shipping": {
                "name": self.shipping_name,
                "phone": self.shipping_phone,
                "city": self.shipping_city,
                "address": self.shipping_address,
                "postal": self.shipping_postal,
            },
            "delivery_type": self.delivery_type or "courier",
            "pvz_id": self.pvz_id,
            "pvz_meta": self.pvz_meta,
            "comment": self.comment,
            "items": [i.to_dict() for i in self.items],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
        }
        if include_payments:
            data["payments"] = [p.to_dict() for p in self.payments]
        return data


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey("product_variants.id"), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(120), nullable=False)
    size = db.Column(db.String(32), nullable=False)
    color = db.Column(db.String(64), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price_rub = db.Column(db.Numeric(12, 2), nullable=False)
    line_total_rub = db.Column(db.Numeric(12, 2), nullable=False)

    order = db.relationship("Order", back_populates="items")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "product_id": self.product_id,
            "variant_id": self.variant_id,
            "product_name": self.product_name,
            "sku": self.sku,
            "size": self.size,
            "color": self.color,
            "quantity": self.quantity,
            "unit_price_rub": float(self.unit_price_rub),
            "line_total_rub": float(self.line_total_rub),
        }


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True)
    provider = db.Column(db.String(32), nullable=False, default="yookassa")  # yookassa | mock
    provider_payment_id = db.Column(db.String(128), unique=True, nullable=True, index=True)
    idempotency_key = db.Column(db.String(128), unique=True, nullable=False)
    status = db.Column(db.String(32), nullable=False, default="pending")
    amount_rub = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="RUB")
    confirmation_url = db.Column(db.String(1024), nullable=True)
    qr_url = db.Column(db.String(1024), nullable=True)
    raw_response = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    order = db.relationship("Order", back_populates="payments")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "order_id": self.order_id,
            "provider": self.provider,
            "provider_payment_id": self.provider_payment_id,
            "status": self.status,
            "amount_rub": float(self.amount_rub),
            "currency": self.currency,
            "confirmation_url": self.confirmation_url,
            "qr_url": self.qr_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
