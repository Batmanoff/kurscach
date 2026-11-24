import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# Load repo-root .env then local overrides (never commit secrets).
_root_env = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(_root_env)
load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///fashion_store.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # pool_pre_ping helps PostgreSQL; SQLite works fine without a special pool.
    SQLALCHEMY_ENGINE_OPTIONS = (
        {"pool_pre_ping": True}
        if not (os.getenv("DATABASE_URL") or "sqlite").startswith("sqlite")
        else {}
    )

    # Leave empty for in-memory rate limits (no Redis required on Windows/dev).
    REDIS_URL = (os.getenv("REDIS_URL") or "").strip()
    CORS_ORIGINS = [
        o.strip()
        for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if o.strip()
    ]

    BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:5000")
    # Same origin as Flask Jinja UI by default (Next.js is optional).
    FRONTEND_URL = os.getenv("FRONTEND_URL", BACKEND_URL)
    STORE_NAME = os.getenv("STORE_NAME", "BAST")

    YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID", "").strip()
    YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY", "").strip()
    YOOKASSA_RETURN_URL = os.getenv(
        "YOOKASSA_RETURN_URL", f"{FRONTEND_URL.rstrip('/')}/checkout/success"
    )
    YOOKASSA_WEBHOOK_SECRET = os.getenv("YOOKASSA_WEBHOOK_SECRET", "").strip()

    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@atelier.dev")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin123!")
    DEMO_EMAIL = os.getenv("DEMO_EMAIL", "demo@atelier.dev")
    DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "Demo123!")

    # Optional browser Maps JS / Geosearch key (safe to expose as Maps JS client key)
    YANDEX_MAPS_API_KEY = os.getenv("YANDEX_MAPS_API_KEY", "").strip()

    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "120 per minute")
    RATELIMIT_AUTH = os.getenv("RATELIMIT_AUTH", "20 per minute")
    # Flask-Limiter storage: memory:// unless Redis URL is explicitly provided.
    RATELIMIT_STORAGE_URI = REDIS_URL if REDIS_URL else "memory://"

    @property
    def yookassa_enabled(self) -> bool:
        return bool(self.YOOKASSA_SHOP_ID and self.YOOKASSA_SECRET_KEY)
