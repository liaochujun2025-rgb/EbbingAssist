from http import HTTPStatus
import traceback
import json
from datetime import datetime

from flask import current_app as app
from flask import g, request
from werkzeug.exceptions import HTTPException

from backend.common.response import response_error


class AppError(Exception):
    def __init__(self, code: int, message: str, status_code: int = HTTPStatus.BAD_REQUEST):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        _log_exception(app.logger, error, error.status_code)
        return response_error(error.code, error.message, error.status_code)

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        code = error.code or HTTPStatus.INTERNAL_SERVER_ERROR
        _log_exception(app.logger, error, code)
        return response_error(code, error.description, code)

    @app.errorhandler(Exception)
    def handle_generic_error(error: Exception):
        _log_exception(app.logger, error, HTTPStatus.INTERNAL_SERVER_ERROR)
        return response_error(HTTPStatus.INTERNAL_SERVER_ERROR, "internal_error", HTTPStatus.INTERNAL_SERVER_ERROR)
def _log_exception(logger, error: Exception, status_code: int):
    trace_id = getattr(g, "request_id", None)
    user_id = getattr(g, "current_user_id", None)
    stack = traceback.format_exc()
    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": "ERROR",
        "logger": logger.name,
        "trace_id": trace_id,
        "path": request.path if request else "",
        "method": request.method if request else "",
        "status_code": status_code,
        "user_id": user_id,
        "error_message": str(error),
        "stack": stack,
    }
    logger.error(json.dumps(payload, ensure_ascii=False))
