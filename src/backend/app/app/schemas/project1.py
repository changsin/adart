import datetime
from typing import Optional, List

from pydantic import BaseModel

from .annotation_error import AnnotationError
from .annotation_class import AnnotationClass


# Shared properties
class Project1Base(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    data_total_count: Optional[int] = None
    data_sample_count: Optional[int] = None

    dir_name: Optional[str] = None

    owner_id: Optional[int] = None

    domain_id: Optional[int] = None

    company_info: Optional[str] = None
    extended_properties: Optional[str] = None


# Properties to receive on item creation
class Project1Create(Project1Base):
    name: str
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class Project1CreateTotal(Project1Base):
    name: str
    annotation_errors: List[int]


# Properties to receive on item update
class Project1Update(Project1Base):
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class Project1UpdateTotal(Project1Base):
    name: Optional[str]
    annotation_errors: Optional[List[int]]


# Properties shared by models stored in DB
class Project1InDBBase(Project1Base):
    id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Project1(Project1InDBBase):
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class Project1Summary(Project1InDBBase):
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    task_done_count: Optional[int]
    task_total_count: Optional[int]


class Project1Detail(Project1InDBBase):
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    annotation_errors: Optional[List[int]]
    task_done_count: Optional[int]
    task_total_count: Optional[int]


class Project1WithCount(BaseModel):
    num_count: Optional[int]
    projects: List[Project1Summary]


class AnnotatorWithCount(BaseModel):
    annotator_count: Optional[int]
    reviewer_count: Optional[int]
    # projects: List[Project]


# Properties properties stored in DB
class Project1InDB(Project1InDBBase):
    pass
