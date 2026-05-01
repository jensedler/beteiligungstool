import json

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models.user import User
from app.models.question import Section, Question
from app.models.knowledge import KnowledgeDocument

admin_bp = Blueprint("admin", __name__, template_folder="../../templates/admin")


def require_admin(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ---- User management ----

@admin_bp.route("/users")
@login_required
@require_admin
def users():
    all_users = User.query.order_by(User.name).all()
    return render_template("admin_users.html", users=all_users)


@admin_bp.route("/users/new", methods=["GET", "POST"])
@login_required
@require_admin
def user_create():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        name = request.form.get("name", "").strip()
        role = request.form.get("role", "fachamt")
        department = request.form.get("department", "").strip()
        password = request.form.get("password", "")

        if not email or not name or not password:
            flash("Alle Pflichtfelder ausfuellen.", "warning")
            return render_template("admin_user_form.html", user=None)

        if User.query.filter_by(email=email).first():
            flash("E-Mail existiert bereits.", "danger")
            return render_template("admin_user_form.html", user=None)

        user = User(email=email, name=name, role=role, department=department)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Benutzer erstellt.", "success")
        return redirect(url_for("admin.users"))
    return render_template("admin_user_form.html", user=None)


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@require_admin
def user_edit(user_id):
    user = db.session.get(User, user_id)
    if not user:
        abort(404)
    if request.method == "POST":
        user.email = request.form.get("email", "").strip().lower()
        user.name = request.form.get("name", "").strip()
        user.role = request.form.get("role", user.role)
        user.department = request.form.get("department", "").strip()
        user.is_active = "is_active" in request.form
        password = request.form.get("password", "")
        if password:
            user.set_password(password)
        db.session.commit()
        flash("Benutzer aktualisiert.", "success")
        return redirect(url_for("admin.users"))
    return render_template("admin_user_form.html", user=user)


# ---- Sections / Questions management ----

@admin_bp.route("/sections")
@login_required
@require_admin
def sections():
    all_sections = Section.query.order_by(Section.order).all()
    return render_template("admin_sections.html", sections=all_sections)


@admin_bp.route("/sections/new", methods=["GET", "POST"])
@login_required
@require_admin
def section_create():
    if request.method == "POST":
        section = Section(
            title=request.form.get("title", "").strip(),
            description=request.form.get("description", "").strip(),
            order=request.form.get("order", 0, type=int),
            is_optional="is_optional" in request.form,
        )
        db.session.add(section)
        db.session.commit()
        flash("Sektion erstellt.", "success")
        return redirect(url_for("admin.sections"))
    return render_template("admin_section_form.html", section=None)


@admin_bp.route("/sections/<int:section_id>/edit", methods=["GET", "POST"])
@login_required
@require_admin
def section_edit(section_id):
    section = db.session.get(Section, section_id)
    if not section:
        abort(404)
    if request.method == "POST":
        section.title = request.form.get("title", "").strip()
        section.description = request.form.get("description", "").strip()
        section.order = request.form.get("order", section.order, type=int)
        section.is_optional = "is_optional" in request.form
        section.is_active = "is_active" in request.form
        db.session.commit()
        flash("Sektion aktualisiert.", "success")
        return redirect(url_for("admin.sections"))
    return render_template("admin_section_form.html", section=section)


@admin_bp.route("/sections/<int:section_id>/questions/new", methods=["GET", "POST"])
@login_required
@require_admin
def question_create(section_id):
    section = db.session.get(Section, section_id)
    if not section:
        abort(404)
    if request.method == "POST":
        options = request.form.get("options_json", "").strip()
        question = Question(
            section_id=section.id,
            text=request.form.get("text", "").strip(),
            help_text=request.form.get("help_text", "").strip(),
            question_type=request.form.get("question_type", "textarea"),
            options_json=options,
            order=request.form.get("order", 0, type=int),
            is_required="is_required" in request.form,
        )
        db.session.add(question)
        db.session.commit()
        flash("Frage erstellt.", "success")
        return redirect(url_for("admin.section_edit", section_id=section.id))
    return render_template("admin_question_form.html", section=section, question=None)


@admin_bp.route("/questions/<int:question_id>/edit", methods=["GET", "POST"])
@login_required
@require_admin
def question_edit(question_id):
    question = db.session.get(Question, question_id)
    if not question:
        abort(404)
    if request.method == "POST":
        question.text = request.form.get("text", "").strip()
        question.help_text = request.form.get("help_text", "").strip()
        question.question_type = request.form.get("question_type", question.question_type)
        question.options_json = request.form.get("options_json", "").strip()
        question.order = request.form.get("order", question.order, type=int)
        question.is_required = "is_required" in request.form
        question.is_active = "is_active" in request.form
        db.session.commit()
        flash("Frage aktualisiert.", "success")
        return redirect(url_for("admin.section_edit", section_id=question.section_id))
    return render_template("admin_question_form.html", section=question.section, question=question)


# ---- Knowledge documents management ----

@admin_bp.route("/knowledge")
@login_required
@require_admin
def knowledge_list():
    docs = KnowledgeDocument.query.order_by(KnowledgeDocument.priority, KnowledgeDocument.id).all()
    return render_template("admin_knowledge.html", docs=docs)


@admin_bp.route("/knowledge/new", methods=["GET", "POST"])
@login_required
@require_admin
def knowledge_create():
    if request.method == "POST":
        doc = KnowledgeDocument(
            title=request.form.get("title", "").strip(),
            description=request.form.get("description", "").strip(),
            content=request.form.get("content", "").strip(),
            category=request.form.get("category", "").strip(),
            priority=request.form.get("priority", 10, type=int),
        )
        db.session.add(doc)
        db.session.commit()
        flash("Dokument erstellt.", "success")
        return redirect(url_for("admin.knowledge_list"))
    return render_template("admin_knowledge_form.html", doc=None)


@admin_bp.route("/knowledge/<int:doc_id>/edit", methods=["GET", "POST"])
@login_required
@require_admin
def knowledge_edit(doc_id):
    doc = db.session.get(KnowledgeDocument, doc_id)
    if not doc:
        abort(404)
    if request.method == "POST":
        doc.title = request.form.get("title", "").strip()
        doc.description = request.form.get("description", "").strip()
        doc.content = request.form.get("content", "").strip()
        doc.category = request.form.get("category", "").strip()
        doc.priority = request.form.get("priority", doc.priority, type=int)
        doc.is_active = "is_active" in request.form
        db.session.commit()
        flash("Dokument aktualisiert.", "success")
        return redirect(url_for("admin.knowledge_list"))
    return render_template("admin_knowledge_form.html", doc=doc)


@admin_bp.route("/knowledge/<int:doc_id>/delete", methods=["POST"])
@login_required
@require_admin
def knowledge_delete(doc_id):
    doc = db.session.get(KnowledgeDocument, doc_id)
    if not doc:
        abort(404)
    db.session.delete(doc)
    db.session.commit()
    flash("Dokument gelöscht.", "success")
    return redirect(url_for("admin.knowledge_list"))
