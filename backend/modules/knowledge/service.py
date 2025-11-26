from datetime import datetime
from typing import Iterable, Optional

from flask import abort
from sqlalchemy import or_

from backend.common.errors import AppError
from backend.extensions import db
from backend.modules.knowledge.models import KnowledgeEntry, Topic


def list_topics(user_id: int) -> Iterable[Topic]:
    return Topic.query.filter_by(user_id=user_id).order_by(Topic.created_at.desc()).all()


def create_topic(user_id: int, payload: dict) -> Topic:
    name = (payload.get("name") or "").strip()
    if not name:
        raise AppError(code=3001, message="missing_name", status_code=400)
    topic = Topic(user_id=user_id, name=name, desc=payload.get("desc"))
    db.session.add(topic)
    db.session.commit()
    return topic


def update_topic(user_id: int, topic_id: int, payload: dict) -> Topic:
    topic = _get_topic(user_id, topic_id)
    if "name" in payload:
        name = (payload.get("name") or "").strip()
        if not name:
            raise AppError(code=3001, message="missing_name", status_code=400)
        topic.name = name
    if "desc" in payload:
        topic.desc = payload.get("desc")
    db.session.commit()
    return topic


def delete_topic(user_id: int, topic_id: int) -> None:
    topic = _get_topic(user_id, topic_id)
    db.session.delete(topic)
    db.session.commit()


def list_entries(user_id: int, filters: dict, page: int, page_size: int):
    query = KnowledgeEntry.query.filter_by(user_id=user_id)
    keyword = filters.get("keyword")
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(or_(KnowledgeEntry.title.ilike(like), KnowledgeEntry.content.ilike(like)))
    tag = filters.get("tag")
    if tag:
        query = query.filter(KnowledgeEntry.tags.contains([tag]))
    topic_id = filters.get("topic_id")
    if topic_id:
        query = query.filter(KnowledgeEntry.topic_id == topic_id)
    total = query.count()
    items = (
        query.order_by(KnowledgeEntry.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return total, items


def create_entry(user_id: int, payload: dict) -> KnowledgeEntry:
    title = (payload.get("title") or "").strip()
    content = (payload.get("content") or "").strip()
    if not title or not content:
        raise AppError(code=3101, message="missing_title_or_content", status_code=400)
    topic_id = payload.get("topic_id")
    if topic_id:
        _get_topic(user_id, topic_id)
    entry = KnowledgeEntry(
        user_id=user_id,
        topic_id=topic_id,
        title=title,
        content=content,
        tags=payload.get("tags") or [],
        links=payload.get("links") or [],
    )
    db.session.add(entry)
    db.session.commit()
    return entry


def update_entry(user_id: int, entry_id: int, payload: dict) -> KnowledgeEntry:
    entry = _get_entry(user_id, entry_id)
    if "title" in payload:
        title = (payload.get("title") or "").strip()
        if not title:
            raise AppError(code=3101, message="missing_title_or_content", status_code=400)
        entry.title = title
    if "content" in payload:
        content = (payload.get("content") or "").strip()
        if not content:
            raise AppError(code=3101, message="missing_title_or_content", status_code=400)
        entry.content = content
    if "tags" in payload:
        entry.tags = payload.get("tags") or []
    if "links" in payload:
        entry.links = payload.get("links") or []
    if "topic_id" in payload:
        topic_id = payload.get("topic_id")
        if topic_id:
            _get_topic(user_id, topic_id)
        entry.topic_id = topic_id
    db.session.commit()
    return entry


def delete_entry(user_id: int, entry_id: int) -> None:
    entry = _get_entry(user_id, entry_id)
    db.session.delete(entry)
    db.session.commit()


def _get_topic(user_id: int, topic_id: int) -> Topic:
    topic = Topic.query.filter_by(id=topic_id, user_id=user_id).first()
    if not topic:
        abort(404)
    return topic


def _get_entry(user_id: int, entry_id: int) -> KnowledgeEntry:
    entry = KnowledgeEntry.query.filter_by(id=entry_id, user_id=user_id).first()
    if not entry:
        abort(404)
    return entry
