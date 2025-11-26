from datetime import date, datetime
from typing import Iterable, Optional

from backend.common.errors import AppError
from backend.extensions import db
from backend.modules.knowledge.service import _get_entry
from backend.modules.study_log.models import StudyLog


def create_log(user_id: int, payload: dict) -> StudyLog:
    entry_id = payload.get("entry_id")
    if not entry_id:
        raise AppError(code=3201, message="missing_entry_id", status_code=400)
    _get_entry(user_id, entry_id)
    logged_at = _parse_date(payload.get("logged_at")) or date.today()
    log = StudyLog(
        user_id=user_id,
        entry_id=entry_id,
        note=payload.get("note"),
        logged_at=logged_at,
    )
    db.session.add(log)
    db.session.commit()
    return log


def list_logs(user_id: int, start_date: Optional[date], end_date: Optional[date]) -> Iterable[StudyLog]:
    query = StudyLog.query.filter_by(user_id=user_id)
    if start_date:
        query = query.filter(StudyLog.logged_at >= start_date)
    if end_date:
        query = query.filter(StudyLog.logged_at <= end_date)
    return query.order_by(StudyLog.logged_at.desc(), StudyLog.id.desc()).all()


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        raise AppError(code=1001, message="invalid_date", status_code=400)
