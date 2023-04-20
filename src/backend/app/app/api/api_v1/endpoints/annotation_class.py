from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.AnnotationClass])
def read_annotation_classs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve annotation_classs.
    """
    annotation_classs = crud.annotation_class.get_multi(db, skip=skip, limit=limit)
    return annotation_classs


@router.post("/", response_model=schemas.AnnotationClass)
def create_annotation_class(
    *,
    db: Session = Depends(deps.get_db),
    annotation_class_in: schemas.AnnotationClassCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new annotation_class.
    """
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    annotation_class = crud.annotation_class.create(db=db, obj_in=annotation_class_in)
    return annotation_class


@router.put("/{id}", response_model=schemas.AnnotationClass)
def update_annotation_class(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    annotation_class_in: schemas.AnnotationClassUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an annotation_class.
    """
    annotation_class = crud.annotation_class.get(db=db, id=id)
    if not annotation_class:
        raise HTTPException(status_code=404, detail="어노테이션 클래스를 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    annotation_class = crud.annotation_class.update(
        db=db, db_obj=annotation_class, obj_in=annotation_class_in
    )
    return annotation_class


@router.get("/{id}", response_model=schemas.AnnotationClass)
def read_annotation_class(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get annotation_class by ID.
    """
    annotation_class = crud.annotation_class.get(db=db, id=id)
    if not annotation_class:
        raise HTTPException(status_code=404, detail="어노테이션 클래스를 찾을 수 없습니다.")
    return annotation_class


@router.delete("/{id}", response_model=schemas.AnnotationClass)
def delete_annotation_class(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an annotation_class.
    """
    annotation_class = crud.annotation_class.get(db=db, id=id)
    if not annotation_class:
        raise HTTPException(status_code=404, detail="어노테이션 클래스를 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    crud.annotation_class.remove(db=db, id=id)
    return annotation_class
