from flask import Flask, render_template, Response
from markupsafe import Markup
import markdown

from app.config import Config
from app.extensions import db, login_manager, migrate, csrf


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Markdown-Filter fuer Templates
    @app.template_filter('markdown')
    def markdown_filter(text):
        if not text:
            return ""
        return Markup(markdown.markdown(text, extensions=['tables', 'fenced_code']))

    from app.models import User, Section, Question, Konzept, Answer, Comment, Notification, KnowledgeDocument  # noqa: F401

    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.main.routes import main_bp
    from app.blueprints.konzept.routes import konzept_bp
    from app.blueprints.review.routes import review_bp
    from app.blueprints.admin.routes import admin_bp
    from app.blueprints.export.routes import export_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(konzept_bp, url_prefix="/konzept")
    app.register_blueprint(review_bp, url_prefix="/review")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(export_bp, url_prefix="/export")

    @app.route("/up")
    def healthcheck():
        return Response("OK", status=200, mimetype="text/plain")

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    return app
