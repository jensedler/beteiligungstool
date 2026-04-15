from app.extensions import db


class Section(db.Model):
    __tablename__ = "sections"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, default="")
    order = db.Column(db.Integer, nullable=False, default=0)
    is_optional = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    questions = db.relationship("Question", backref="section", lazy="select", order_by="Question.order")

    def __repr__(self):
        return f"<Section {self.title}>"


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey("sections.id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    help_text = db.Column(db.Text, default="")
    question_type = db.Column(db.String(20), nullable=False, default="textarea")
    # text, textarea, yesno, multichoice, checklist
    options_json = db.Column(db.Text, default="")  # JSON for multichoice/checklist
    order = db.Column(db.Integer, nullable=False, default=0)
    is_required = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)

    answers = db.relationship("Answer", backref="question", lazy="dynamic")

    def __repr__(self):
        return f"<Question {self.id}: {self.text[:50]}>"
