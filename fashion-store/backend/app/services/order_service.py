from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from flask import abort

from app import db
from app.models import Coupon, Order, OrderItem, Payment, ProductVariant
from app.payments import YooKassaService
from app.services.cart_service import CartService


class OrderService:
    @staticmethod
    def apply_coupon(subtotal: Decimal, code: str | None) -> tuple[Decimal, str | None]:
        if not code:
            return Decimal("0"), None
        coupon = Coupon.query.filter_by(code=code.upper().strip(), is_active=True).first()
        if not coupon:
            abort(400, description="invalid_coupon")
        if coupon.valid_until and coupon.valid_until.replace(tzinfo=timezone.utc) < datetime.now(
            timezone.utc
        ):
            abort(400, description="coupon_expired")
        if coupon.usage_limit is not None and coupon.used_count >= coupon.usage_limit:
            abort(400, description="coupon_exhausted")
        if subtotal < Decimal(str(coupon.min_order_rub or 0)):
            abort(400, description="coupon_min_order")
        if coupon.discount_percent:
            discount = (subtotal * Decimal(coupon.discount_percent) / Decimal(100)).quantize(
                Decimal("0.01")
            )
        elif coupon.discount_amount_rub is not None:
            discount = Decimal(str(coupon.discount_amount_rub))
        else:
            discount = Decimal("0")
        return min(discount, subtotal), coupon.code

    @staticmethod
    def create_from_cart(user, payload: dict) -> Order:
        cart = CartService.get_or_create(user.id)
        if not cart.items:
            abort(400, description="cart_empty")

        for item in cart.items:
            if not item.variant or item.variant.stock < item.quantity:
                abort(400, description=f"insufficient_stock:{item.variant_id}")

        subtotal = Decimal("0")
        lines: list[OrderItem] = []
        for item in cart.items:
            unit = Decimal(str(item.variant.effective_price()))
            line_total = unit * item.quantity
            subtotal += line_total
            lines.append(
                OrderItem(
                    product_id=item.variant.product_id,
                    variant_id=item.variant.id,
                    product_name=item.variant.product.name,
                    sku=item.variant.sku,
                    size=item.variant.size,
                    color=item.variant.color,
                    quantity=item.quantity,
                    unit_price_rub=unit,
                    line_total_rub=line_total,
                )
            )

        discount, coupon_code = OrderService.apply_coupon(subtotal, payload.get("coupon_code"))
        shipping = Decimal(str(payload.get("shipping_rub", 0) or 0))
        total = subtotal - discount + shipping

        order = Order(
            public_id=str(uuid.uuid4()),
            user_id=user.id,
            status="pending_payment",
            subtotal_rub=subtotal,
            discount_rub=discount,
            shipping_rub=shipping,
            total_rub=total,
            coupon_code=coupon_code,
            shipping_name=payload["shipping_name"],
            shipping_phone=payload["shipping_phone"],
            shipping_city=payload["shipping_city"],
            shipping_address=payload["shipping_address"],
            shipping_postal=payload.get("shipping_postal"),
            comment=payload.get("comment"),
        )
        db.session.add(order)
        db.session.flush()
        for line in lines:
            line.order_id = order.id
            db.session.add(line)

        # Reserve stock (FOR UPDATE when DB supports it; SQLite falls back)
        for item in cart.items:
            q = ProductVariant.query.filter_by(id=item.variant_id)
            try:
                variant = q.with_for_update().first()
            except Exception:
                variant = q.first()
            if not variant or variant.stock < item.quantity:
                abort(400, description="insufficient_stock")
            variant.stock -= item.quantity

        if coupon_code:
            coupon = Coupon.query.filter_by(code=coupon_code).first()
            if coupon:
                coupon.used_count = (coupon.used_count or 0) + 1

        CartService.clear(user.id)
        db.session.commit()
        return order

    @staticmethod
    def create_payment(order: Order, user_email: str | None = None) -> Payment:
        existing = (
            Payment.query.filter_by(order_id=order.id)
            .filter(Payment.status.in_(["pending", "waiting_for_capture", "succeeded"]))
            .order_by(Payment.id.desc())
            .first()
        )
        if existing and existing.status == "succeeded":
            return existing
        if existing and existing.status in ("pending", "waiting_for_capture"):
            return existing

        idempotency_key = f"order-{order.public_id}-{uuid.uuid4().hex[:8]}"
        yk = YooKassaService()
        result = yk.create_sbp_payment(
            amount_rub=order.total_rub,
            description=f"Заказ {order.public_id[:8]}",
            order_public_id=order.public_id,
            idempotency_key=idempotency_key,
            customer_email=user_email,
        )
        payment = Payment(
            order_id=order.id,
            provider=result["provider"],
            provider_payment_id=result["provider_payment_id"],
            idempotency_key=idempotency_key,
            status=result["status"],
            amount_rub=order.total_rub,
            confirmation_url=result.get("confirmation_url"),
            qr_url=result.get("qr_url"),
            raw_response=result.get("raw"),
        )
        db.session.add(payment)
        db.session.commit()
        return payment

    @staticmethod
    def mark_paid(order: Order, payment: Payment) -> Order:
        if order.status in ("paid", "processing", "shipped", "delivered"):
            return order
        payment.status = "succeeded"
        order.status = "paid"
        order.paid_at = datetime.now(timezone.utc)
        db.session.commit()
        return order

    @staticmethod
    def handle_webhook_event(event: dict) -> Payment | None:
        obj = event.get("object") or {}
        provider_payment_id = obj.get("id")
        status = obj.get("status")
        metadata = obj.get("metadata") or {}
        if not provider_payment_id:
            return None

        payment = Payment.query.filter_by(provider_payment_id=provider_payment_id).first()
        if not payment:
            # Idempotent no-op for unknown payments
            return None

        # Idempotency: ignore duplicate succeeded events
        if payment.status == "succeeded" and status == "succeeded":
            return payment

        payment.status = status or payment.status
        payment.raw_response = event
        if status == "succeeded":
            OrderService.mark_paid(payment.order, payment)
        elif status in ("canceled", "cancelled"):
            order = payment.order
            if order.status == "pending_payment":
                order.status = "cancelled"
                # Restore stock
                for item in order.items:
                    variant = ProductVariant.query.get(item.variant_id)
                    if variant:
                        variant.stock += item.quantity
            db.session.commit()
        else:
            db.session.commit()

        # Prefer metadata order id match when present
        order_public_id = metadata.get("order_public_id")
        if order_public_id and payment.order.public_id != order_public_id:
            # Do not mutate mismatched orders
            pass
        return payment
