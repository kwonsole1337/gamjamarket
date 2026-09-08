from datetime import datetime

from flask import Blueprint, jsonify, g

from extensions import db
from models import Purchase

purchase_bp = Blueprint("purchase", __name__, url_prefix="/api/purchase")

@purchase_bp.route("/<int:purchase_id>/confirm", methods=["POST"])
def confirm_purchase(purchase_id):
    if not g.get("user"):
        return jsonify({"ok": False, "error": "로그인이 필요합니다."}), 401

    purchase = Purchase.query.get_or_404(purchase_id)

    if purchase.status != "결제완료":
        return jsonify({"ok": False, "error": f"현재 상태({purchase.status})에서는 거래확정을 할 수 없습니다."}), 400

    purchase.status = "거래완료"
    purchase.confirmed_at = datetime.utcnow()
    purchase.confirmed_by = g.user.id

    purchase.product.status = "거래완료"

    purchase.seller.gamja_money_balance += purchase.amount

    db.session.commit()

    return jsonify({
        "ok": True,
        "purchase_id": purchase.id,
        "status": purchase.status,
        "confirmed_by_user_id": purchase.confirmed_by,
        "message": f"거래가 확정되어 {purchase.amount:,}원이 판매자에게 정산되었습니다.",
    })
