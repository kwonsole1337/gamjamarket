import os
import time

from flask import Flask, render_template
from sqlalchemy import text

from config import Config
from extensions import db
from auth_utils import load_current_user

def wait_for_db(app, retries=30, delay=2):
    with app.app_context():
        for attempt in range(1, retries + 1):
            try:
                db.session.execute(text("SELECT 1"))
                print(f"[gamjamarket] DB 연결 성공 (시도 {attempt}회)")
                return True
            except Exception as e:
                print(f"[gamjamarket] DB 연결 대기 중... ({attempt}/{retries}) - {e}")
                time.sleep(delay)
    print("[gamjamarket] DB 연결 실패. 앱은 계속 기동합니다.")
    return False

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.json.ensure_ascii = False

    db.init_app(app)

    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.products import products_bp
    from routes.preview import preview_bp
    from routes.chat import chat_bp
    from routes.location import location_bp
    from routes.purchase import purchase_bp
    from routes.payment import payment_bp
    from routes.wallet import wallet_bp
    from routes.mypage import mypage_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(preview_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(location_bp)
    app.register_blueprint(purchase_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(wallet_bp)
    app.register_blueprint(mypage_bp)

    app.before_request(load_current_user)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.template_filter("won")
    def won_format(value):
        try:
            return f"{int(value):,}원"
        except (TypeError, ValueError):
            return value

    @app.context_processor
    def inject_current_user():
        from flask import g
        return {"current_user": getattr(g, "user", None)}

    return app

app = create_app()

if __name__ == "__main__":
    wait_for_db(app)
    with app.app_context():
        db.create_all()
        from seed import run_seed
        run_seed()

    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
