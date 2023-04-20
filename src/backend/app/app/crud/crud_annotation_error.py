from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.project import AnnotationError
from app.schemas.annotation_error import AnnotationErrorCreate, AnnotationErrorUpdate


class CRUDAnnotationError(CRUDBase[AnnotationError, AnnotationErrorCreate, AnnotationErrorUpdate]):
    def get_by_code(self, db: Session, *, code: str) -> Optional[AnnotationError]:
        return db.query(AnnotationError).filter(AnnotationError.code == code).first()


annotation_error = CRUDAnnotationError(AnnotationError)
