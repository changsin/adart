from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Domain])
def read_domains(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve domains.
    """
    domains = crud.domain.get_multi(db, skip=skip, limit=limit)
    return domains


@router.post("/", response_model=schemas.Domain)
def create_domain(
    *,
    db: Session = Depends(deps.get_db),
    domain_in: schemas.DomainCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new domain.
    """
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    domain = crud.domain.create(db=db, obj_in=domain_in)
    return domain


@router.put("/{id}", response_model=schemas.Domain)
def update_domain(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    domain_in: schemas.DomainUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an domain.
    """
    domain = crud.domain.get(db=db, id=id)
    if not domain:
        raise HTTPException(status_code=404, detail="도메인을 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    domain = crud.domain.update(db=db, db_obj=domain, obj_in=domain_in)
    return domain


@router.get("/{id}", response_model=schemas.Domain)
def read_domain(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get domain by ID.
    """
    domain = crud.domain.get(db=db, id=id)
    if not domain:
        raise HTTPException(status_code=404, detail="도메인을 찾을 수 없습니다.")
    return domain


@router.delete("/{id}", response_model=schemas.Domain)
def delete_domain(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an domain.
    """
    domain = crud.domain.get(db=db, id=id)
    if not domain:
        raise HTTPException(status_code=404, detail="도메인을 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    if crud.project.get_by_domain_id(db=db, domain_id=id):
        raise HTTPException(status_code=400, detail="도메인이 작업에 존재합니다.")
    crud.domain.remove(db=db, id=id)
    return domain
