from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Group])
def read_groups(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve groups.
    """
    groups = crud.group.get_multi(db, skip=skip, limit=limit)
    return groups


@router.post("/", response_model=schemas.Group)
def create_group(
    *,
    db: Session = Depends(deps.get_db),
    group_in: schemas.GroupCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new group.
    """
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    group = crud.group.create(db=db, obj_in=group_in)
    return group


@router.put("/{id}", response_model=schemas.Group)
def update_group(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    group_in: schemas.GroupUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an group.
    """
    group = crud.group.get(db=db, id=id)
    if not group:
        raise HTTPException(status_code=404, detail="해당 권한을 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    group = crud.group.update(db=db, db_obj=group, obj_in=group_in)
    return group


@router.get("/{id}", response_model=schemas.Group)
def read_group(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get group by ID.
    """
    group = crud.group.get(db=db, id=id)
    if not group:
        raise HTTPException(status_code=404, detail="해당 권한을 찾을 수 없습니다.")
    return group


@router.delete("/{id}", response_model=schemas.Group)
def delete_group(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an group.
    """
    group = crud.group.get(db=db, id=id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    crud.group.remove(db=db, id=id)
    return group
