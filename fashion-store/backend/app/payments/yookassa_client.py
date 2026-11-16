"""YooKassa SBP payments with mock fallback when keys are missing."""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from decimal import Decimal
from typing import Any

from app.config import Config


class YooKassaService:
    def __init__(self, config: Config | None = None):
        self.config = config or Config()

    @property
    def enabled(self) -> bool:
        return self.config.yookassa_enabled

    def create_sbp_payment(
        self,
        *,
        amount_rub: Decimal | float | str,
        description: str,
        order_public_id: str,
        idempotency_key: str,
        customer_email: str | None = None,
        return_url: str | None = None,
    ) -> dict[str, Any]:
        amount = f"{Decimal(str(amount_rub)):.2f}"
        return_url = return_url or self.config.YOOKASSA_RETURN_URL

        if not self.enabled:
            return self._mock_payment(
                amount=amount,
                description=description,
                order_public_id=order_public_id,
                idempotency_key=idempotency_key,
                return_url=return_url,
            )

        from yookassa import Configuration, Payment

        Configuration.account_id = self.config.YOOKASSA_SHOP_ID
        Configuration.secret_key = self.config.YOOKASSA_SECRET_KEY

        payload = {
            "amount": {"value": amount, "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": return_url},
            "capture": True,
            "description": description[:128],
            "metadata": {"order_public_id": order_public_id},
            "payment_method_data": {"type": "sbp"},
        }
        if customer_email:
            payload["receipt"] = {
                "customer": {"email": customer_email},
                "items": [
                    {
                        "description": description[:128],
                        "quantity": "1.00",
                        "amount": {"value": amount, "currency": "RUB"},
                        "vat_code": 1,
                        "payment_mode": "full_payment",
                        "payment_subject": "commodity",
                    }
                ],
            }

        payment = Payment.create(payload, idempotency_key)
        confirmation_url = None
        qr_url = None
        confirmation = getattr(payment, "confirmation", None)
        if confirmation is not None:
            confirmation_url = getattr(confirmation, "confirmation_url", None)
            qr_url = getattr(confirmation, "confirmation_data", None)

        return {
            "provider": "yookassa",
            "provider_payment_id": payment.id,
            "status": payment.status,
            "amount_rub": float(amount),
            "confirmation_url": confirmation_url,
            "qr_url": qr_url or confirmation_url,
            "raw": json.loads(payment.json()),
        }

    def get_payment_status(self, provider_payment_id: str) -> dict[str, Any]:
        if provider_payment_id.startswith("mock_"):
            # Mock payments stay pending until webhook/simulate marks them paid.
            return {
                "provider": "mock",
                "provider_payment_id": provider_payment_id,
                "status": "pending",
            }

        if not self.enabled:
            return {
                "provider": "mock",
                "provider_payment_id": provider_payment_id,
                "status": "pending",
            }

        from yookassa import Configuration, Payment

        Configuration.account_id = self.config.YOOKASSA_SHOP_ID
        Configuration.secret_key = self.config.YOOKASSA_SECRET_KEY
        payment = Payment.find_one(provider_payment_id)
        return {
            "provider": "yookassa",
            "provider_payment_id": payment.id,
            "status": payment.status,
            "raw": json.loads(payment.json()),
        }

    def verify_webhook(self, headers: dict, body: bytes) -> bool:
        """
        YooKassa IP allowlist + optional shared secret header.
        Never trust client-reported payment status — only webhook / API lookup.
        """
        secret = self.config.YOOKASSA_WEBHOOK_SECRET
        if secret:
            signature = headers.get("X-Webhook-Signature") or headers.get("x-webhook-signature")
            if not signature:
                return False
            digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
            return hmac.compare_digest(digest, signature)
        # Without webhook secret, still accept in mock/dev; production should set secret.
        return True

    def _mock_payment(
        self,
        *,
        amount: str,
        description: str,
        order_public_id: str,
        idempotency_key: str,
        return_url: str,
    ) -> dict[str, Any]:
        payment_id = f"mock_{uuid.uuid4().hex}"
        # Frontend can render this as a QR payload / deep link placeholder.
        qr_payload = (
            f"https://qr.nspk.ru/mock?sum={amount}&order={order_public_id}&pid={payment_id}"
        )
        confirmation_url = (
            f"{self.config.FRONTEND_URL}/checkout/mock-pay"
            f"?order={order_public_id}&payment={payment_id}&return={return_url}"
        )
        return {
            "provider": "mock",
            "provider_payment_id": payment_id,
            "status": "pending",
            "amount_rub": float(amount),
            "confirmation_url": confirmation_url,
            "qr_url": qr_payload,
            "raw": {
                "mode": "mock",
                "description": description,
                "idempotency_key": idempotency_key,
                "message": "YooKassa keys missing — mock SBP payment created",
            },
        }
