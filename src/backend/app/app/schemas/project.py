import datetime
from typing import Optional, List

from pydantic import BaseModel

from .annotation_error import AnnotationError
from .annotation_class import AnnotationClass


# Shared properties
class ProjectBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    dataset_name: Optional[str] = None
    total_count: Optional[int] = None
    sample_count: Optional[int] = None
    per_task_count: Optional[int] = None
    dir_name: Optional[str] = None
    owner_id: Optional[int] = None
    file_format_id: Optional[int] = None
    annotation_type_id: Optional[int] = None
    domain_id: Optional[int] = None
    state_id: Optional[int] = None
    customer_name: Optional[str] = None
    customer_company: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None


# Properties to receive on item creation
class ProjectCreate(ProjectBase):
    name: str
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class ProjectCreateTotal(ProjectBase):
    name: str
    annotation_errors: List[int]
    annotation_classes: str


# Properties to receive on item update
class ProjectUpdate(ProjectBase):
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class ProjectUpdateTotal(ProjectBase):
    name: Optional[str]
    annotation_errors: Optional[List[int]]
    annotation_classes: Optional[str]


# Properties shared by models stored in DB
class ProjectInDBBase(ProjectBase):
    id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Project(ProjectInDBBase):
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]


class ProjectSummary(ProjectInDBBase):
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    task_done_count: Optional[int]
    task_total_count: Optional[int]


class ProjectDetail(ProjectInDBBase):
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    annotation_errors: Optional[List[int]]
    annotation_classes: Optional[str]
    task_done_count: Optional[int]
    task_total_count: Optional[int]


class ProjectsWithCount(BaseModel):
    num_count: Optional[int]
    projects: List[ProjectSummary]


class AnnotatorWithCount(BaseModel):
    annotator_count: Optional[int]
    reviewer_count: Optional[int]
    # projects: List[Project]


# Properties properties stored in DB
class ProjectInDB(ProjectInDBBase):
    pass
