from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify, abort
from sqlalchemy import exists

from extensions import db
from models import Chat, ChatMessage, Product
from auth_utils import login_required, town_verified_required
from routes.auth import PHONE_PATTERN

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")

@chat_bp.route("")
@login_required
def chat_list():
    chats = (
        Chat.query.filter(
            (Chat.buyer_id == g.user.id) | (Chat.seller_id == g.user.id)
        )
        .filter(exists().where(ChatMessage.chat_id == Chat.id))
        .order_by(Chat.created_at.desc())
        .all()
    )
    return render_template("chat/list.html", chats=chats)

@chat_bp.route("/start/<int:product_id>", methods=["POST"])
@login_required
@town_verified_required
def start_chat(product_id):
    product = Product.query.get_or_404(product_id)

    if product.seller_id == g.user.id:
        flash("본인 게시글에는 채팅을 시작할 수 없습니다.", "error")
        return redirect(url_for("products.detail", product_id=product_id))

    chat = Chat.query.filter_by(product_id=product_id, buyer_id=g.user.id).first()
    if not chat:
        chat = Chat(product_id=product_id, buyer_id=g.user.id, seller_id=product.seller_id)
        db.session.add(chat)
        db.session.commit()

    return redirect(url_for("chat.chat_room", chat_id=chat.id))

@chat_bp.route("/<int:chat_id>")
@login_required
@town_verified_required
def chat_room(chat_id):
    chat = Chat.query.get_or_404(chat_id)

    messages = ChatMessage.query.filter_by(chat_id=chat.id).order_by(ChatMessage.created_at.asc()).all()
    return render_template("chat/room.html", chat=chat, messages=messages)

@chat_bp.route("/<int:chat_id>/message", methods=["POST"])
@login_required
@town_verified_required
def send_message(chat_id):
    chat = Chat.query.get_or_404(chat_id)

    text = request.form.get("message", "").strip()
    if text:
        db.session.add(ChatMessage(chat_id=chat.id, sender_id=g.user.id, message=text))
        db.session.commit()

    return redirect(url_for("chat.chat_room", chat_id=chat.id))

@chat_bp.route("/<int:chat_id>/share_location", methods=["POST"])
@login_required
@town_verified_required
def share_location(chat_id):
    chat = Chat.query.get_or_404(chat_id)

    address = request.form.get("address", "").strip()
    phone = request.form.get("phone", "").strip()

    if phone and not PHONE_PATTERN.match(phone):
        flash("전화번호 형식이 올바르지 않습니다. 예) 010-1234-5678", "error")
        return redirect(url_for("chat.chat_room", chat_id=chat.id))

    chat.shared_address = address or chat.shared_address
    chat.shared_phone = phone or chat.shared_phone

    system_msg = f"📍 위치와 연락처를 공유했습니다: {address} / {phone}"
    db.session.add(ChatMessage(chat_id=chat.id, sender_id=g.user.id, message=system_msg))
    db.session.commit()

    return redirect(url_for("chat.chat_room", chat_id=chat.id))
