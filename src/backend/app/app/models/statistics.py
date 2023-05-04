from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .project import Project


class Statistics(Base):
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    verbose = Column(String)
    file_path = Column(String)
    created_at = Column(DateTime)

    project_id = Column(Integer, ForeignKey("project.id"))

    project = relationship("Project", back_populates="statistics")
