import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "gamja-mkt-prod-k3y-8f4c!!")

    MYSQL_HOST = os.environ.get("MYSQL_HOST", "db")
    MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
    MYSQL_USER = os.environ.get("MYSQL_USER", "gamja_app")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "gamjaAppPass!23")
    MYSQL_DB = os.environ.get("MYSQL_DATABASE", "gamja_market")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    UPLOAD_FOLDER = os.path.join(basedir, "uploads")
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024

    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"
