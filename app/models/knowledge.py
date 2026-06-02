from app.extensions import db


class KnowledgeDocument(db.Model):
    __tablename__ = "knowledge_documents"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500), default="")
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), default="")
    priority = db.Column(db.Integer, nullable=False, default=10)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<KnowledgeDocument {self.title}>"
