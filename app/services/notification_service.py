from app.extensions import db
from app.models.notification import Notification
from app.models.user import User
from app.models.konzept import Konzept


def notify_db_team(konzept: Konzept, message: str):
    db_team_users = User.query.filter_by(role="db_team", is_active=True).all()
    admin_users = User.query.filter_by(role="admin", is_active=True).all()
    for user in db_team_users + admin_users:
        n = Notification(user_id=user.id, konzept_id=konzept.id, message=message)
        db.session.add(n)
    db.session.commit()


def notify_author(konzept: Konzept, message: str):
    n = Notification(user_id=konzept.author_id, konzept_id=konzept.id, message=message)
    db.session.add(n)
    db.session.commit()
