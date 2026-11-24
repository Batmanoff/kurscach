from datetime import timedelta
from urllib.parse import quote

from flask import Flask, jsonify, redirect, request, url_for
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per hour"],
    storage_uri="memory://",
)


def create_app(config_object: type[Config] | None = None) -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")
    cfg = config_object or Config
    app.config.from_object(cfg)
    app.config.setdefault("STORE_NAME", "ATELIER")
    app.config.setdefault("PERMANENT_SESSION_LIFETIME", timedelta(days=14))

    storage_uri = getattr(cfg, "RATELIMIT_STORAGE_URI", None) or "memory://"
    if not str(storage_uri).startswith(("memory://", "redis://", "rediss://")):
        storage_uri = "memory://"
    app.config["RATELIMIT_STORAGE_URI"] = storage_uri

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}}, supports_credentials=True)
    limiter.init_app(app)
    try:
        limiter._storage_uri = storage_uri
        from limits import parse_storage_uri as _parse

        limiter._storage = _parse(storage_uri)
    except Exception:
        limiter._storage_uri = "memory://"

    app.jinja_env.filters["urlencode"] = lambda u: quote(str(u), safe="")

    from app import models  # noqa: F401
    from app.routes import register_blueprints

    register_blueprints(app)

    @app.get("/api/health")
    def health():
        return jsonify(
            {
                "status": "ok",
                "payments": "yookassa" if Config().yookassa_enabled else "mock",
                "currency": "RUB",
                "ui": "flask-jinja",
            }
        )

    def _wants_json() -> bool:
        return request.path.startswith("/api/") or "application/json" in (
            request.accept_mimetypes.best or ""
        )

    @app.errorhandler(400)
    def bad_request(err):
        if _wants_json():
            return jsonify({"error": getattr(err, "description", "bad_request")}), 400
        return redirect(request.referrer or url_for("web.home"))

    @app.errorhandler(401)
    def unauthorized(err):
        if _wants_json():
            return jsonify({"error": "unauthorized"}), 401
        return redirect(url_for("web.login"))

    @app.errorhandler(403)
    def forbidden(err):
        if _wants_json():
            return jsonify({"error": "forbidden"}), 403
        return redirect(url_for("web.home"))

    @app.errorhandler(404)
    def not_found(err):
        if _wants_json():
            return jsonify({"error": "not_found"}), 404
        return (
            "<!doctype html><html><body style='font-family:sans-serif;padding:3rem'>"
            "<h1>404</h1><p>Страница не найдена. <a href='/'>На главную</a></p></body></html>",
            404,
        )

    @app.errorhandler(429)
    def rate_limited(err):
        if _wants_json():
            return jsonify({"error": "rate_limited", "message": str(err.description)}), 429
        return "Слишком много запросов. Подождите минуту.", 429

    @app.errorhandler(500)
    def server_error(err):
        if _wants_json():
            return jsonify({"error": "server_error"}), 500
        return "Ошибка сервера", 500

    return app
