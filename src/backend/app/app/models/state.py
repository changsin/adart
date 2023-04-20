from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .task import Task
    from .project import Project


class State(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)

    tasks = relationship("Task", back_populates="state")
    projects = relationship("Project", back_populates="state")
