import json
from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, g

from extensions import db
from models import Town
from auth_utils import login_required

location_bp = Blueprint("location", __name__, url_prefix="")

@location_bp.route("/location/verify", methods=["GET"])
@login_required
def verify_page():
    towns = Town.query.order_by(Town.name.asc()).all()
    towns_json = json.dumps([
        {
            "id": t.id,
            "name": t.name,
            "lat": t.center_lat,
            "lng": t.center_lng,
            "radius_m": t.radius_m,
        }
        for t in towns
    ])
    return render_template("location/verify.html", towns=towns, towns_json=towns_json)

@location_bp.route("/api/location/verify", methods=["POST"])
@login_required
def verify_api():
    data = request.get_json(silent=True) or {}
    lat = data.get("lat")
    lng = data.get("lng")
    town_id = data.get("town_id")
    client_verified = bool(data.get("client_verified", False))

    try:
        lat = float(lat)
        lng = float(lng)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "좌표 형식이 올바르지 않습니다."}), 400

    if not (33.0 <= lat <= 39.0 and 124.0 <= lng <= 132.0):
        return jsonify({"ok": False, "error": "대한민국 범위를 벗어난 좌표입니다."}), 400

    town = Town.query.get(town_id)
    if not town:
        return jsonify({"ok": False, "error": "존재하지 않는 동네입니다."}), 400

    if not client_verified:
        return jsonify({"ok": False, "error": "인증 범위 밖입니다."}), 400

    g.user.verified_town_id = town.id
    g.user.verified_lat = lat
    g.user.verified_lng = lng
    g.user.verified_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"ok": True, "town": town.name})
