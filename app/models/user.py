from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="fachamt")  # fachamt, db_team, admin
    department = db.Column(db.String(255), default="")
    is_active = db.Column(db.Boolean, default=True)

    konzepte = db.relationship("Konzept", backref="author", lazy="dynamic")
    comments = db.relationship("Comment", backref="author", lazy="dynamic")
    notifications = db.relationship("Notification", backref="user", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_db_team(self):
        return self.role == "db_team"

    @property
    def is_fachamt(self):
        return self.role == "fachamt"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
