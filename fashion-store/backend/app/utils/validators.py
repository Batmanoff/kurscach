from email_validator import EmailNotValidError, validate_email as _validate_email
from flask import jsonify


def validate_email(value: str) -> str:
    try:
        return _validate_email(value, check_deliverability=False).normalized
    except EmailNotValidError as exc:
        raise ValueError(str(exc)) from exc


def require_fields(payload: dict, fields: list[str]):
    missing = [f for f in fields if payload.get(f) in (None, "", [])]
    if missing:
        return jsonify({"error": "validation_error", "missing": missing}), 400
    return None
