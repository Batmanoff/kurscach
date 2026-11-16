from flask import Blueprint, jsonify, request

from app.models import Category, Product

bp = Blueprint("products", __name__)


@bp.get("")
def list_products():
    q = Product.query.filter_by(is_published=True)
    category = request.args.get("category")
    brand = request.args.get("brand")
    search = request.args.get("q")
    featured = request.args.get("featured")
    sort = request.args.get("sort", "newest")
    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(max(int(request.args.get("per_page", 24)), 1), 60)

    if category:
        cat = Category.query.filter_by(slug=category).first()
        if cat:
            q = q.filter_by(category_id=cat.id)
    if brand:
        q = q.filter(Product.brand.ilike(f"%{brand}%"))
    if search:
        like = f"%{search}%"
        q = q.filter(Product.name.ilike(like) | Product.description.ilike(like) | Product.brand.ilike(like))
    if featured in ("1", "true", "yes"):
        q = q.filter_by(is_featured=True)

    if sort == "price_asc":
        q = q.order_by(Product.base_price_rub.asc())
    elif sort == "price_desc":
        q = q.order_by(Product.base_price_rub.desc())
    else:
        q = q.order_by(Product.created_at.desc())

    pagination = q.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(
        {
            "items": [p.to_dict() for p in pagination.items],
            "page": pagination.page,
            "pages": pagination.pages,
            "total": pagination.total,
        }
    )


@bp.get("/categories")
def categories():
    cats = Category.query.order_by(Category.sort_order.asc(), Category.name.asc()).all()
    return jsonify({"items": [c.to_dict(with_children=True) for c in cats if c.parent_id is None]})


@bp.get("/<slug>")
def product_detail(slug: str):
    product = Product.query.filter_by(slug=slug, is_published=True).first_or_404()
    return jsonify({"product": product.to_dict()})
