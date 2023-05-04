from typing import Optional

from pydantic import BaseModel


class StateCount(BaseModel):
    state_id: int
    count: int


class DomainCount(BaseModel):
    domain_id: int
    count: int


class GroupCount(BaseModel):
    group_id: int
    count: int


class AnnotationTypeCount(BaseModel):
    annotation_type_id: int
    count: int