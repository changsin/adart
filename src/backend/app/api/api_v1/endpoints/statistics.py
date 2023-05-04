from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Statistics])
def read_statistics(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve statisticss.
    """
    statisticss = crud.statistics.get_multi(db, skip=skip, limit=limit)
    return statisticss


@router.post("/", response_model=schemas.Statistics)
def create_statistics(
    *,
    db: Session = Depends(deps.get_db),
    statistics_in: schemas.StatisticsCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new statistics.
    """
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    statistics = crud.statistics.create(db=db, obj_in=statistics_in)
    return statistics


@router.put("/{id}", response_model=schemas.Statistics)
def update_statistics(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    statistics_in: schemas.StatisticsUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an statistics.
    """
    statistics = crud.statistics.get(db=db, id=id)
    if not statistics:
        raise HTTPException(status_code=404, detail="통계를 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    statistics = crud.statistics.update(db=db, db_obj=statistics, obj_in=statistics_in)
    return statistics


@router.get("/{id}", response_model=schemas.Statistics)
def read_statistics(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get statistics by ID.
    """
    statistics = crud.statistics.get(db=db, id=id)
    if not statistics:
        raise HTTPException(status_code=404, detail="통계를 찾을 수 없습니다.")
    return statistics


@router.delete("/{id}", response_model=schemas.Statistics)
def delete_statistics(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an statistics.
    """
    statistics = crud.statistics.get(db=db, id=id)
    if not statistics:
        raise HTTPException(status_code=404, detail="통계를 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    crud.statistics.remove(db=db, id=id)
    return statistics
