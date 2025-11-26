from datetime import datetime, date

from backend.extensions import db


class StudyLog(db.Model):
    __tablename__ = "study_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    entry_id = db.Column(db.Integer, db.ForeignKey("knowledge_entries.id"), nullable=False, index=True)
    note = db.Column(db.Text, nullable=True)
    logged_at = db.Column(db.Date, default=date.today, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "entry_id": self.entry_id,
            "note": self.note,
            "logged_at": self.logged_at.isoformat(),
            "created_at": self.created_at.isoformat(),
        }
