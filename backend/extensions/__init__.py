import logging
import logging.config

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from redis import Redis

db = SQLAlchemy()
migrate = Migrate()
redis_client: Redis | None = None
scheduler = BackgroundScheduler()
jwt = JWTManager()


def init_logging(app: Flask) -> None:
    level = getattr(logging, app.config.get("LOG_LEVEL", "INFO"), logging.INFO)
    logging.basicConfig(level=level, format=app.config.get("LOG_FORMAT"))


def init_extensions(app: Flask) -> None:
    global redis_client

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    redis_url = app.config.get("REDIS_URL")
    redis_client = Redis.from_url(redis_url) if redis_url else None

    if app.config.get("SCHEDULER_ENABLED") and not app.config.get("TESTING"):
        if not scheduler.running:
            scheduler.start()
        app.extensions["scheduler"] = scheduler

    @app.teardown_appcontext
    def _shutdown_scheduler(exception=None):
        if scheduler.running and app.config.get("SCHEDULER_ENABLED"):
            scheduler.shutdown(wait=False)
