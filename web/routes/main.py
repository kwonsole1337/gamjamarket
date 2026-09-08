from flask import Blueprint, render_template, request, g

from models import Product

main_bp = Blueprint("main", __name__, url_prefix="")

CATEGORIES = ["전체", "디지털기기", "가구/인테리어", "의류", "생활가전", "유아동", "도서", "스포츠/레저", "기타"]

@main_bp.route("/")
def home():
    category = request.args.get("category", "전체")
    q = request.args.get("q", "").strip()

    query = Product.query.order_by(Product.created_at.desc())

    if category and category != "전체":
        query = query.filter(Product.category == category)

    if q:
        query = query.filter(Product.title.ilike(f"%{q}%"))

    products = query.limit(60).all()

    my_town = None
    if g.get("user") and g.user.verified_town:
        my_town = g.user.verified_town.name

    return render_template(
        "main/home.html",
        products=products,
        categories=CATEGORIES,
        active_category=category,
        q=q,
        my_town=my_town,
    )
