from flask import Blueprint, jsonify, request

from app import db
from app.auth import login_required
from app.models import Favorite, Product, User
from app.utils import require_fields

bp = Blueprint("favorites", __name__)


@bp.get("")
@login_required
def list_favorites(user: User):
    favs = Favorite.query.filter_by(user_id=user.id).order_by(Favorite.created_at.desc()).all()
    return jsonify({"items": [f.to_dict() for f in favs]})


@bp.post("")
@login_required
def add_favorite(user: User):
    data = request.get_json(silent=True) or {}
    err = require_fields(data, ["product_id"])
    if err:
        return err
    product = Product.query.get_or_404(int(data["product_id"]))
    existing = Favorite.query.filter_by(user_id=user.id, product_id=product.id).first()
    if existing:
        return jsonify({"favorite": existing.to_dict()})
    fav = Favorite(user_id=user.id, product_id=product.id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({"favorite": fav.to_dict()}), 201


@bp.delete("/<int:product_id>")
@login_required
def remove_favorite(user: User, product_id: int):
    fav = Favorite.query.filter_by(user_id=user.id, product_id=product_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
    return jsonify({"ok": True})
