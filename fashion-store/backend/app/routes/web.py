"""Student-facing storefront: Flask + Jinja2 (no Node required)."""

from __future__ import annotations

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.exceptions import HTTPException

from app import db
from app.auth.session_auth import (
    login_user,
    logout_user,
    session_user,
    web_admin_required,
    web_login_required,
)
from app.models import ORDER_STATUSES, Category, Favorite, Order, Product, ProductVariant, User
from app.services import CartService, OrderService
from app.services.order_service import checkout_error_message
from app.utils import validate_email

bp = Blueprint("web", __name__)


def _fmt_rub(value) -> str:
    try:
        return f"{float(value):,.0f} ₽".replace(",", " ")
    except (TypeError, ValueError):
        return "—"


@bp.app_context_processor
def inject_globals():
    user = session_user()
    cart_count = 0
    if user:
        cart = CartService.get_or_create(user.id)
        cart_count = cart.to_dict().get("items_count", 0)
    return {
        "current_user": user,
        "cart_count": cart_count,
        "store_name": current_app.config.get("STORE_NAME", "Swaga"),
        "fmt_rub": _fmt_rub,
        "payments_mode": "yookassa"
        if (current_app.config.get("YOOKASSA_SHOP_ID") and current_app.config.get("YOOKASSA_SECRET_KEY"))
        else "mock",
    }


@bp.get("/")
def home():
    featured = (
        Product.query.filter_by(is_published=True, is_featured=True)
        .order_by(Product.created_at.desc())
        .limit(8)
        .all()
    )
    if not featured:
        featured = Product.query.filter_by(is_published=True).limit(8).all()
    return render_template("home.html", featured=featured)


@bp.get("/catalog")
def catalog():
    category_slug = request.args.get("category") or ""
    q = request.args.get("q") or ""
    sort = request.args.get("sort") or "newest"
    query = Product.query.filter_by(is_published=True)
    if category_slug:
        cat = Category.query.filter_by(slug=category_slug).first()
        if cat:
            query = query.filter_by(category_id=cat.id)
    if q:
        like = f"%{q}%"
        query = query.filter(
            Product.name.ilike(like) | Product.brand.ilike(like) | Product.description.ilike(like)
        )
    if sort == "price_asc":
        query = query.order_by(Product.base_price_rub.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.base_price_rub.desc())
    else:
        query = query.order_by(Product.created_at.desc())
    products = query.limit(48).all()
    categories = Category.query.order_by(Category.sort_order.asc()).all()
    return render_template(
        "catalog.html",
        products=products,
        categories=categories,
        category_slug=category_slug,
        q=q,
        sort=sort,
    )


@bp.get("/product/<slug>")
def product_detail(slug: str):
    product = Product.query.filter_by(slug=slug, is_published=True).first_or_404()
    swatches = product.color_swatches()
    colors = [s["name"] for s in swatches]
    selected_color = request.args.get("color") or (colors[0] if colors else "")
    if selected_color not in colors and colors:
        selected_color = colors[0]
    sizes = [v for v in product.variants if v.color == selected_color]
    return render_template(
        "product.html",
        product=product,
        colors=colors,
        swatches=swatches,
        selected_color=selected_color,
        sizes=sizes,
    )


@bp.route("/login", methods=["GET", "POST"])
def login():
    if session_user():
        return redirect(url_for("web.account"))
    if request.method == "POST":
        email_raw = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        try:
            email = validate_email(email_raw)
        except ValueError:
            flash("Неверный email или пароль", "error")
            return render_template("login.html", email=email_raw)
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Неверный email или пароль", "error")
            return render_template("login.html", email=email_raw)
        login_user(user)
        flash("С возвращением", "ok")
        return redirect(url_for("web.account"))
    return render_template("login.html", email="")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if session_user():
        return redirect(url_for("web.account"))
    if request.method == "POST":
        full_name = (request.form.get("full_name") or "").strip()
        email_raw = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        if len(password) < 8 or not full_name:
            flash("Имя и пароль (от 8 символов) обязательны", "error")
            return render_template("register.html")
        try:
            email = validate_email(email_raw)
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template("register.html")
        if User.query.filter_by(email=email).first():
            flash("Email уже занят", "error")
            return render_template("register.html")
        user = User(email=email, full_name=full_name, role="customer")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Аккаунт создан", "ok")
        return redirect(url_for("web.catalog"))
    return render_template("register.html")


@bp.post("/logout")
def logout():
    logout_user()
    flash("Вы вышли", "ok")
    return redirect(url_for("web.home"))


