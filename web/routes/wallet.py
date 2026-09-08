from flask import Blueprint, render_template, request, jsonify, g

from extensions import db
from models import WalletCharge
from auth_utils import login_required

wallet_bp = Blueprint("wallet", __name__, url_prefix="")

@wallet_bp.route("/wallet/charge")
@login_required
def charge_page():
    recent_charges = (
        WalletCharge.query.filter_by(user_id=g.user.id)
        .order_by(WalletCharge.created_at.desc())
        .limit(10)
        .all()
    )
    return render_template("wallet/charge.html", recent_charges=recent_charges)

@wallet_bp.route("/api/wallet/charge", methods=["POST"])
@login_required
def charge_api():
    data = request.get_json(silent=True) or {}
    amount = data.get("amount")

    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "충전 금액이 올바르지 않습니다."}), 400

    if amount <= 0:
        return jsonify({"ok": False, "error": "충전 금액은 0원보다 커야 합니다."}), 400

    if amount % 10000 != 0:
        return jsonify({"ok": False, "error": "충전 금액은 1만원 단위로 입력해주세요."}), 400

    g.user.bank_balance = max(0, g.user.bank_balance - amount)
    g.user.gamja_money_balance += amount

    db.session.add(WalletCharge(user_id=g.user.id, amount=amount, bank_balance_after=g.user.bank_balance))
    db.session.commit()

    return jsonify({
        "ok": True,
        "amount": amount,
        "gamja_money_balance": g.user.gamja_money_balance,
        "bank_balance": g.user.bank_balance,
    })
