from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.AnnotationType])
def read_annotation_types(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve annotation_types.
    """
    annotation_types = crud.annotation_type.get_multi(db, skip=skip, limit=limit)
    return annotation_types


@router.post("/", response_model=schemas.AnnotationType)
def create_annotation_type(
    *,
    db: Session = Depends(deps.get_db),
    annotation_type_in: schemas.AnnotationTypeCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new annotation_type.
    """
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    annotation_type = crud.annotation_type.create(db=db, obj_in=annotation_type_in)
    return annotation_type


@router.put("/{id}", response_model=schemas.AnnotationType)
def update_annotation_type(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    annotation_type_in: schemas.AnnotationTypeUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an annotation_type.
    """
    annotation_type = crud.annotation_type.get(db=db, id=id)
    if not annotation_type:
        raise HTTPException(status_code=404, detail="어노테이션 타입을 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    annotation_type = crud.annotation_type.update(
        db=db, db_obj=annotation_type, obj_in=annotation_type_in
    )
    return annotation_type


@router.get("/{id}", response_model=schemas.AnnotationType)
def read_annotation_type(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get annotation_type by ID.
    """
    annotation_type = crud.annotation_type.get(db=db, id=id)
    if not annotation_type:
        raise HTTPException(status_code=404, detail="어노테이션 타입을 찾을 수 없습니다.")
    return annotation_type


@router.delete("/{id}", response_model=schemas.AnnotationType)
def delete_annotation_type(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an annotation_type.
    """
    annotation_type = crud.annotation_type.get(db=db, id=id)
    if not annotation_type:
        raise HTTPException(status_code=404, detail="어노테이션 타입을 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    crud.annotation_type.remove(db=db, id=id)
    return annotation_type
