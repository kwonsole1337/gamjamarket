from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

db = SQLAlchemy()

main_engine = None

def init_main_engine(uri):
    global main_engine
    main_engine = create_engine(uri, pool_pre_ping=True, pool_recycle=280)
    return main_engine
