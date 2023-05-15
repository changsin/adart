from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401
    from .project import Project
    from .project1 import Project1
    from .state import State


class Task(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    count = Column(Integer)
    anno_file_name = Column(String)

    annotator_id = Column(Integer, ForeignKey("user.id"))
    reviewer_id = Column(Integer, ForeignKey("user.id"))
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"))
    project1_id = Column(Integer, ForeignKey("project1.id", ondelete="CASCADE"))
    state_id = Column(Integer, ForeignKey("state.id"))

    annotator = relationship("User", backref="annotator", uselist=False, foreign_keys=[annotator_id])
    reviewer = relationship("User", backref="reviewer", uselist=False, foreign_keys=[reviewer_id])
    project = relationship("Project", back_populates="tasks")
    project1 = relationship("Project1", back_populates="tasks")
    state = relationship("State", back_populates="tasks")
