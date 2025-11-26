from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.common.response import response_ok
from backend.modules.plan.models import Plan, Task
from backend.modules.plan.service import (
    complete_task,
    create_plan,
    create_task,
    get_plan_detail,
    list_plans,
    update_plan,
    update_task,
    delete_plan,
)

plan_bp = Blueprint("plan", __name__, url_prefix="/api")


def _plan_to_dict(plan: Plan) -> dict:
    return {
        "id": plan.id,
        "title": plan.title,
        "goal": plan.goal,
        "deadline": plan.deadline.isoformat() if plan.deadline else None,
        "priority": plan.priority,
        "tags": plan.tags or [],
        "status": plan.status,
        "progress": plan.progress,
        "created_at": plan.created_at.isoformat(),
        "updated_at": plan.updated_at.isoformat(),
    }


@plan_bp.post("/plans")
@jwt_required()
def create_plan_route():
    user_id = int(get_jwt_identity())
    payload = request.get_json() or {}
    plan = create_plan(user_id, payload)
    return response_ok(_plan_to_dict(plan), "plan_created")


@plan_bp.get("/plans")
@jwt_required()
def list_plans_route():
    user_id = int(get_jwt_identity())
    filters = {
        "status": request.args.get("status"),
        "priority": request.args.get("priority"),
        "tag": request.args.get("tag"),
        "start_date": request.args.get("start_date"),
        "end_date": request.args.get("end_date"),
    }
    plans = list_plans(user_id, filters)
    data = [_plan_to_dict(p) for p in plans]
    return response_ok({"items": data, "total": len(data)})


@plan_bp.get("/plans/<int:plan_id>")
@jwt_required()
def plan_detail_route(plan_id: int):
    user_id = int(get_jwt_identity())
    plan = get_plan_detail(user_id, plan_id)
    plan_dict = _plan_to_dict(plan)
    plan_dict["tasks"] = [t.as_dict() for t in plan.tasks]
    return response_ok(plan_dict)


@plan_bp.put("/plans/<int:plan_id>")
@jwt_required()
def update_plan_route(plan_id: int):
    user_id = int(get_jwt_identity())
    payload = request.get_json() or {}
    plan = update_plan(user_id, plan_id, payload)
    return response_ok(_plan_to_dict(plan), "plan_updated")


@plan_bp.delete("/plans/<int:plan_id>")
@jwt_required()
def delete_plan_route(plan_id: int):
    user_id = int(get_jwt_identity())
    delete_plan(user_id, plan_id)
    return response_ok(message="plan_deleted")


@plan_bp.post("/plans/<int:plan_id>/tasks")
@jwt_required()
def create_task_route(plan_id: int):
    user_id = int(get_jwt_identity())
    payload = request.get_json() or {}
    task = create_task(user_id, plan_id, payload)
    return response_ok(task.as_dict(), "task_created")


@plan_bp.put("/tasks/<int:task_id>")
@jwt_required()
def update_task_route(task_id: int):
    user_id = int(get_jwt_identity())
    payload = request.get_json() or {}
    task = update_task(user_id, task_id, payload)
    return response_ok(task.as_dict(), "task_updated")


@plan_bp.post("/tasks/<int:task_id>/complete")
@jwt_required()
def complete_task_route(task_id: int):
    user_id = int(get_jwt_identity())
    task = complete_task(user_id, task_id)
    return response_ok(task.as_dict(), "task_completed")
