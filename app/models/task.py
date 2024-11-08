from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from ..db import db
from typing import Optional
from datetime import datetime
from typing import TYPE_CHECKING
if TYPE_CHECKING: 
    from .goal import Goal

class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str]
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    goal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("goal.id"))
    goal: Mapped[Optional["Goal"]] = relationship(back_populates="tasks")
    
    def to_dict(self):
        return {
            "id":self.id, 
            "title":self.title,
            "description":self.description,
            "is_complete":self.completed_at is not None,
            "goal":self.goal.title if self.goal else None
        }

    @classmethod
    def from_dict(cls, task_data):
        completed_at = datetime if task_data.get("is_complete", False) else None
        return cls(
            title=task_data["title"],
            description=task_data["description"],
            completed_at=completed_at,
            goal_id=task_data.get("goal_id", None)
        )
    
    def mark_complete(self):
        self.completed_at = datetime.now()

    def mark_incomplete(self):
        self.completed_at = None