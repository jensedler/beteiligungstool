from datetime import datetime, timezone

from app.extensions import db


class Konzept(db.Model):
    __tablename__ = "konzepte"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="draft")
    # draft, submitted, in_review, returned, final
    generated_text = db.Column(db.Text, default="")
    edited_text = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    submitted_at = db.Column(db.DateTime, nullable=True)
    finalized_at = db.Column(db.DateTime, nullable=True)

    answers = db.relationship("Answer", backref="konzept", lazy="select", cascade="all, delete-orphan")
    comments = db.relationship("Comment", backref="konzept", lazy="dynamic", cascade="all, delete-orphan")
    notifications = db.relationship("Notification", backref="konzept", lazy="dynamic", cascade="all, delete-orphan")


class Answer(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.Integer, primary_key=True)
    konzept_id = db.Column(db.Integer, db.ForeignKey("konzepte.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    value = db.Column(db.Text, default="")

    __table_args__ = (db.UniqueConstraint("konzept_id", "question_id"),)
