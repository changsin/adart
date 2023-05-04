import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class AnnotationClassBase(BaseModel):
    name: Optional[str] = None


# Properties to receive on item creation
class AnnotationClassCreate(AnnotationClassBase):
    name: str


# Properties to receive on item update
class AnnotationClassUpdate(AnnotationClassBase):
    pass


# Properties shared by models stored in DB
class AnnotationClassInDBBase(AnnotationClassBase):
    id: int
    name: str

    class Config:
        orm_mode = True


# Properties to return to client
class AnnotationClass(AnnotationClassInDBBase):
    pass


# Properties properties stored in DB
class AnnotationClassInDB(AnnotationClassInDBBase):
    pass
