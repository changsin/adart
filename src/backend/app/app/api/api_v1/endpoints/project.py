import os
from datetime import datetime
from typing import Any, List

import requests
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app import crud, models, schemas
from app.api import deps

router = APIRouter()
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

# @router.get("/", response_model=List[schemas.Project])
@router.get("/", response_model=schemas.ProjectsWithCount)
def read_projects(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    is_dir_null: bool = False,
    name: str = "",
    date_start: str = "1000-01-01",
    date_end: str = "9999-12-30",
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve projects.
    """
    if crud.user.is_admin(current_user) or crud.user.is_reviewer(current_user):
        count, projects = crud.project.get_multi_order_by_created_at(
            db,
            name=name,
            is_dir_null=is_dir_null,
            skip=skip,
            limit=limit,
            date_start=date_start,
            date_end=date_end,
        )
    elif crud.user.is_inspector(current_user):
        count, projects = crud.project.get_multi_by_email(
            db,
            is_dir_null=is_dir_null,
            current_user_email=current_user.email,
            name=name,
            skip=skip,
            limit=limit,
            date_start=date_start,
            date_end=date_end,
        )
    else:
        count, projects = crud.project.get_multi_by_task_owner(
            db=db,
            owner_id=current_user.id,
            name=name,
            skip=skip,
            limit=limit,
            date_start=date_start,
            date_end=date_end,
        )
    payloads = schemas.ProjectsWithCount(num_count=count, projects=projects)
    return payloads


@router.post("/", response_model=schemas.Project)
def create_project(
    *,
    db: Session = Depends(deps.get_db),
    project_total_in: schemas.ProjectCreateTotal,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new project and related cutomer, annotation_classes, annotation_errors.
    """
    project_in = schemas.ProjectCreate(**project_total_in.__dict__)
    time_now = datetime.now()
    project_in.created_at = time_now
    project_in.updated_at = time_now
    # project_in = schemas.ProjectCreate(
    #    name=project_total_in.name,
    #    description=project_total_in.description,
    #    total_count=project_total_in.total_count,
    #    sample_count=project_total_in.sample_count,
    #    per_task_count=project_total_in.per_task_count,
    #    dir_name=project_total_in.dir_name,
    #    created_at=time_now,
    #    updated_at=time_now,
    #    owner_id=project_total_in.owner_id,
    #    customer_name=project_total_in.customer_name,
    #    customer_company=project_total_in.customer_company,
    #    customer_email=project_total_in.customer_email,
    #    customer_phone=project_total_in.customer_phone,
    #    file_format_id=project_total_in.file_format_id,
    #    annotation_type_id=project_total_in.annotation_type_id
    # )
    # project = crud.project.create(db=db, obj_in=project_in)
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    annotation_error_data = []
    for i in project_total_in.annotation_errors:
        annotation_error = crud.annotation_error.get(db=db, id=i)
        annotation_error_data.append(annotation_error)

    annotation_class_data = []
    annotation_classes = [
        x.strip() for x in project_total_in.annotation_classes.split(",")
    ]
    for anno_class in annotation_classes:
        annotation_class = crud.annotation_class.get_by_name(db=db, name=anno_class)
        if not annotation_class:
            annotation_class = crud.annotation_class.create(
                db=db, obj_in=schemas.AnnotationClassCreate(name=anno_class)
            )
        annotation_class_data.append(annotation_class)

    project = crud.project.create_with_annotation_errors_and_classes(
        db=db,
        obj_in=project_in,
        anno_errors=annotation_error_data,
        anno_classes=annotation_class_data,
    )

    return project


@router.put("/{id}", response_model=schemas.Project)
def update_project(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    project_in: schemas.ProjectUpdateTotal,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an project.
    """
    project = crud.project.get(db=db, id=id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")

    annotation_error_data = []
    if project_in.annotation_errors is not None:
        for i in project_in.annotation_errors:
            annotation_error = crud.annotation_error.get(db=db, id=i)
            annotation_error_data.append(annotation_error)
    else:
        annotation_error_data = None

    annotation_class_data = []
    if project_in.annotation_classes is not None:
        annotation_classes = [x.strip() for x in project_in.annotation_classes.split(",")]
        for anno_class in annotation_classes:
            annotation_class = crud.annotation_class.get_by_name(db=db, name=anno_class)
            if not annotation_class:
                annotation_class = crud.annotation_class.create(
                    db=db, obj_in=schemas.AnnotationClassCreate(name=anno_class)
                )
            annotation_class_data.append(annotation_class)
    else:
        annotation_class_data = None

    project = crud.project.update_with_annotation_errors_and_classes(
        db=db,
        db_obj=project,
        obj_in=project_in,
        anno_errors=annotation_error_data,
        anno_classes=annotation_class_data,
    )
    return project


@router.get("/{id}", response_model=schemas.ProjectDetail)
def read_project(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get project by ID.
    """
    project = crud.project.get_with_string_classes(db=db, id=id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    return project


@router.delete("/{id}", response_model=schemas.Project)
def delete_project(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    token: str = Depends(reusable_oauth2),
) -> Any:
    """
    Delete an project.
    """
    project = crud.project.get(db=db, id=id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")

    if project.dir_name is not None:
        requests.post(
            settings.FILE_SERVER_HOST + "/rpc",
            data=json.dumps({"args": [project.dir_name], "call": "rm"}),
            headers={"Authorization": token},
        )
    # count, tasks = crud.task.get_multi_by_project(db=db, project_id=id)
    # for t in tasks:
    #    task = crud.task.remove(db=db, id=t.id)
    crud.project.remove(db=db, id=id)
    return project


@router.get("/create_tasks/{id}", response_model=schemas.Project)
def create_tasks(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    token: str = Depends(reusable_oauth2),
) -> Any:
    """
    Create tasks of the project.
    """
    project = crud.project.get(db=db, id=id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    # Get task directory from file server.
    # TODO: exception handling when server or folder doesn't exists.
    # TODO:  solve [Errno 110] Connection timed out
    tasks = []
    files_in_project = requests.post(
        settings.FILE_SERVER_HOST + "/rpc",
        data=json.dumps({"args": [project.dir_name], "call": "ls"}),
        headers={"Authorization": token},
    ).json()["listdir"]
    for f in files_in_project:
        if f[0] == "d":
            tasks.append(f[1])
    tasks = sorted(tasks)

    # Make dirtory for modified annotation file in task directory and copy original annotation file.
    for task in tasks:
        anno_file_name = None
        files_in_task = requests.post(
            settings.FILE_SERVER_HOST + "/rpc",
            data=json.dumps(
                {"args": [os.path.join(project.dir_name, task)], "call": "ls"}
            ),
            headers={"Authorization": token},
        ).json()["listdir"]
        requests.post(
            settings.FILE_SERVER_HOST + "/rpc",
            data=json.dumps(
                {
                    "args": [os.path.join(project.dir_name, task, "mod_anno")],
                    "call": "mkdirp",
                }
            ),
            headers={"Authorization": token},
        )

        for i, f in enumerate(files_in_task):
            if f[0] == "d":
                files_in_task.pop(i)
            elif (
                f[1].endswith(".json")
                or f[1].endswith(".xml")
                or f[1].endswith(".csv")
                or f[1].endswith(".txt")
            ):
                requests.post(
                    settings.FILE_SERVER_HOST + "/rpc",
                    data=json.dumps(
                        {
                            "args": [
                                os.path.join(project.dir_name, task, f[1]),
                                os.path.join(project.dir_name, task, "mod_anno", f[1]),
                            ],
                            "call": "cp",
                        }
                    ),
                    headers={"Authorization": token},
                )
                files_in_task.pop(i)
                anno_file_name = f[1]

        task_in = schemas.TaskCreate(
            name=task,
            count=len(files_in_task),
            anno_file_name=anno_file_name,
            project_id=project.id,
            state_id=1,
        )
        crud.task.create(db=db, obj_in=task_in)

    return project


@router.get("/annotator_count/{id}", response_model=schemas.AnnotatorWithCount)
def get_distinct_annotator_count(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new all tasks of the project.
    """
    project = crud.project.get(db=db, id=id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")
    count = crud.project.get_distinct_annotator_count(db=db, project_id=id)

    payloads = schemas.AnnotatorWithCount(
        annotator_count=count["annotator_count"],
        reviewer_count=count["reviewer_count"],
    )
    return payloads
