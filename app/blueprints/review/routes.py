from datetime import datetime, timezone

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models.konzept import Konzept
from app.models.question import Section
from app.models.comment import Comment
from app.services.notification_service import notify_author

review_bp = Blueprint("review", __name__, template_folder="../../templates/review")


def require_reviewer(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if not (current_user.is_db_team or current_user.is_admin):
            abort(403)
        return f(*args, **kwargs)
    return decorated


@review_bp.route("/")
@login_required
@require_reviewer
def list_reviews():
    konzepte = Konzept.query.filter(
        Konzept.status.in_(["submitted", "in_review", "returned", "final"])
    ).order_by(Konzept.updated_at.desc()).all()
    return render_template("review_list.html", konzepte=konzepte)


@review_bp.route("/<int:konzept_id>")
@login_required
@require_reviewer
def detail(konzept_id):
    konzept = db.session.get(Konzept, konzept_id)
    if not konzept:
        abort(404)
    sections = Section.query.filter_by(is_active=True).order_by(Section.order).all()
    answers_map = {a.question_id: a.value for a in konzept.answers}
    comments = konzept.comments.order_by("created_at").all()
    return render_template("review_detail.html", konzept=konzept, sections=sections,
                           answers_map=answers_map, comments=comments)


@review_bp.route("/<int:konzept_id>/start_review", methods=["POST"])
@login_required
@require_reviewer
def start_review(konzept_id):
    konzept = db.session.get(Konzept, konzept_id)
    if not konzept or konzept.status != "submitted":
        abort(400)
    konzept.status = "in_review"
    db.session.commit()
    flash("Review gestartet.", "info")
    return redirect(url_for("review.detail", konzept_id=konzept.id))


@review_bp.route("/<int:konzept_id>/save_text", methods=["POST"])
@login_required
@require_reviewer
def save_text(konzept_id):
    konzept = db.session.get(Konzept, konzept_id)
    if not konzept or konzept.status not in ("submitted", "in_review"):
        abort(400)
    konzept.edited_text = request.form.get("edited_text", "")
    if konzept.status == "submitted":
        konzept.status = "in_review"
    db.session.commit()

    if request.headers.get("HX-Request"):
        return '<div class="alert alert-success alert-dismissible fade show" role="alert">Text gespeichert.<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>'
    flash("Text gespeichert.", "success")
    return redirect(url_for("review.detail", konzept_id=konzept.id))


@review_bp.route("/<int:konzept_id>/comment", methods=["POST"])
@login_required
@require_reviewer
def add_comment(konzept_id):
    konzept = db.session.get(Konzept, konzept_id)
    if not konzept:
        abort(404)
    text = request.form.get("text", "").strip()
    section_id = request.form.get("section_id", type=int)
    if not text:
        abort(400)
    comment = Comment(konzept_id=konzept.id, author_id=current_user.id, text=text, section_id=section_id)
    db.session.add(comment)
    db.session.commit()

    if request.headers.get("HX-Request"):
        comments = konzept.comments.order_by("created_at").all()
        return render_template("_comments.html", comments=comments)

    flash("Kommentar hinzugefuegt.", "success")
    return redirect(url_for("review.detail", konzept_id=konzept.id))


@review_bp.route("/<int:konzept_id>/return", methods=["POST"])
@login_required
@require_reviewer
def return_konzept(konzept_id):
    konzept = db.session.get(Konzept, konzept_id)
    if not konzept or konzept.status not in ("submitted", "in_review"):
        abort(400)
    konzept.status = "returned"
    db.session.commit()
    notify_author(konzept, f'Dein Konzept "{konzept.title}" wurde zur Ueberarbeitung zurueckgesendet.')
    flash("Konzept zurueckgesendet.", "info")
    return redirect(url_for("review.list_reviews"))


@review_bp.route("/<int:konzept_id>/finalize", methods=["POST"])
@login_required
@require_reviewer
def finalize(konzept_id):
    konzept = db.session.get(Konzept, konzept_id)
    if not konzept or konzept.status not in ("submitted", "in_review"):
        abort(400)
    konzept.status = "final"
    konzept.finalized_at = datetime.now(timezone.utc)
    db.session.commit()
    notify_author(konzept, f'Dein Konzept "{konzept.title}" wurde finalisiert.')
    flash("Konzept finalisiert.", "success")
    return redirect(url_for("review.detail", konzept_id=konzept.id))
