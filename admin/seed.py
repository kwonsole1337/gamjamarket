import hashlib

from extensions import db
from models import AdminUser

ADMIN_USERNAME = "gamjaadmin"
ADMIN_PASSWORD = "potato"

def _md5(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def run_seed():
    if AdminUser.query.first() is not None:
        print("[gm-admin] 관리자 계정이 이미 있어 시드를 건너뜁니다.")
        return

    print("[gm-admin] 관리자 계정을 생성합니다...")
    admin = AdminUser(
        username_hash=_md5(ADMIN_USERNAME),
        password_hash=_md5(ADMIN_PASSWORD),
        role="super_admin",
    )
    db.session.add(admin)
    db.session.commit()
    print("[gm-admin] 관리자 계정 생성 완료")
