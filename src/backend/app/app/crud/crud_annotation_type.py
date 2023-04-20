from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.annotation_type import AnnotationType
from app.schemas.annotation_type import AnnotationTypeCreate, AnnotationTypeUpdate


class CRUDAnnotationType(CRUDBase[AnnotationType, AnnotationTypeCreate, AnnotationTypeUpdate]):
    pass


annotation_type = CRUDAnnotationType(AnnotationType)
