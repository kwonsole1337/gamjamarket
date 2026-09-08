from datetime import datetime
from extensions import db

class Town(db.Model):
    __tablename__ = "towns"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    city = db.Column(db.String(50), nullable=False, default="서울특별시")
    center_lat = db.Column(db.Float, nullable=False)
    center_lng = db.Column(db.Float, nullable=False)
    radius_m = db.Column(db.Integer, nullable=False, default=1500)

    def __repr__(self):
        return f"<Town {self.name}>"

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    profile_emoji = db.Column(db.String(10), default="🥔")

    verified_town_id = db.Column(db.Integer, db.ForeignKey("towns.id"), nullable=True)
    verified_lat = db.Column(db.Float, nullable=True)
    verified_lng = db.Column(db.Float, nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)

    manner_score = db.Column(db.Float, default=36.5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bank_balance = db.Column(db.Integer, default=0)
    gamja_money_balance = db.Column(db.Integer, default=0)

    is_suspended = db.Column(db.Boolean, default=False)

    verified_town = db.relationship("Town", foreign_keys=[verified_town_id])

    def __repr__(self):
        return f"<User {self.username}>"

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(30), nullable=False, default="기타")
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    trade_type = db.Column(db.String(20), default="직거래")
    town_name = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default="판매중")
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    seller = db.relationship("User", foreign_keys=[seller_id])
    images = db.relationship("ProductImage", backref="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product {self.id} {self.title}>"

class ProductImage(db.Model):
    __tablename__ = "product_images"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    sort_order = db.Column(db.Integer, default=0)

class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", foreign_keys=[user_id])
    product = db.relationship("Product", foreign_keys=[product_id])

    __table_args__ = (db.UniqueConstraint("user_id", "product_id", name="uq_fav_user_product"),)

class Chat(db.Model):
    __tablename__ = "chats"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    shared_address = db.Column(db.String(255), nullable=True)
    shared_phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship("Product", foreign_keys=[product_id])
    buyer = db.relationship("User", foreign_keys=[buyer_id])
    seller = db.relationship("User", foreign_keys=[seller_id])

    __table_args__ = (db.UniqueConstraint("product_id", "buyer_id", name="uq_chat_product_buyer"),)

class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey("chats.id"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship("User", foreign_keys=[sender_id])

class Purchase(db.Model):
    __tablename__ = "purchases"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="대기")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    confirmed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    product = db.relationship("Product", foreign_keys=[product_id])
    buyer = db.relationship("User", foreign_keys=[buyer_id])
    seller = db.relationship("User", foreign_keys=[seller_id])

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey("purchases.id"), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    method = db.Column(db.String(20), default="감자페이")
    status = db.Column(db.String(20), default="결제완료")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    purchase = db.relationship("Purchase", foreign_keys=[purchase_id])

class WalletCharge(db.Model):
    __tablename__ = "wallet_charges"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    bank_balance_after = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", foreign_keys=[user_id])
