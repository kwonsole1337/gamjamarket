import random
import re

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__, url_prefix="")

PHONE_PATTERN = re.compile(r"^01[016789]-\d{3,4}-\d{4}$")

BANK_BALANCE_CHOICES = list(range(10000, 100001, 10000))

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")
        nickname = request.form.get("nickname", "").strip()
        phone = request.form.get("phone", "").strip()

        if not username or not password or not nickname:
            flash("아이디, 비밀번호, 닉네임은 필수입니다.", "error")
            return render_template("auth/register.html", form=request.form)

        if len(password) < 8:
            flash("비밀번호는 8자 이상이어야 합니다.", "error")
            return render_template("auth/register.html", form=request.form)

        if password != password_confirm:
            flash("비밀번호가 일치하지 않습니다.", "error")
            return render_template("auth/register.html", form=request.form)

        if phone and not PHONE_PATTERN.match(phone):
            flash("전화번호 형식이 올바르지 않습니다. 예) 010-1234-5678", "error")
            return render_template("auth/register.html", form=request.form)

        if User.query.filter_by(username=username).first():
            flash("이미 사용 중인 아이디입니다.", "error")
            return render_template("auth/register.html", form=request.form)

        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            nickname=nickname,
            phone=phone or None,
            bank_balance=random.choice(BANK_BALANCE_CHOICES),
        )
        db.session.add(user)
        db.session.commit()

        flash("회원가입이 완료되었습니다. 로그인해주세요.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form={})

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user is None or not check_password_hash(user.password_hash, password):
            flash("아이디 또는 비밀번호가 올바르지 않습니다.", "error")
            return render_template("auth/login.html", username=username)

        if user.is_suspended:
            flash("이용이 정지된 계정입니다. 고객센터에 문의해주세요.", "error")
            return render_template("auth/login.html", username=username)

        session.clear()
        session["user_id"] = user.id
        session["nickname"] = user.nickname
        flash(f"{user.nickname}님, 환영합니다 🥔", "success")

        next_url = request.args.get("next")
        return redirect(next_url or url_for("main.home"))

    return render_template("auth/login.html", username="")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("로그아웃 되었습니다.", "success")
    return redirect(url_for("main.home"))
