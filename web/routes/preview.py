from flask import Blueprint, request, jsonify, g, render_template_string

from auth_utils import login_required

preview_bp = Blueprint("preview", __name__, url_prefix="/api")

@preview_bp.route("/product/preview", methods=["POST"])
@login_required
def product_preview():
    if request.is_json:
        description = (request.json or {}).get("description", "")
    else:
        description = request.form.get("description", "")

    town = g.user.verified_town.name if g.user.verified_town else "동네미인증"

    context = {
        "닉네임": g.user.nickname,
        "동네": town,
        "작성자": g.user.nickname,
    }

    try:
        rendered_html = render_template_string(description, **context)
        return jsonify({"ok": True, "html": rendered_html})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 200
