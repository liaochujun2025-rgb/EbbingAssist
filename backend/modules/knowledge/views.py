from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.common.response import response_ok
from backend.modules.knowledge.service import (
    create_entry,
    create_topic,
    delete_entry,
    delete_topic,
    list_entries,
    list_topics,
    update_entry,
    update_topic,
)

knowledge_bp = Blueprint("knowledge", __name__, url_prefix="/api/knowledge")


@knowledge_bp.get("/topics")
@jwt_required()
def topics_list():
    user_id = int(get_jwt_identity())
    topics = list_topics(user_id)
    data = [
        {"id": t.id, "name": t.name, "desc": t.desc, "created_at": t.created_at.isoformat()}
        for t in topics
    ]
    return response_ok({"items": data, "total": len(data)})


@knowledge_bp.post("/topics")
@jwt_required()
def topic_create():
    user_id = int(get_jwt_identity())
    payload = request.get_json() or {}
    topic = create_topic(user_id, payload)
    data = {"id": topic.id, "name": topic.name, "desc": topic.desc, "created_at": topic.created_at.isoformat()}
    return response_ok(data, "topic_created")


@knowledge_bp.put("/topics/<int:topic_id>")
@jwt_required()
def topic_update(topic_id: int):
    user_id = int(get_jwt_identity())
    payload = request.get_json() or {}
    topic = update_topic(user_id, topic_id, payload)
    data = {"id": topic.id, "name": topic.name, "desc": topic.desc, "created_at": topic.created_at.isoformat()}
    return response_ok(data, "topic_updated")


@knowledge_bp.delete("/topics/<int:topic_id>")
@jwt_required()
def topic_delete(topic_id: int):
    user_id = int(get_jwt_identity())
    delete_topic(user_id, topic_id)
    return response_ok(message="topic_deleted")


@knowledge_bp.get("/entries")
@jwt_required()
def entries_list():
    user_id = int(get_jwt_identity())
    filters = {
        "keyword": request.args.get("keyword"),
        "tag": request.args.get("tag"),
        "topic_id": request.args.get("topic_id", type=int),
    }
    page = request.args.get("page", default=1, type=int)
    page_size = request.args.get("page_size", default=20, type=int)
    total, items = list_entries(user_id, filters, page, page_size)
    data = [
        {
            "id": e.id,
            "title": e.title,
            "content": e.content,
            "tags": e.tags or [],
            "links": e.links or [],
            "topic_id": e.topic_id,
            "created_at": e.created_at.isoformat(),
            "updated_at": e.updated_at.isoformat(),
        }
        for e in items
    ]
    return response_ok({"items": data, "total": total, "page": page, "page_size": page_size})


@knowledge_bp.post("/entries")
@jwt_required()
def entry_create():
    user_id = int(get_jwt_identity())
    payload = request.get_json() or {}
    entry = create_entry(user_id, payload)
    return response_ok(entry.as_dict(), "entry_created")


@knowledge_bp.get("/entries/<int:entry_id>")
@jwt_required()
def entry_detail(entry_id: int):
    user_id = int(get_jwt_identity())
    from backend.modules.knowledge.service import _get_entry  # lazy import to avoid circular import in minimal env

    entry = _get_entry(user_id, entry_id)
    return response_ok(entry.as_dict())


@knowledge_bp.put("/entries/<int:entry_id>")
@jwt_required()
def entry_update(entry_id: int):
    user_id = int(get_jwt_identity())
    payload = request.get_json() or {}
    entry = update_entry(user_id, entry_id, payload)
    return response_ok(entry.as_dict(), "entry_updated")


@knowledge_bp.delete("/entries/<int:entry_id>")
@jwt_required()
def entry_delete(entry_id: int):
    user_id = int(get_jwt_identity())
    delete_entry(user_id, entry_id)
    return response_ok(message="entry_deleted")
