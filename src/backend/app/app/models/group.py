from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user import User


class Group(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    is_admin = Column(Boolean(), default=False)
    is_user = Column(Boolean(), default=False)
    is_reviewer = Column(Boolean(), default=False)
    read_only = Column(Boolean(), default=False)

    users = relationship("User", back_populates="group")
