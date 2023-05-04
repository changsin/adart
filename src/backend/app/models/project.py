from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Table, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401
    from .state import State
    from .file_format import FileFormat
    from .annotation_type import AnnotationType
    from .task import Task
    from .statistics import Statistics


class Project(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    dataset_name = Column(String)
    total_count = Column(Integer)
    sample_count = Column(Integer)
    per_task_count = Column(Integer)
    dir_name = Column(String)
    customer_name = Column(String)
    customer_company = Column(String)
    customer_email = Column(String)
    customer_phone = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    owner_id = Column(Integer, ForeignKey("user.id"))
    state_id = Column(Integer, ForeignKey("state.id"), default=1)
    file_format_id = Column(Integer, ForeignKey("fileformat.id"))
    annotation_type_id = Column(Integer, ForeignKey("annotationtype.id"))
    domain_id = Column(Integer, ForeignKey("domain.id"))

    owner = relationship("User", back_populates="projects")
    state = relationship("State", back_populates="projects")
    file_format = relationship("FileFormat", back_populates="projects")
    annotation_type = relationship("AnnotationType", back_populates="projects")
    domain = relationship("Domain", back_populates="projects")

    tasks = relationship("Task", back_populates="project", cascade="all, delete")
    statistics = relationship("Statistics", back_populates="project")

    annotation_classes = relationship(
        "AnnotationClass",
        secondary=lambda: project_annotationclass_table,
        backref="projects",
    )
    annotation_errors = relationship(
        "AnnotationError",
        secondary=lambda: project_annotationerror_table,
        backref="projects",
    )


class AnnotationClass(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)


class AnnotationError(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)
    description = Column(String)
    is_default = Column(Boolean(), default=False)


project_annotationclass_table = Table(
    "projectannotationclass",
    Base.metadata,
    Column("project_id", ForeignKey("project.id", ondelete="CASCADE"), primary_key=True),
    Column("annotationclass_id", ForeignKey("annotationclass.id"), primary_key=True),
)
project_annotationerror_table = Table(
    "projectannotationerror",
    Base.metadata,
    Column("project_id", ForeignKey("project.id", ondelete="CASCADE"), primary_key=True),
    Column("annotationerror_id", ForeignKey("annotationerror.id"), primary_key=True),
)
