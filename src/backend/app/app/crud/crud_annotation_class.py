from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.project import AnnotationClass
from app.schemas.annotation_class import AnnotationClassCreate, AnnotationClassUpdate


class CRUDAnnotationClass(CRUDBase[AnnotationClass, AnnotationClassCreate, AnnotationClassUpdate]):
    def get_by_name(
        self, db: Session, *, name: str
    ) -> AnnotationClass:
        return db.query(self.model).filter(self.model.name == name).first()


annotation_class = CRUDAnnotationClass(AnnotationClass)
