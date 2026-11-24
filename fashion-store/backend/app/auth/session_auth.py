from functools import wraps

from flask import flash, redirect, session, url_for

from app.models import User


def session_user() -> User | None:
    uid = session.get("user_id")
    if not uid:
        return None
    user = User.query.get(int(uid))
    if not user or not user.is_active:
        session.pop("user_id", None)
        return None
    return user


def login_user(user: User) -> None:
    session["user_id"] = user.id
    session.permanent = True


def logout_user() -> None:
    session.pop("user_id", None)


def web_login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = session_user()
        if not user:
            flash("Войдите, чтобы продолжить", "error")
            return redirect(url_for("web.login"))
        return fn(user, *args, **kwargs)

    return wrapper


def web_admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = session_user()
        if not user:
            flash("Войдите как администратор", "error")
            return redirect(url_for("web.login"))
        if not user.is_admin:
            flash("Недостаточно прав", "error")
            return redirect(url_for("web.home"))
        return fn(user, *args, **kwargs)

    return wrapper
