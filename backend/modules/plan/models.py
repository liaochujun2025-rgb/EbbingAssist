from datetime import datetime

from backend.extensions import db


class Plan(db.Model):
    __tablename__ = "plans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    goal = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(16), default="medium")
    tags = db.Column(db.JSON, default=list)
    status = db.Column(db.String(32), default="not_started")
    progress = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = db.relationship("Task", backref="plan", cascade="all, delete-orphan", lazy="select")


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("plans.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    desc = db.Column(db.Text, nullable=True)
    estimate_minutes = db.Column(db.Integer, nullable=True)
    priority = db.Column(db.String(16), default="medium")
    status = db.Column(db.String(32), default="todo")
    due_date = db.Column(db.Date, nullable=True)
    tags = db.Column(db.JSON, default=list)
    order_no = db.Column(db.Integer, default=0)
    focus_minutes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "plan_id": self.plan_id,
            "title": self.title,
            "desc": self.desc,
            "estimate_minutes": self.estimate_minutes,
            "priority": self.priority,
            "status": self.status,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "tags": self.tags or [],
            "order_no": self.order_no,
            "focus_minutes": self.focus_minutes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
