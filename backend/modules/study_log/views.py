from datetime import date, timedelta

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.common.response import response_ok
from backend.modules.study_log.service import create_log, list_logs, _parse_date

study_log_bp = Blueprint("study_log", __name__, url_prefix="/api/study")


@study_log_bp.post("/logs")
@jwt_required()
def create_study_log():
    user_id = int(get_jwt_identity())
    payload = request.get_json() or {}
    log = create_log(user_id, payload)
    return response_ok(log.as_dict(), "study_log_created")


@study_log_bp.get("/logs")
@jwt_required()
def list_study_logs():
    user_id = int(get_jwt_identity())
    start = _parse_date(request.args.get("start_date"))
    end = _parse_date(request.args.get("end_date"))
    if not start and not end:
        end = date.today()
        start = end - timedelta(days=6)
    logs = list_logs(user_id, start, end)
    data = [log.as_dict() for log in logs]
    return response_ok({"items": data, "total": len(data), "start_date": start.isoformat(), "end_date": end.isoformat()})
