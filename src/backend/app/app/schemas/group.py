import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class GroupBase(BaseModel):
    name: Optional[str] = None
    is_admin: Optional[bool] = False
    is_user: Optional[bool] = False
    is_reviewer: Optional[bool] = False
    read_only: Optional[bool] = False


# Properties to receive on item creation
class GroupCreate(GroupBase):
    name: str


# Properties to receive on item update
class GroupUpdate(GroupBase):
    pass


# Properties shared by models stored in DB
class GroupInDBBase(GroupBase):
    id: int
    name: str

    class Config:
        orm_mode = True


# Properties to return to client
class Group(GroupInDBBase):
    pass


# Properties properties stored in DB
class GroupInDB(GroupInDBBase):
    pass
