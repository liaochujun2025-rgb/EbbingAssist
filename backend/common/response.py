from flask import jsonify


def response_ok(data=None, message: str = "ok", status_code: int = 200):
    payload = {"code": 0, "message": message, "data": data or {}}
    return jsonify(payload), status_code


def response_error(code: int, message: str, status_code: int = 400):
    payload = {"code": code, "message": message, "data": None}
    return jsonify(payload), status_code
