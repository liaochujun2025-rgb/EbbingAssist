from http import HTTPStatus

from flask import current_app as app
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
        app.logger.warning("AppError: %s", error.message)
        return response_error(error.code, error.message, error.status_code)

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        code = error.code or HTTPStatus.INTERNAL_SERVER_ERROR
        return response_error(code, error.description, code)

    @app.errorhandler(Exception)
    def handle_generic_error(error: Exception):
        app.logger.exception("Unhandled exception")
        return response_error(HTTPStatus.INTERNAL_SERVER_ERROR, "internal_error", HTTPStatus.INTERNAL_SERVER_ERROR)
