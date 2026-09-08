import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("ADMIN_SECRET_KEY", "gm-admin-internal-key-2024")

    ADMIN_DB_HOST = os.environ.get("ADMIN_MYSQL_HOST", "admin_db")
    ADMIN_DB_PORT = os.environ.get("ADMIN_MYSQL_PORT", "3306")
    ADMIN_DB_USER = os.environ.get("ADMIN_MYSQL_USER", "gmadmin_app")
    ADMIN_DB_PASSWORD = os.environ.get("ADMIN_MYSQL_PASSWORD", "gmAdminDbPass!45")
    ADMIN_DB_NAME = os.environ.get("ADMIN_MYSQL_DATABASE", "gamja_admin")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{ADMIN_DB_USER}:{ADMIN_DB_PASSWORD}"
        f"@{ADMIN_DB_HOST}:{ADMIN_DB_PORT}/{ADMIN_DB_NAME}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}

    MAIN_DB_HOST = os.environ.get("MAIN_MYSQL_HOST", "db")
    MAIN_DB_PORT = os.environ.get("MAIN_MYSQL_PORT", "3306")
    MAIN_DB_USER = os.environ.get("MAIN_MYSQL_USER", "gamja_app")
    MAIN_DB_PASSWORD = os.environ.get("MAIN_MYSQL_PASSWORD", "gamjaAppPass!23")
    MAIN_DB_NAME = os.environ.get("MAIN_MYSQL_DATABASE", "gamja_market")

    MAIN_DB_URI = (
        f"mysql+pymysql://{MAIN_DB_USER}:{MAIN_DB_PASSWORD}"
        f"@{MAIN_DB_HOST}:{MAIN_DB_PORT}/{MAIN_DB_NAME}?charset=utf8mb4"
    )

    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
