from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.AnnotationError])
def read_annotation_errors(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve annotation_errors.
    """
    annotation_errors = crud.annotation_error.get_multi(db, skip=skip, limit=limit)
    return annotation_errors


@router.post("/", response_model=schemas.AnnotationError)
def create_annotation_error(
    *,
    db: Session = Depends(deps.get_db),
    annotation_error_in: schemas.AnnotationErrorCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new annotation_error.
    """
    if crud.annotation_error.get_by_code(db, code=annotation_error_in.code):
        raise HTTPException(status_code=400, detail="오류코드가 이미 존재합니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")

    annotation_error = crud.annotation_error.create(db=db, obj_in=annotation_error_in)
    return annotation_error


@router.put("/{id}", response_model=schemas.AnnotationError)
def update_annotation_error(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    annotation_error_in: schemas.AnnotationErrorUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an annotation_error.
    """
    annotation_error = crud.annotation_error.get(db=db, id=id)
    if not annotation_error:
        raise HTTPException(status_code=404, detail="검증 오류를 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    annotation_error = crud.annotation_error.update(
        db=db, db_obj=annotation_error, obj_in=annotation_error_in
    )
    return annotation_error


@router.get("/{id}", response_model=schemas.AnnotationError)
def read_annotation_error(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get annotation_error by ID.
    """
    annotation_error = crud.annotation_error.get(db=db, id=id)
    if not annotation_error:
        raise HTTPException(status_code=404, detail="검증 오류를 찾을 수 없습니다.")
    return annotation_error


@router.delete("/{id}", response_model=schemas.AnnotationError)
def delete_annotation_error(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an annotation_error.
    """
    annotation_error = crud.annotation_error.get(db=db, id=id)
    if not annotation_error:
        raise HTTPException(status_code=404, detail="검증 오류를 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    if crud.project.exist_error_id(db=db, id=id):
        raise HTTPException(status_code=400, detail="검증 오류가 작업에 존재합니다.")
    crud.annotation_error.remove(db=db, id=id)
    return annotation_error
