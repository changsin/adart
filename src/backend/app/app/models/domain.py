from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .project import Project 
    from .project1 import Project1


class Domain(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)
    description = Column(String)

    projects = relationship("Project", back_populates="domain")
    projects1 = relationship("Project1", back_populates="domain")
