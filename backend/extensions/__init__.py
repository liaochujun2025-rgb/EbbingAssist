import logging
import logging.config
from logging.handlers import RotatingFileHandler
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from redis import Redis
from typing import Optional

jwt = JWTManager()
db = SQLAlchemy()
migrate = Migrate()
redis_client: Optional[Redis] = None
scheduler = BackgroundScheduler()
jwt = JWTManager()


def init_logging(app: Flask) -> None:
    level = getattr(logging, app.config.get("LOG_LEVEL", "INFO"), logging.INFO)
    log_dir = Path(app.root_path).parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    formatter = logging.Formatter("%(message)s")
    handlers: list[logging.Handler] = []

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)
    handlers.append(stream_handler)

    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    handlers.append(file_handler)

    root = logging.getLogger()
    root.handlers = []
    root.setLevel(level)
    for h in handlers:
        root.addHandler(h)


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
