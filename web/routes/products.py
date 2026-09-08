import imghdr
import os
import uuid

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, g,
    current_app, send_from_directory, abort, jsonify
)
from werkzeug.utils import secure_filename

from extensions import db
from models import Product, ProductImage, Favorite
from auth_utils import login_required, town_verified_required
from routes.main import CATEGORIES

products_bp = Blueprint("products", __name__, url_prefix="/products")

ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp", "svg"}
ALLOWED_IMGHDR_KINDS = {"png", "jpeg", "gif", "webp"}

def _has_allowed_extension(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def _is_real_image(file_storage):
    filename = file_storage.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower()

    if ext == "svg":
        header = file_storage.stream.read(512)
        file_storage.stream.seek(0)
        return b"<svg" in header.lower() or b"<?xml" in header.lower()
        
    header = file_storage.stream.read(512)
    file_storage.stream.seek(0)
    kind = imghdr.what(None, h=header)
    return kind in ALLOWED_IMGHDR_KINDS

def _allowed_file(file_storage):
    filename = file_storage.filename or ""

    if "svg" in filename:
        return False
        
    return _has_allowed_extension(filename) and _is_real_image(file_storage)

@products_bp.route("/<int:product_id>")
def detail(product_id):
    product = Product.query.get_or_404(product_id)

    if not g.get("user") or g.user.id != product.seller_id:
        product.view_count = (product.view_count or 0) + 1
        db.session.commit()

    is_favorited = False
    if g.get("user"):
        is_favorited = Favorite.query.filter_by(
            user_id=g.user.id, product_id=product.id
        ).first() is not None

    favorite_count = Favorite.query.filter_by(product_id=product.id).count()

    return render_template(
        "products/detail.html",
        product=product,
        is_favorited=is_favorited,
        favorite_count=favorite_count,
    )

@products_bp.route("/new", methods=["GET", "POST"])
@login_required
@town_verified_required
def new():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "기타")
        description = request.form.get("description", "").strip()
        price = request.form.get("price", "0").replace(",", "")
        trade_type = request.form.get("trade_type", "직거래")

        if not title or not description:
            flash("제목과 설명을 입력해주세요.", "error")
            return render_template("products/write.html", categories=CATEGORIES[1:], form=request.form)

        try:
            price = int(price)
        except ValueError:
            price = 0

        town_name = g.user.verified_town.name if g.user.verified_town else None

        product = Product(
            seller_id=g.user.id,
            title=title,
            category=category,
            description=description,
            price=price,
            trade_type=trade_type,
            town_name=town_name,
        )
        db.session.add(product)
        db.session.flush()

        files = request.files.getlist("images")
        saved_count = 0
        for file in files[:5]:
            if file and file.filename and _allowed_file(file):
                ext = file.filename.rsplit(".", 1)[1].lower()
                fname = f"{uuid.uuid4().hex}.{ext}"
                file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], fname))
                db.session.add(ProductImage(product_id=product.id, filename=fname, sort_order=saved_count))
                saved_count += 1

        db.session.commit()
        flash("게시글이 등록되었습니다.", "success")
        return redirect(url_for("products.detail", product_id=product.id))

    return render_template("products/write.html", categories=CATEGORIES[1:], form={})

@products_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def edit(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id != g.user.id:
        abort(403)

    if request.method == "POST":
        product.title = request.form.get("title", product.title).strip()
        product.category = request.form.get("category", product.category)
        product.description = request.form.get("description", product.description).strip()
        product.status = request.form.get("status", product.status)
        try:
            product.price = int(request.form.get("price", product.price))
        except ValueError:
            pass

        files = request.files.getlist("images")
        saved_count = ProductImage.query.filter_by(product_id=product.id).count()
        for file in files[:5]:
            if file and file.filename and _allowed_file(file):
                ext = file.filename.rsplit(".", 1)[1].lower()
                fname = f"{uuid.uuid4().hex}.{ext}"
                file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], fname))
                db.session.add(ProductImage(product_id=product.id, filename=fname, sort_order=saved_count))
                saved_count += 1

        db.session.commit()
        flash("게시글이 수정되었습니다.", "success")
        return redirect(url_for("products.detail", product_id=product.id))

    return render_template("products/edit.html", product=product, categories=CATEGORIES[1:])

@products_bp.route("/<int:product_id>/delete", methods=["POST"])
@login_required
def delete(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id != g.user.id:
        abort(403)

    db.session.delete(product)
    db.session.commit()
    flash("게시글이 삭제되었습니다.", "success")
    return redirect(url_for("main.home"))

@products_bp.route("/<int:product_id>/favorite", methods=["POST"])
@login_required
def toggle_favorite(product_id):
    product = Product.query.get_or_404(product_id)
    fav = Favorite.query.filter_by(user_id=g.user.id, product_id=product.id).first()

    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({"favorited": False, "count": Favorite.query.filter_by(product_id=product.id).count()})

    db.session.add(Favorite(user_id=g.user.id, product_id=product.id))
    db.session.commit()
    return jsonify({"favorited": True, "count": Favorite.query.filter_by(product_id=product.id).count()})

@products_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
