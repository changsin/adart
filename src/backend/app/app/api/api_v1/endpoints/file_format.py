from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.FileFormat])
def read_file_formats(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve file_formats.
    """
    file_formats = crud.file_format.get_multi(db, skip=skip, limit=limit)
    return file_formats


@router.post("/", response_model=schemas.FileFormat)
def create_file_format(
    *,
    db: Session = Depends(deps.get_db),
    file_format_in: schemas.FileFormatCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new file_format.
    """
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    file_format = crud.file_format.create(db=db, obj_in=file_format_in)
    return file_format


@router.put("/{id}", response_model=schemas.FileFormat)
def update_file_format(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    file_format_in: schemas.FileFormatUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an file_format.
    """
    file_format = crud.file_format.get(db=db, id=id)
    if not file_format:
        raise HTTPException(status_code=404, detail="파일 포맷을 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    file_format = crud.file_format.update(
        db=db, db_obj=file_format, obj_in=file_format_in
    )
    return file_format


@router.get("/{id}", response_model=schemas.FileFormat)
def read_file_format(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get file_format by ID.
    """
    file_format = crud.file_format.get(db=db, id=id)
    if not file_format:
        raise HTTPException(status_code=404, detail="파일 포맷을 찾을 수 없습니다.")
    return file_format


@router.delete("/{id}", response_model=schemas.FileFormat)
def delete_file_format(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an file_format.
    """
    file_format = crud.file_format.get(db=db, id=id)
    if not file_format:
        raise HTTPException(status_code=404, detail="파일 포맷을 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    crud.file_format.remove(db=db, id=id)
    return file_format
