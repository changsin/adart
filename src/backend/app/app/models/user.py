from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .group import Group
    from .item import Item  # noqa: F401
    from .project import Project
    from .project1 import Project1
    from .task import Task


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    phone = Column(String)
    description = Column(String)

    group_id = Column(Integer, ForeignKey("group.id"))
    group = relationship("Group", back_populates="users")

    items = relationship("Item", back_populates="owner")
    projects = relationship("Project", back_populates="owner")
    projects1 = relationship("Project1", back_populates="owner")
