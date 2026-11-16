from flask import Blueprint, jsonify, request

from app.auth import login_required
from app.models import User
from app.services import CartService
from app.utils import require_fields

bp = Blueprint("cart", __name__)


@bp.get("")
@login_required
def get_cart(user: User):
    cart = CartService.get_or_create(user.id)
    return jsonify({"cart": cart.to_dict()})


@bp.post("/items")
@login_required
def add_item(user: User):
    data = request.get_json(silent=True) or {}
    err = require_fields(data, ["variant_id"])
    if err:
        return err
    quantity = int(data.get("quantity", 1))
    cart = CartService.add_item(user.id, int(data["variant_id"]), quantity)
    return jsonify({"cart": cart.to_dict()}), 201


@bp.patch("/items/<int:item_id>")
@login_required
def update_item(user: User, item_id: int):
    data = request.get_json(silent=True) or {}
    err = require_fields(data, ["quantity"])
    if err:
        return err
    cart = CartService.update_item(user.id, item_id, int(data["quantity"]))
    return jsonify({"cart": cart.to_dict()})


@bp.delete("/items/<int:item_id>")
@login_required
def remove_item(user: User, item_id: int):
    cart = CartService.remove_item(user.id, item_id)
    return jsonify({"cart": cart.to_dict()})


@bp.delete("")
@login_required
def clear_cart(user: User):
    cart = CartService.clear(user.id)
    return jsonify({"cart": cart.to_dict()})
