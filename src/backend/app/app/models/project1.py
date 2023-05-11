from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Table, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.project import project_annotationerror_table
if TYPE_CHECKING:
    from .user import User  # noqa: F401
    from .state import State
    from .file_format import FileFormat
    from .annotation_type import AnnotationType
    from .task import Task
    from .statistics import Statistics


class Project1(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)

    data_total_count = Column(Integer)
    data_sample_count = Column(Integer)

    dir_name = Column(String)

    company_info = Column(String)
    extended_properties = Column(String)

    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    owner_id = Column(Integer, ForeignKey("user.id"))
    state_id = Column(Integer, ForeignKey("state.id"), default=1)

    domain_id = Column(Integer, ForeignKey("domain.id"))

    owner = relationship("User", back_populates="projects")
    state = relationship("State", back_populates="projects")

    domain = relationship("Domain", back_populates="projects")

    tasks = relationship("Task", back_populates="project", cascade="all, delete")
    statistics = relationship("Statistics", back_populates="project")

    annotation_errors = relationship(
        "AnnotationError",
        secondary=lambda: project_annotationerror_table,
        backref="project1",
    )
