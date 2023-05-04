from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.State])
def read_states(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve states.
    """
    states = crud.state.get_multi(db, skip=skip, limit=limit)
    return states


@router.post("/", response_model=schemas.State)
def create_state(
    *,
    db: Session = Depends(deps.get_db),
    state_in: schemas.StateCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new state.
    """
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    state = crud.state.create(db=db, obj_in=state_in)
    return state


@router.put("/{id}", response_model=schemas.State)
def update_state(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    state_in: schemas.StateUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an state.
    """
    state = crud.state.get(db=db, id=id)
    if not state:
        raise HTTPException(status_code=404, detail="해당 작업 상태를 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    state = crud.state.update(db=db, db_obj=state, obj_in=state_in)
    return state


@router.get("/{id}", response_model=schemas.State)
def read_state(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get state by ID.
    """
    state = crud.state.get(db=db, id=id)
    if not state:
        raise HTTPException(status_code=404, detail="해당 작업 상태를 찾을 수 없습니다.")
    return state


@router.delete("/{id}", response_model=schemas.State)
def delete_state(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an state.
    """
    state = crud.state.get(db=db, id=id)
    if not state:
        raise HTTPException(status_code=404, detail="해당 작업 상태를 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    crud.state.remove(db=db, id=id)
    return state
