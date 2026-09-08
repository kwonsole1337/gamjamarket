from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify, abort

from extensions import db
from models import Product, Purchase, Payment
from auth_utils import login_required, town_verified_required

payment_bp = Blueprint("payment", __name__, url_prefix="")

@payment_bp.route("/payment/checkout/<int:product_id>", methods=["GET"])
@login_required
@town_verified_required
def checkout_page(product_id):
    product = Product.query.get_or_404(product_id)

    if product.seller_id == g.user.id:
        flash("본인 상품은 구매할 수 없습니다.", "error")
        return redirect(url_for("products.detail", product_id=product_id))

    if product.status != "판매중":
        flash("이미 예약중이거나 거래완료된 상품입니다.", "error")
        return redirect(url_for("products.detail", product_id=product_id))

    return render_template("payment/checkout.html", product=product)

@payment_bp.route("/api/payment/checkout", methods=["POST"])
@login_required
def checkout_api():
    if not g.user.verified_town_id:
        return jsonify({
            "ok": False,
            "error": "동네인증을 완료해야 안전결제를 이용할 수 있어요.",
            "need_town_verification": True,
        }), 400

    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")

    product = Product.query.get_or_404(int(product_id))

    if product.seller_id == g.user.id:
        return jsonify({"ok": False, "error": "본인 상품은 구매할 수 없습니다."}), 400

    if product.status != "판매중":
        return jsonify({"ok": False, "error": "이미 예약중이거나 거래완료된 상품입니다."}), 400

    amount = product.price

    if g.user.gamja_money_balance < amount:
        return jsonify({
            "ok": False,
            "error": "감자머니 잔액이 부족합니다. 충전 후 다시 시도해주세요.",
            "need_charge": True,
        }), 400

    g.user.gamja_money_balance -= amount

    purchase = Purchase.query.filter_by(
        product_id=product.id, buyer_id=g.user.id, status="대기"
    ).first()
    if not purchase:
        purchase = Purchase(
            product_id=product.id,
            buyer_id=g.user.id,
            seller_id=product.seller_id,
            amount=amount,
            status="대기",
        )
        db.session.add(purchase)
        db.session.flush()
    else:
        purchase.amount = amount

    payment = Payment(purchase_id=purchase.id, amount=amount, status="결제완료", method="감자머니")
    db.session.add(payment)

    purchase.status = "결제완료"
    product.status = "예약중"

    db.session.commit()

    return jsonify({
        "ok": True,
        "purchase_id": purchase.id,
        "amount": amount,
        "gamja_money_balance": g.user.gamja_money_balance,
        "redirect_url": url_for("payment.complete_page", purchase_id=purchase.id),
    })

@payment_bp.route("/payment/complete/<int:purchase_id>")
@login_required
def complete_page(purchase_id):
    purchase = Purchase.query.get_or_404(purchase_id)
    if g.user.id not in (purchase.buyer_id, purchase.seller_id):
        abort(403)
    return render_template("payment/complete.html", purchase=purchase)
