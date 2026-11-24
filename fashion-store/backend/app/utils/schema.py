"""Lightweight SQLite column ensure for coursework (no full migrate required)."""

from __future__ import annotations

from sqlalchemy import inspect, text

from app import db


def ensure_order_delivery_columns() -> None:
    engine = db.engine
    insp = inspect(engine)
    if "orders" not in insp.get_table_names():
        return
    existing = {c["name"] for c in insp.get_columns("orders")}
    alters: list[str] = []
    if "delivery_type" not in existing:
        alters.append("ALTER TABLE orders ADD COLUMN delivery_type VARCHAR(32) DEFAULT 'courier'")
    if "pvz_id" not in existing:
        alters.append("ALTER TABLE orders ADD COLUMN pvz_id VARCHAR(64)")
    if "pvz_meta" not in existing:
        # SQLite JSON affinity
        alters.append("ALTER TABLE orders ADD COLUMN pvz_meta JSON")
    if not alters:
        return
    with engine.begin() as conn:
        for stmt in alters:
            conn.execute(text(stmt))
