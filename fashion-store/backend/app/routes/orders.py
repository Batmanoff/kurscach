from flask import Blueprint, jsonify, request

from app.auth import login_required
from app.models import Order, User
from app.services import OrderService
from app.utils import require_fields

bp = Blueprint("orders", __name__)


@bp.get("")
@login_required
def list_orders(user: User):
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return jsonify({"items": [o.to_dict(include_payments=True) for o in orders]})


@bp.post("")
@login_required
def create_order(user: User):
    data = request.get_json(silent=True) or {}
    err = require_fields(
        data, ["shipping_name", "shipping_phone", "shipping_city", "shipping_address"]
    )
    if err:
        return err
    order = OrderService.create_from_cart(user, data)
    return jsonify({"order": order.to_dict(include_payments=True)}), 201


@bp.get("/<public_id>")
@login_required
def get_order(user: User, public_id: str):
    order = Order.query.filter_by(public_id=public_id, user_id=user.id).first_or_404()
    return jsonify({"order": order.to_dict(include_payments=True)})


@bp.post("/<public_id>/pay")
@login_required
def pay_order(user: User, public_id: str):
    order = Order.query.filter_by(public_id=public_id, user_id=user.id).first_or_404()
    if order.status not in ("pending_payment",):
        return jsonify({"error": "order_not_payable", "status": order.status}), 400
    payment = OrderService.create_payment(order, user_email=user.email)
    return jsonify({"order": order.to_dict(include_payments=True), "payment": payment.to_dict()})
