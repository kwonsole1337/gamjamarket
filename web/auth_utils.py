from functools import wraps
from flask import session, redirect, url_for, flash, g

from models import User

def load_current_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)
    return None

def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("user_id") or g.get("user") is None:
            session.clear()
            flash("로그인이 필요한 서비스입니다.", "error")
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapped

def town_verified_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not g.user.verified_town_id:
            flash("동네인증을 완료해야 이용할 수 있는 기능이에요.", "error")
            return redirect(url_for("location.verify_page"))
        return view_func(*args, **kwargs)

    return wrapped

def get_current_user():
    return getattr(g, "user", None)
