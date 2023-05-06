from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .project import Project 


class Domain(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)
    description = Column(String)

    projects = relationship("Project", back_populates="domain")