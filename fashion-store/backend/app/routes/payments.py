from flask import Blueprint, jsonify, request

from app.auth import login_required
from app.models import Order, Payment, User
from app.payments import YooKassaService
from app.services import OrderService

bp = Blueprint("payments", __name__)


@bp.post("/create")
@login_required
def create_payment(user: User):
    data = request.get_json(silent=True) or {}
    public_id = data.get("order_public_id") or data.get("order_id")
    if not public_id:
        return jsonify({"error": "validation_error", "missing": ["order_public_id"]}), 400
    order = Order.query.filter_by(public_id=public_id, user_id=user.id).first_or_404()
    if order.status != "pending_payment":
        return jsonify({"error": "order_not_payable"}), 400
    payment = OrderService.create_payment(order, user_email=user.email)
    return jsonify({"payment": payment.to_dict(), "order": order.to_dict()}), 201


@bp.get("/<provider_payment_id>/status")
@login_required
def payment_status(user: User, provider_payment_id: str):
    payment = Payment.query.filter_by(provider_payment_id=provider_payment_id).first_or_404()
    if payment.order.user_id != user.id and user.role != "admin":
        return jsonify({"error": "forbidden"}), 403

    # Never trust frontend: refresh from provider when real keys present
    yk = YooKassaService()
    remote = yk.get_payment_status(provider_payment_id)
    remote_status = remote.get("status")
    if remote_status == "succeeded" and payment.status != "succeeded":
        OrderService.mark_paid(payment.order, payment)
    elif remote_status and remote_status != payment.status and remote.get("provider") != "mock":
        payment.status = remote_status
        from app import db

        db.session.commit()

    return jsonify({"payment": payment.to_dict(), "order_status": payment.order.status})


@bp.post("/webhook")
def webhook():
    raw = request.get_data()
    yk = YooKassaService()
    if not yk.verify_webhook(dict(request.headers), raw):
        return jsonify({"error": "invalid_signature"}), 401
    try:
        event = request.get_json(force=True, silent=False)
    except Exception:
        return jsonify({"error": "invalid_json"}), 400

    payment = OrderService.handle_webhook_event(event or {})
    return jsonify({"ok": True, "payment_id": payment.provider_payment_id if payment else None})


@bp.post("/mock/confirm")
@login_required
def mock_confirm(user: User):
    """Dev-only: mark a mock SBP payment as paid (keys missing)."""
    data = request.get_json(silent=True) or {}
    provider_payment_id = data.get("provider_payment_id")
    if not provider_payment_id or not str(provider_payment_id).startswith("mock_"):
        return jsonify({"error": "only_mock_payments"}), 400
    payment = Payment.query.filter_by(provider_payment_id=provider_payment_id).first_or_404()
    if payment.order.user_id != user.id and user.role != "admin":
        return jsonify({"error": "forbidden"}), 403
    OrderService.mark_paid(payment.order, payment)
    return jsonify({"payment": payment.to_dict(), "order": payment.order.to_dict()})
