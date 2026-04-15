from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.models.konzept import Konzept
from app.models.notification import Notification

main_bp = Blueprint("main", __name__, template_folder="../../templates/main")


@main_bp.route("/")
@login_required
def dashboard():
    if current_user.is_admin:
        konzepte = Konzept.query.order_by(Konzept.updated_at.desc()).all()
    elif current_user.is_db_team:
        konzepte = Konzept.query.filter(
            Konzept.status.in_(["submitted", "in_review", "returned", "final"])
        ).order_by(Konzept.updated_at.desc()).all()
    else:
        konzepte = Konzept.query.filter_by(author_id=current_user.id).order_by(Konzept.updated_at.desc()).all()

    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return render_template("dashboard.html", konzepte=konzepte, unread_count=unread_count)


@main_bp.route("/notifications")
@login_required
def notifications():
    notes = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(50).all()
    # mark as read
    for n in notes:
        if not n.is_read:
            n.is_read = True
    from app.extensions import db
    db.session.commit()
    return render_template("notifications.html", notifications=notes)


@main_bp.route("/notifications/count")
@login_required
def notification_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    if count > 0:
        return f'<span class="badge bg-danger">{count}</span>'
    return ""
