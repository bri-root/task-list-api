from sqlalchemy.orm import Mapped, mapped_column
from ..db import db
from typing import Optional
from datetime import datetime


class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    def to_dict(self):
        return {
            "id":self.id, 
            "title":self.title,
            "description":self.description,
            "is_complete":self.completed_at is not None
        }

    @classmethod
    def from_dict(cls, task_data):
        completed_at = datetime if task_data.get("is_complete", False) else None
        return cls(
            title=task_data["title"],
            description=task_data["description"],
            completed_at=completed_at
        )
    
    def mark_complete(self):
        self.completed_at = datetime.now()

    def mark_incomplete(self):
        self.completed_at = None