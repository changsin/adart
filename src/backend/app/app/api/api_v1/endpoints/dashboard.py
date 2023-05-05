from datetime import datetime
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/project_state_count", response_model=List[schemas.StateCount])
def read_project_state_count(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve dashboards.
    """
    result = []
    counts = crud.project.get_state_count(db)

    for i in counts.keys():
        result.append(schemas.StateCount(
            state_id=i,
            count=counts[i]
        ))
    return result


@router.get("/project_domain_count", response_model=List[schemas.DomainCount])
def read_project_domain_count(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve dashboards.
    """
    result = []
    counts = crud.project.get_domain_count(db)

    for i in counts.keys():
        result.append(schemas.DomainCount(
            domain_id=i,
            count=counts[i]
        ))
    return result


@router.get("/user_group_count", response_model=List[schemas.GroupCount])
def read_user_group_count(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve dashboards.
    """
    result = []
    counts = crud.user.get_group_count(db)

    for i in counts.keys():
        result.append(schemas.GroupCount(
            group_id=i,
            count=counts[i]
        ))
    return result


@router.get("/project_annotype_count", response_model=List[schemas.AnnotationTypeCount])
def read_user_group_count(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve dashboards.
    """
    result = []
    counts = crud.project.get_annotation_type_count(db)

    for i in counts.keys():
        result.append(schemas.AnnotationTypeCount(
            annotation_type_id=i,
            count=counts[i]
        ))
    return result
