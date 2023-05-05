import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class AnnotationTypeBase(BaseModel):
    name: Optional[str] = None


# Properties to receive on item creation
class AnnotationTypeCreate(AnnotationTypeBase):
    name: str


# Properties to receive on item update
class AnnotationTypeUpdate(AnnotationTypeBase):
    pass


# Properties shared by models stored in DB
class AnnotationTypeInDBBase(AnnotationTypeBase):
    id: int
    name: str

    class Config:
        orm_mode = True


# Properties to return to client
class AnnotationType(AnnotationTypeInDBBase):
    pass


# Properties properties stored in DB
class AnnotationTypeInDB(AnnotationTypeInDBBase):
    pass
