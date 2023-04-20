from typing import Optional

from pydantic import BaseModel


# Shared properties
class StateBase(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None


# Properties to receive on item creation
class StateCreate(StateBase):
    name: str
    code: str


# Properties to receive on item update
class StateUpdate(StateBase):
    pass


# Properties shared by models stored in DB
class StateInDBBase(StateBase):
    id: int
    name: str
    code: str

    class Config:
        orm_mode = True


# Properties to return to client
class State(StateInDBBase):
    pass


# Properties properties stored in DB
class StateInDB(StateInDBBase):
    pass
