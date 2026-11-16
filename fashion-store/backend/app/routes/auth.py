from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required

from app import db, limiter
from app.auth import login_required
from app.config import Config
from app.models import User
from app.utils import require_fields, validate_email

bp = Blueprint("auth", __name__)


@bp.post("/register")
@limiter.limit(Config.RATELIMIT_AUTH)
def register():
    data = request.get_json(silent=True) or {}
    err = require_fields(data, ["email", "password", "full_name"])
    if err:
        return err
    try:
        email = validate_email(data["email"])
    except ValueError as exc:
        return jsonify({"error": "invalid_email", "message": str(exc)}), 400
    if len(data["password"]) < 8:
        return jsonify({"error": "weak_password"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email_taken"}), 409

    user = User(email=email, full_name=data["full_name"].strip(), phone=data.get("phone"), role="customer")
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    refresh = create_refresh_token(identity=str(user.id))
    return jsonify({"user": user.to_dict(), "access_token": token, "refresh_token": refresh}), 201


@bp.post("/login")
@limiter.limit(Config.RATELIMIT_AUTH)
def login():
    data = request.get_json(silent=True) or {}
    err = require_fields(data, ["email", "password"])
    if err:
        return err
    try:
        email = validate_email(data["email"])
    except ValueError:
        return jsonify({"error": "invalid_credentials"}), 401
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(data["password"]) or not user.is_active:
        return jsonify({"error": "invalid_credentials"}), 401
    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    refresh = create_refresh_token(identity=str(user.id))
    return jsonify({"user": user.to_dict(), "access_token": token, "refresh_token": refresh})


@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    user = User.query.get(int(identity))
    if not user or not user.is_active:
        return jsonify({"error": "unauthorized"}), 401
    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify({"access_token": token})


@bp.get("/me")
@login_required
def me(user: User):
    return jsonify({"user": user.to_dict()})