@bp.get("/cart")
@web_login_required
def cart(user: User):
    cart_obj = CartService.get_or_create(user.id)
    return render_template("cart.html", cart=cart_obj.to_dict())


@bp.post("/cart/add")
@web_login_required
def cart_add(user: User):
    variant_id = int(request.form.get("variant_id", 0))
    quantity = int(request.form.get("quantity", 1))
    try:
        CartService.add_item(user.id, variant_id, quantity)
        flash("Добавлено в корзину", "ok")
    except HTTPException as exc:
        flash(exc.description or "Ошибка корзины", "error")
    except Exception:
        flash("Ошибка корзины", "error")
    product = ProductVariant.query.get(variant_id)
    if product and product.product:
        return redirect(url_for("web.product_detail", slug=product.product.slug))
    return redirect(url_for("web.cart"))


@bp.post("/cart/update/<int:item_id>")
@web_login_required
def cart_update(user: User, item_id: int):
    quantity = int(request.form.get("quantity", 1))
    try:
        CartService.update_item(user.id, item_id, quantity)
    except HTTPException as exc:
        flash(exc.description or "Ошибка", "error")
    except Exception:
        flash("Ошибка", "error")
    return redirect(url_for("web.cart"))


@bp.post("/cart/remove/<int:item_id>")
@web_login_required
def cart_remove(user: User, item_id: int):
    CartService.remove_item(user.id, item_id)
    return redirect(url_for("web.cart"))


@bp.get("/favorites")
@web_login_required
def favorites(user: User):
    favs = Favorite.query.filter_by(user_id=user.id).order_by(Favorite.created_at.desc()).all()
    return render_template("favorites.html", favorites=favs)


@bp.post("/favorites/add/<int:product_id>")
@web_login_required
def favorite_add(user: User, product_id: int):
    product = Product.query.get_or_404(product_id)
    if not Favorite.query.filter_by(user_id=user.id, product_id=product.id).first():
        db.session.add(Favorite(user_id=user.id, product_id=product.id))
        db.session.commit()
    flash("В избранном", "ok")
    return redirect(request.referrer or url_for("web.product_detail", slug=product.slug))


@bp.route("/checkout", methods=["GET", "POST"])
@web_login_required
def checkout(user: User):
    cart_obj = CartService.get_or_create(user.id)
    cart_data = cart_obj.to_dict()
    default_form = {
        "shipping_name": user.full_name,
        "shipping_phone": user.phone or "+7",
        "shipping_city": "Москва",
        "shipping_address": "",
        "shipping_postal": "",
        "coupon_code": "",
        "delivery_type": "yandex_pvz",
        "pvz_id": "",
        "pvz_address": "",
        "pvz_work_time": "",
        "pvz_lat": "",
        "pvz_lon": "",
        "pvz_source": "",
    }
    if request.method == "GET":
        if not cart_data["items"]:
            flash("Корзина пуста", "error")
            return redirect(url_for("web.catalog"))
        return render_template(
            "checkout.html",
            cart=cart_data,
            form=default_form,
            yandex_maps_api_key=current_app.config.get("YANDEX_MAPS_API_KEY") or "",
        )

    delivery_type = (request.form.get("delivery_type") or "courier").strip()
    if delivery_type == "wb_pvz":
        delivery_type = "yandex_pvz"
    pvz_id = (request.form.get("pvz_id") or "").strip()
    pvz_address = (request.form.get("pvz_address") or "").strip()
    shipping_city = (request.form.get("shipping_city") or "").strip()
    shipping_address = (request.form.get("shipping_address") or "").strip()
    if delivery_type == "yandex_pvz":
        if not pvz_id or not pvz_address:
            flash("Выберите пункт выдачи Яндекс Маркет", "error")
            form = {**default_form, **{k: request.form.get(k, "") for k in default_form}}
            return render_template(
                "checkout.html",
                cart=cart_data,
                form=form,
                yandex_maps_api_key=current_app.config.get("YANDEX_MAPS_API_KEY") or "",
            )
        shipping_address = f"ПВЗ Яндекс Маркет: {pvz_address}"

    payload = {
        "shipping_name": (request.form.get("shipping_name") or "").strip(),
        "shipping_phone": (request.form.get("shipping_phone") or "").strip(),
        "shipping_city": shipping_city,
        "shipping_address": shipping_address,
        "shipping_postal": (request.form.get("shipping_postal") or "").strip() or None,
        "coupon_code": (request.form.get("coupon_code") or "").strip() or None,
        "delivery_type": delivery_type,
        "pvz_id": pvz_id or None,
        "pvz_meta": {
            "id": pvz_id,
            "address": pvz_address,
            "work_time": (request.form.get("pvz_work_time") or "").strip(),
            "lat": (request.form.get("pvz_lat") or "").strip() or None,
            "lon": (request.form.get("pvz_lon") or "").strip() or None,
            "source": (request.form.get("pvz_source") or "").strip() or None,
            "provider": "yandex_market",
        }
        if delivery_type == "yandex_pvz"
        else None,
    }
    if not all(
        [
            payload["shipping_name"],
            payload["shipping_phone"],
            payload["shipping_city"],
            payload["shipping_address"],
        ]
    ):
        flash("Заполните данные доставки", "error")
        form = {**default_form, **{k: request.form.get(k, "") for k in default_form}}
        return render_template(
            "checkout.html",
            cart=cart_data,
            form=form,
            yandex_maps_api_key=current_app.config.get("YANDEX_MAPS_API_KEY") or "",
        )
    try:
        order = OrderService.create_from_cart(user, payload)
        OrderService.create_payment(order, user_email=user.email)
    except HTTPException as exc:
        db.session.rollback()
        flash(checkout_error_message(exc.description), "error")
        cart_data = CartService.get_or_create(user.id).to_dict()
        form = {**default_form, **{k: request.form.get(k, "") for k in default_form}}
        return render_template(
            "checkout.html",
            cart=cart_data,
            form=form,
            yandex_maps_api_key=current_app.config.get("YANDEX_MAPS_API_KEY") or "",
        )
    except Exception:
        db.session.rollback()
        flash("Не удалось оформить заказ. Проверьте данные и попробуйте снова.", "error")
        cart_data = CartService.get_or_create(user.id).to_dict()
        form = {**default_form, **{k: request.form.get(k, "") for k in default_form}}
        return render_template(
            "checkout.html",
            cart=cart_data,
            form=form,
            yandex_maps_api_key=current_app.config.get("YANDEX_MAPS_API_KEY") or "",
        )
    return redirect(url_for("web.checkout_pay", public_id=order.public_id))


