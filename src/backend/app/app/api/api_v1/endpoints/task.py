from datetime import datetime
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Task])
def read_tasks(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve tasks.
    """
    tasks = crud.task.get_multi(db, skip=skip, limit=limit)
    return tasks


@router.post("/", response_model=schemas.Task)
def create_task(
    *,
    db: Session = Depends(deps.get_db),
    task_in: schemas.TaskCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new task.
    """
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    task = crud.task.create(db=db, obj_in=task_in)
    return task


@router.put("/{id}", response_model=schemas.Task)
def update_task(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    task_in: schemas.TaskUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an task.
    """
    task = crud.task.get(db=db, id=id)
    none_count = 0
    for k in task_in.__dict__.keys():
        if task_in.__dict__[k] == None:
            none_count += 1
    if not task:
        raise HTTPException(status_code=404, detail="해당 작업을 찾을 수 없습니다.")
    if not (
        crud.user.is_admin(current_user)
        or (none_count == 6 and task_in.state_id is not None)
    ):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    if task_in.state_id == 4:
        task_in.reviewer_id = current_user.id
        task = crud.task.update(db=db, db_obj=task, obj_in=task_in)
        project = crud.project.get(db=db, id=task.project_id)
        if (
            crud.task.get_not_done_count_by_project(db=db, project_id=task.project_id)
            == 0
        ):
            project_in = schemas.ProjectUpdate(updated_at=datetime.now(), state_id=4)
        else:
            project_in = schemas.ProjectUpdate(updated_at=datetime.now())
        crud.project.update(db=db, db_obj=project, obj_in=project_in)
    else:
        task = crud.task.update(db=db, db_obj=task, obj_in=task_in)

    return task


@router.get("/{id}", response_model=schemas.Task)
def read_task(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get task by ID.
    """
    task = crud.task.get(db=db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="해당 작업을 찾을 수 없습니다.")
    return task


# @router.get("/project/{id}", response_model=List[schemas.TaskOuterjoinUserState])
@router.get("/project/{id}", response_model=schemas.TasksOuterjoinUserStateWithCount)
def read_tasks_by_project(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    skip: int = 0,
    limit: int = 100,
    name: str = None,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get task by Project ID.
    """
    if not crud.user.is_user(current_user):
        count, tasks = crud.task.get_multi_by_project(
            db, project_id=id, name=name, skip=skip, limit=limit
        )
    else:
        count, tasks = crud.task.get_multi_by_project(
            db,
            project_id=id,
            annotator_id=current_user.id,
            name=name,
            skip=skip,
            limit=limit,
        )
    payloads = schemas.TasksOuterjoinUserStateWithCount(num_count=count, tasks=tasks)
    return payloads


@router.delete("/{id}", response_model=schemas.Task)
def delete_task(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an task.
    """
    task = crud.task.get(db=db, id=id)
    if not task:
        raise HTTPException(status_code=404, detail="해당 작업을 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    crud.task.remove(db=db, id=id)
    return task
