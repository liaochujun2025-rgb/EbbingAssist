from flask import Flask

from backend.modules.auth.views import auth_bp
from backend.modules.health.views import health_bp
from backend.modules.plan.views import plan_bp
from backend.modules.user.views import user_bp
from backend.modules.knowledge.views import knowledge_bp
from backend.modules.study_log.views import study_log_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(plan_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(study_log_bp)
