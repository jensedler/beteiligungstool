from flask import Blueprint, abort, send_file
from flask_login import login_required, current_user

from app.extensions import db
from app.models.konzept import Konzept
from app.services.export_service import export_docx, export_markdown

export_bp = Blueprint("export", __name__, template_folder="../../templates/export")


@export_bp.route("/<int:konzept_id>/docx")
@login_required
def docx(konzept_id):
    konzept = db.session.get(Konzept, konzept_id)
    if not konzept:
        abort(404)
    if current_user.is_fachamt and konzept.author_id != current_user.id:
        abort(403)
    filepath = export_docx(konzept)
    return send_file(filepath, as_attachment=True, download_name=f"{konzept.title}.docx")


@export_bp.route("/<int:konzept_id>/md")
@login_required
def md(konzept_id):
    konzept = db.session.get(Konzept, konzept_id)
    if not konzept:
        abort(404)
    if current_user.is_fachamt and konzept.author_id != current_user.id:
        abort(403)
    filepath = export_markdown(konzept)
    return send_file(filepath, as_attachment=True, download_name=f"{konzept.title}.md")
