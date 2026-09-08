from flask import Blueprint, render_template, g

from models import Product, Purchase, Favorite
from auth_utils import login_required

mypage_bp = Blueprint("mypage", __name__, url_prefix="/mypage")

@mypage_bp.route("")
@login_required
def index():
    selling_count = Product.query.filter_by(seller_id=g.user.id).count()
    buying_count = Purchase.query.filter_by(buyer_id=g.user.id).count()
    favorite_count = Favorite.query.filter_by(user_id=g.user.id).count()

    return render_template(
        "mypage/index.html",
        selling_count=selling_count,
        buying_count=buying_count,
        favorite_count=favorite_count,
    )

@mypage_bp.route("/selling")
@login_required
def selling():
    products = Product.query.filter_by(seller_id=g.user.id).order_by(Product.created_at.desc()).all()

    pending_purchases = {}
    for p in products:
        purchase = Purchase.query.filter_by(product_id=p.id, status="결제완료").first()
        if purchase:
            pending_purchases[p.id] = purchase

    return render_template("mypage/selling.html", products=products, pending_purchases=pending_purchases)

@mypage_bp.route("/buying")
@login_required
def buying():
    purchases = Purchase.query.filter_by(buyer_id=g.user.id).order_by(Purchase.created_at.desc()).all()
    return render_template("mypage/buying.html", purchases=purchases)

@mypage_bp.route("/favorites")
@login_required
def favorites():
    favs = (
        Favorite.query.filter_by(user_id=g.user.id)
        .order_by(Favorite.created_at.desc())
        .all()
    )
    return render_template("mypage/favorites.html", favorites=favs)
