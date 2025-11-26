from datetime import datetime
from typing import Iterable, Optional

from flask import abort

from backend.common.errors import AppError
from backend.extensions import db
from backend.modules.plan.models import Plan, Task

PLAN_STATUSES = {"not_started", "in_progress", "completed", "delayed"}
TASK_STATUSES = {"todo", "doing", "done", "blocked", "delayed"}


def _validate_status(value: str, allowed: set[str], code: int):
    if value not in allowed:
        raise AppError(code=code, message="invalid_status", status_code=400)


def _recalc_progress(plan: Plan):
    total = len(plan.tasks)
    if total == 0:
        plan.progress = 0.0
        plan.status = plan.status or "not_started"
    else:
        done = len([t for t in plan.tasks if t.status == "done"])
        plan.progress = round(done / total, 4)
        if done == total:
            plan.status = "completed"
        elif done == 0:
            plan.status = "not_started"
        else:
            plan.status = "in_progress"


def create_plan(user_id: int, payload: dict) -> Plan:
    title = (payload.get("title") or "").strip()
    if not title:
        raise AppError(code=2101, message="missing_title", status_code=400)
    plan = Plan(
        user_id=user_id,
        title=title,
        goal=payload.get("goal"),
        deadline=_parse_date(payload.get("deadline")),
        priority=payload.get("priority", "medium"),
        tags=payload.get("tags") or [],
        status=payload.get("status", "not_started"),
    )
    _validate_status(plan.status, PLAN_STATUSES, 2102)
    db.session.add(plan)
    db.session.commit()
    return plan


def update_plan(user_id: int, plan_id: int, payload: dict) -> Plan:
    plan = _get_user_plan(user_id, plan_id)
    if "title" in payload:
        title = (payload.get("title") or "").strip()
        if not title:
            raise AppError(code=2101, message="missing_title", status_code=400)
        plan.title = title
    if "goal" in payload:
        plan.goal = payload.get("goal")
    if "deadline" in payload:
        plan.deadline = _parse_date(payload.get("deadline"))
    if "priority" in payload:
        plan.priority = payload.get("priority")
    if "tags" in payload:
        plan.tags = payload.get("tags") or []
    if "status" in payload:
        status = payload.get("status")
        _validate_status(status, PLAN_STATUSES, 2102)
        plan.status = status
    db.session.commit()
    return plan


def delete_plan(user_id: int, plan_id: int) -> None:
    plan = _get_user_plan(user_id, plan_id)
    db.session.delete(plan)
    db.session.commit()


def list_plans(user_id: int, filters: dict) -> Iterable[Plan]:
    query = Plan.query.filter_by(user_id=user_id)
    status = filters.get("status")
    if status:
        query = query.filter(Plan.status == status)
    priority = filters.get("priority")
    if priority:
        query = query.filter(Plan.priority == priority)
    tag = filters.get("tag")
    if tag:
        query = query.filter(Plan.tags.contains([tag]))
    start_date = _parse_date(filters.get("start_date"))
    end_date = _parse_date(filters.get("end_date"))
    if start_date:
        query = query.filter(Plan.deadline >= start_date)
    if end_date:
        query = query.filter(Plan.deadline <= end_date)
    return query.order_by(Plan.deadline.asc().nulls_last(), Plan.id.desc()).all()


def get_plan_detail(user_id: int, plan_id: int) -> Plan:
    return _get_user_plan(user_id, plan_id)


def create_task(user_id: int, plan_id: int, payload: dict) -> Task:
    plan = _get_user_plan(user_id, plan_id)
    title = (payload.get("title") or "").strip()
    if not title:
        raise AppError(code=2201, message="missing_title", status_code=400)
    task = Task(
        user_id=user_id,
        plan_id=plan.id,
        title=title,
        desc=payload.get("desc"),
        estimate_minutes=payload.get("estimate_minutes"),
        priority=payload.get("priority", "medium"),
        status=payload.get("status", "todo"),
        due_date=_parse_date(payload.get("due_date")),
        tags=payload.get("tags") or [],
        order_no=payload.get("order_no", 0),
    )
    _validate_status(task.status, TASK_STATUSES, 2202)
    db.session.add(task)
    db.session.flush()
    _recalc_progress(plan)
    db.session.commit()
    return task


def update_task(user_id: int, task_id: int, payload: dict) -> Task:
    task = _get_user_task(user_id, task_id)
    plan = _get_user_plan(user_id, task.plan_id)
    if "title" in payload:
        title = (payload.get("title") or "").strip()
        if not title:
            raise AppError(code=2201, message="missing_title", status_code=400)
        task.title = title
    if "desc" in payload:
        task.desc = payload.get("desc")
    if "estimate_minutes" in payload:
        task.estimate_minutes = payload.get("estimate_minutes")
    if "priority" in payload:
        task.priority = payload.get("priority")
    if "status" in payload:
        status = payload.get("status")
        _validate_status(status, TASK_STATUSES, 2202)
        task.status = status
    if "due_date" in payload:
        task.due_date = _parse_date(payload.get("due_date"))
    if "tags" in payload:
        task.tags = payload.get("tags") or []
    if "order_no" in payload:
        task.order_no = payload.get("order_no")
    if "focus_minutes" in payload:
        task.focus_minutes = payload.get("focus_minutes") or 0
    _recalc_progress(plan)
    db.session.commit()
    return task


def complete_task(user_id: int, task_id: int) -> Task:
    task = _get_user_task(user_id, task_id)
    task.status = "done"
    task.updated_at = datetime.utcnow()
    plan = _get_user_plan(user_id, task.plan_id)
    _recalc_progress(plan)
    db.session.commit()
    return task


def _parse_date(value: Optional[str]):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        raise AppError(code=1001, message="invalid_date", status_code=400)


def _get_user_plan(user_id: int, plan_id: int) -> Plan:
    plan = Plan.query.filter_by(id=plan_id, user_id=user_id).first()
    if not plan:
        abort(404)
    return plan


def _get_user_task(user_id: int, task_id: int) -> Task:
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        abort(404)
    return task
