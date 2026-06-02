import json
from datetime import datetime, timezone

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user

from app.extensions import db
from app.models.konzept import Konzept, Answer
from app.models.comment import Comment
from app.models.question import Section, Question
from app.services.ai_service import start_generation
from app.services.diff_service import compute_diff_html
from app.services.notification_service import notify_db_team, notify_author

konzept_bp = Blueprint("konzept", __name__, template_folder="../../templates/konzept")


@konzept_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Bitte gib einen Titel ein.", "warning")
            return render_template("konzept_create.html")
        konzept = Konzept(title=title, author_id=current_user.id, status="draft")
        db.session.add(konzept)
        db.session.commit()
        return redirect(url_for("konzept.edit", konzept_id=konzept.id))
    return render_template("konzept_create.html")


@konzept_bp.route("/<int:konzept_id>")
@login_required
def view(konzept_id):
    konzept = db.session.get(Konzept, konzept_id)
    if not konzept:
        abort(404)
    if current_user.is_fachamt and konzept.author_id != current_user.id:
        abort(403)
    sections = Section.query.filter_by(is_active=True).order_by(Section.order).all()
    answers_map = {a.question_id: a.value for a in konzept.answers}
    comments = konzept.comments.order_by("created_at").all()
    diff_old_html = diff_new_html = None
    if (konzept.generated_text and konzept.edited_text
            and konzept.generated_text != konzept.edited_text):
        diff_old_html, diff_new_html = compute_diff_html(
            konzept.generated_text, konzept.edited_text)
    return render_template("konzept_view.html", konzept=konzept, sections=sections,
                           answers_map=answers_map, comments=comments,
                           diff_old_html=diff_old_html, diff_new_html=diff_new_html)


@konzept_bp.route("/<int:konzept_id>/edit")
@login_required
def edit(konzept_id):
    konzept = db.session.get(Konzept, konzept_id)
    if not konzept:
        abort(404)
    if konzept.author_id != current_user.id:
        abort(403)
    if konzept.status not in ("draft", "returned"):
        flash("Dieses Konzept kann nicht mehr bearbeitet werden.", "warning")
        return redirect(url_for("konzept.view", konzept_id=konzept.id))
    sections = Section.query.filter_by(is_active=True).order_by(Section.order).all()
    answers_map = {a.question_id: a.value for a in konzept.answers}
    return render_template("konzept_edit.html", konzept=konzept, sections=sections, answers_map=answers_map)


@konzept_bp.route("/<int:konzept_id>/section/<int:section_id>")
@login_required
def section_form(konzept_id, section_id):
    konzept = db.session.get(Konzept, konzept_id)
    if not konzept or konzept.author_id != current_user.id:
        abort(403)
    section = db.session.get(Section, section_id)
    if not section:
        abort(404)
    answers_map = {a.question_id: a.value for a in konzept.answers}
    sections = Section.query.filter_by(is_active=True).order_by(Section.order).all()
    section_ids = [s.id for s in sections]
    try:
        idx = section_ids.index(section_id)
        next_section = sections[idx + 1] if idx + 1 < len(sections) else None
    except ValueError:
        next_section = None
    return render_template("_section_form.html", konzept=konzept, section=section,
                           answers_map=answers_map, next_section=next_section)


@konzept_bp.route("/<int:konzept_id>/save_section", methods=["POST"])
@login_required
def save_section(konzept_id):
    konzept = db.session.get(Konzept, konzept_id)
    if not konzept or konzept.author_id != current_user.id:
        abort(403)
    if konzept.status not in ("draft", "returned"):
        abort(400)

    section_id = request.form.get("section_id", type=int)
    questions = Question.query.filter_by(section_id=section_id, is_active=True).all()

    for q in questions:
        field_name = f"question_{q.id}"
        if q.question_type == "checklist":
            value = json.dumps(request.form.getlist(field_name))
        else:
            value = request.form.get(field_name, "")

        answer = Answer.query.filter_by(konzept_id=konzept.id, question_id=q.id).first()
        if answer:
            answer.value = value
        else:
            answer = Answer(konzept_id=konzept.id, question_id=q.id, value=value)
            db.session.add(answer)

    db.session.commit()

    if request.headers.get("HX-Request"):
        return '<div class="alert alert-success alert-dismissible fade show" role="alert"><i class="bi bi-check-circle-fill me-2"></i>Abschnitt erfolgreich gespeichert.<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>'

    flash("Abschnitt erfolgreich gespeichert.", "success")
    return redirect(url_for("konzept.edit", konzept_id=konzept.id))


@konzept_bp.route("/<int:konzept_id>/submit", methods=["POST"])
@login_required
def submit(konzept_id):
    konzept = db.session.get(Konzept, konzept_id)
    if not konzept or konzept.author_id != current_user.id:
        abort(403)
    if konzept.status not in ("draft", "returned"):
        abort(400)

    konzept.status = "submitted"
    konzept.submitted_at = datetime.now(timezone.utc)
    konzept.is_generating = True
    konzept.edited_text = ""
    konzept.generated_text = ""
    db.session.commit()

    start_generation(current_app._get_current_object(), konzept.id)

    notify_db_team(konzept, f'Neues Konzept eingereicht: "{konzept.title}"')
    flash("Formular erfolgreich abgeschickt. Die KI generiert das Beteiligungskonzept im Hintergrund.", "success")
    return redirect(url_for("konzept.view", konzept_id=konzept.id))


@konzept_bp.route("/<int:konzept_id>/generate", methods=["POST"])
@login_required
def generate(konzept_id):
    konzept = db.session.get(Konzept, konzept_id)
    if not konzept:
        abort(404)
    # Nur Autor, D&B Team oder Admin duerfen generieren
    if not (konzept.author_id == current_user.id or current_user.is_db_team or current_user.is_admin):
        abort(403)
    if konzept.status == "draft":
        flash("Bitte zuerst einreichen.", "warning")
        return redirect(url_for("konzept.view", konzept_id=konzept.id))

    konzept.is_generating = True
    db.session.commit()

    start_generation(current_app._get_current_object(), konzept.id)

    flash("KI-Generierung gestartet. Die Seite aktualisiert sich automatisch.", "info")
    return redirect(url_for("konzept.view", konzept_id=konzept.id))


@konzept_bp.route("/<int:konzept_id>/comment", methods=["POST"])
@login_required
def add_comment(konzept_id):
    konzept = db.session.get(Konzept, konzept_id)
    if not konzept:
        abort(404)
    if konzept.author_id != current_user.id:
        abort(403)
    text = request.form.get("text", "").strip()
    if not text:
        abort(400)
    comment = Comment(konzept_id=konzept.id, author_id=current_user.id, text=text)
    db.session.add(comment)
    db.session.commit()
    if request.headers.get("HX-Request"):
        comments = konzept.comments.order_by("created_at").all()
        return render_template("konzept/_comments.html", comments=comments)
    flash("Kommentar hinzugefügt.", "success")
    return redirect(url_for("konzept.view", konzept_id=konzept.id))


@konzept_bp.route("/<int:konzept_id>/delete", methods=["POST"])
@login_required
def delete(konzept_id):
    konzept = db.session.get(Konzept, konzept_id)
    if not konzept:
        abort(404)
    if konzept.author_id != current_user.id and not current_user.is_admin:
        abort(403)
    db.session.delete(konzept)
    db.session.commit()
    flash("Konzept geloescht.", "info")
    return redirect(url_for("main.dashboard"))
