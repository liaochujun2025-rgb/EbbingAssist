import logging
import uuid
from datetime import datetime
from typing import Optional

from flask import Flask, g, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError

from backend.common.errors import register_error_handlers
from backend.config import get_config
from backend.extensions import init_extensions, init_logging
from backend.modules import register_blueprints


def create_app(config_name: Optional[str] = None) -> Flask:
    """Application factory."""
    app = Flask(__name__)

    config_obj = get_config(config_name)
    app.config.from_object(config_obj)

    init_logging(app)
    init_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)

    @app.before_request
    def _inject_request_context():
        g.request_id = str(uuid.uuid4())
        g.current_user_id = None
        try:
            verify_jwt_in_request()
            g.current_user_id = get_jwt_identity()
        except NoAuthorizationError:
            g.current_user_id = None
        except Exception:
            g.current_user_id = None
        g.request_started_at = datetime.utcnow()

    if app.config.get("TESTING"):
        _register_test_routes(app)

    app.logger.info("App created with config=%s", config_obj.__class__.__name__)
    return app


def _register_test_routes(app: Flask) -> None:
    """Routes only for tests."""
    from backend.common.errors import AppError
    from backend.common.response import response_ok

    @app.route("/_test_error")
    def _test_error_route():
        raise AppError(code=4001, message="boom", status_code=418)

    @app.route("/_test_ok")
    def _test_ok():
        return response_ok({"status": "ok"})


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    application = create_app()
    application.run(host="0.0.0.0", port=8000)
