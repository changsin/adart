import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class AnnotationErrorBase(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    is_default: bool = False


# Properties to receive on item creation
class AnnotationErrorCreate(AnnotationErrorBase):
    name: str
    code: str


# Properties to receive on item update
class AnnotationErrorUpdate(AnnotationErrorBase):
    pass


# Properties shared by models stored in DB
class AnnotationErrorInDBBase(AnnotationErrorBase):
    id: int
    name: str
    code: str

    class Config:
        orm_mode = True


# Properties to return to client
class AnnotationError(AnnotationErrorInDBBase):
    pass


# Properties properties stored in DB
class AnnotationErrorInDB(AnnotationErrorInDBBase):
    pass
