import hashlib
import time
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy import text

from config import Config
from extensions import db, init_main_engine
import models
from models import AdminUser, LoginAttempt

def wait_for_db(label, check_fn, retries=30, delay=2):
    for attempt in range(1, retries + 1):
        try:
            check_fn()
            print(f"[gm-admin] {label} 연결 성공 (시도 {attempt}회)")
            return True
        except Exception as e:
            print(f"[gm-admin] {label} 연결 대기 중... ({attempt}/{retries}) - {e}")
            time.sleep(delay)
    print(f"[gm-admin] {label} 연결 실패. 앱은 계속 기동합니다.")
    return False

def md5(value):
    return hashlib.md5(value.encode("utf-8")).hexdigest()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.json.ensure_ascii = False

    db.init_app(app)
    main_engine = init_main_engine(Config.MAIN_DB_URI)

    @app.route("/", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "")
            password = request.form.get("password", "")

            try:
                query = (
                    f"SELECT id FROM login_attempts WHERE username = '{username}' "
                    "ORDER BY id DESC LIMIT 1"
                )
                row = db.session.execute(text(query)).first()
                if row is not None:
                    flash(f"최근 이 아이디로 로그인 시도 기록: {row[0]}", "info")
            except Exception:
                db.session.rollback()

            db.session.add(LoginAttempt(username=username[:100]))
            db.session.commit()

            admin = AdminUser.query.filter_by(
                username_hash=md5(username), password_hash=md5(password)
            ).first()

            if admin:
                session["admin_id"] = admin.id
                session["admin_username"] = username
                session["admin_role"] = admin.role
                return redirect(url_for("dashboard"))

            flash("아이디 또는 비밀번호가 올바르지 않습니다.", "error")

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    def admin_required(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not session.get("admin_id"):
                flash("로그인이 필요합니다.", "error")
                return redirect(url_for("login"))
            return view_func(*args, **kwargs)

        return wrapped

    @app.route("/dashboard")
    @admin_required
    def dashboard():
        with main_engine.connect() as conn:
            user_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar() or 0
            product_count = conn.execute(text("SELECT COUNT(*) FROM products")).scalar() or 0
            active_count = conn.execute(
                text("SELECT COUNT(*) FROM products WHERE status = '판매중'")
            ).scalar() or 0
            deal_row = conn.execute(
                text("SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM purchases WHERE status = '거래완료'")
            ).fetchone()
            deal_count, deal_amount = (deal_row[0], deal_row[1]) if deal_row else (0, 0)
            recent_users = conn.execute(
                text("SELECT id, username, nickname, created_at FROM users ORDER BY created_at DESC LIMIT 5")
            ).fetchall()

        return render_template(
            "dashboard.html",
            user_count=user_count,
            product_count=product_count,
            active_count=active_count,
            deal_count=deal_count,
            deal_amount=deal_amount,
            recent_users=recent_users,
        )

    @app.route("/members")
    @admin_required
    def members():
        with main_engine.connect() as conn:
            rows = conn.execute(
                text(
                    """
                    SELECT u.id, u.username, u.nickname, u.phone, u.manner_score,
                           u.created_at, u.is_suspended, u.gamja_money_balance,
                           t.name AS town_name
                    FROM users u
                    LEFT JOIN towns t ON t.id = u.verified_town_id
                    ORDER BY u.id
                    """
                )
            ).fetchall()
        return render_template("members.html", members=rows)

    @app.route("/members/<int:user_id>/suspend", methods=["POST"])
    @admin_required
    def suspend_member(user_id):
        with main_engine.begin() as conn:
            current = conn.execute(
                text("SELECT is_suspended FROM users WHERE id = :uid"), {"uid": user_id}
            ).scalar()
            if current is None:
                flash("존재하지 않는 회원입니다.", "error")
                return redirect(url_for("members"))
            conn.execute(
                text("UPDATE users SET is_suspended = :v WHERE id = :uid"),
                {"v": 0 if current else 1, "uid": user_id},
            )
        flash("회원 상태가 변경되었습니다.", "success")
        return redirect(url_for("members"))

    @app.route("/members/<int:user_id>/delete", methods=["POST"])
    @admin_required
    def delete_member(user_id):
        with main_engine.begin() as conn:
            conn.execute(
                text(
                    "DELETE FROM chat_messages WHERE sender_id = :uid "
                    "OR chat_id IN (SELECT id FROM chats WHERE buyer_id = :uid OR seller_id = :uid)"
                ),
                {"uid": user_id},
            )
            conn.execute(
                text("DELETE FROM chats WHERE buyer_id = :uid OR seller_id = :uid"),
                {"uid": user_id},
            )
            conn.execute(
                text(
                    "DELETE FROM favorites WHERE user_id = :uid "
                    "OR product_id IN (SELECT id FROM products WHERE seller_id = :uid)"
                ),
                {"uid": user_id},
            )
            conn.execute(
                text(
                    "DELETE FROM payments WHERE purchase_id IN "
                    "(SELECT id FROM purchases WHERE buyer_id = :uid OR seller_id = :uid OR confirmed_by = :uid)"
                ),
                {"uid": user_id},
            )
            conn.execute(
                text("DELETE FROM purchases WHERE buyer_id = :uid OR seller_id = :uid OR confirmed_by = :uid"),
                {"uid": user_id},
            )
            conn.execute(
                text("DELETE FROM product_images WHERE product_id IN (SELECT id FROM products WHERE seller_id = :uid)"),
                {"uid": user_id},
            )
            conn.execute(text("DELETE FROM wallet_charges WHERE user_id = :uid"), {"uid": user_id})
            conn.execute(text("DELETE FROM products WHERE seller_id = :uid"), {"uid": user_id})
            conn.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": user_id})

        flash("회원이 강제탈퇴 처리되었습니다.", "success")
        return redirect(url_for("members"))

    @app.route("/products")
    @admin_required
    def products():
        with main_engine.connect() as conn:
            rows = conn.execute(
                text(
                    """
                    SELECT p.id, p.title, p.category, p.price, p.status,
                           p.created_at, u.nickname AS seller_nickname
                    FROM products p
                    JOIN users u ON u.id = p.seller_id
                    ORDER BY p.id DESC
                    """
                )
            ).fetchall()
        return render_template("products.html", products=rows)

    @app.route("/products/<int:product_id>/delete", methods=["POST"])
    @admin_required
    def delete_product(product_id):
        with main_engine.begin() as conn:
            conn.execute(text("DELETE FROM favorites WHERE product_id = :pid"), {"pid": product_id})
            conn.execute(text("DELETE FROM product_images WHERE product_id = :pid"), {"pid": product_id})
            conn.execute(text("DELETE FROM products WHERE id = :pid"), {"pid": product_id})
        flash("상품이 삭제되었습니다.", "success")
        return redirect(url_for("products"))

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("error.html"), 500

    @app.context_processor
    def inject_admin():
        return {"admin_username": session.get("admin_username")}

    return app

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        wait_for_db("관리자 DB", lambda: db.session.execute(text("SELECT 1")))
        db.create_all()
        from seed import run_seed
        run_seed()

    from extensions import main_engine as _me
    wait_for_db("메인 감자마켓 DB", lambda: _me.connect().close())

    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
