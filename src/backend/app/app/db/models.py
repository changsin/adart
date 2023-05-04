from typing import Any
from datetime import datetime

from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

# @as_declarative()
Base = declarative_base()


class UserModel(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    birth = Column(DateTime)
    created = Column(DateTime, default=datetime.utcnow)