@bp.get("/checkout/pay/<public_id>")
@web_login_required
def checkout_pay(user: User, public_id: str):
    order = Order.query.filter_by(public_id=public_id, user_id=user.id).first_or_404()
    payment = order.payments[-1] if order.payments else None
    if not payment and order.status == "pending_payment":
        payment = OrderService.create_payment(order, user_email=user.email)
    return render_template("checkout_pay.html", order=order, payment=payment)


@bp.post("/checkout/mock-confirm/<public_id>")
@web_login_required
def mock_confirm(user: User, public_id: str):
    order = Order.query.filter_by(public_id=public_id, user_id=user.id).first_or_404()
    payment = order.payments[-1] if order.payments else None
    if not payment or not str(payment.provider_payment_id).startswith("mock_"):
        flash("Доступно только для mock-оплаты", "error")
        return redirect(url_for("web.checkout_pay", public_id=public_id))
    OrderService.mark_paid(order, payment)
    flash("Оплата подтверждена (mock)", "ok")
    return redirect(url_for("web.checkout_success", order=order.public_id))


@bp.get("/checkout/success")
@web_login_required
def checkout_success(user: User):
    public_id = request.args.get("order") or ""
    order = None
    if public_id:
        order = Order.query.filter_by(public_id=public_id, user_id=user.id).first()
    return render_template("checkout_success.html", order=order)


@bp.get("/account")
@web_login_required
def account(user: User):
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return render_template("account.html", orders=orders)


@bp.get("/admin")
@web_admin_required
def admin_panel(user: User):
    orders = Order.query.order_by(Order.created_at.desc()).limit(100).all()
    products = Product.query.order_by(Product.id.desc()).limit(100).all()
    revenue = sum(
        float(o.total_rub)
        for o in Order.query.filter(Order.status.in_(["paid", "processing", "shipped", "delivered"])).all()
    )
    return render_template(
        "admin.html",
        orders=orders,
        products=products,
        revenue=revenue,
        statuses=ORDER_STATUSES,
        users_count=User.query.count(),
    )


@bp.post("/admin/orders/<public_id>")
@web_admin_required
def admin_order_status(user: User, public_id: str):
    order = Order.query.filter_by(public_id=public_id).first_or_404()
    status = request.form.get("status")
    if status not in ORDER_STATUSES:
        abort(400)
    order.status = status
    db.session.commit()
    flash("Статус обновлён", "ok")
    return redirect(url_for("web.admin_panel"))
