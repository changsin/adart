from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.celery_app import celery_app
from app.utils import send_test_email, send_new_task_email

router = APIRouter()


@router.post("/test-celery/", response_model=schemas.Msg, status_code=201)
def test_celery(
    msg: schemas.Msg,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test Celery worker.
    """
    celery_app.send_task("app.worker.test_celery", args=[msg.msg])
    return {"msg": "Word received"}


@router.post("/test-email/", response_model=schemas.Msg, status_code=201)
def test_email(
    email_to: EmailStr,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test emails.
    """
    send_test_email(email_to=email_to)
    return {"msg": "Test email sent"}


@router.post("/task_assign_email/", response_model=schemas.Msg, status_code=201)
def task_assign_email(
    user_id: int,
    project_id: int,
    task_list: schemas.task.TaskIdList,
    current_user: models.User = Depends(deps.get_current_active_admin),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    send task assign email to user.
    """
    user = crud.user.get(db=db, id=user_id)
    email_to = user.email
    project_name = crud.project.get(db=db, id=project_id).name

    task_list = task_list.task_id_list.split(",")
    if len(task_list) == 0:
        raise HTTPException(status_code=404, detail="할당된 작업이 없습니다.")
    first_task_name = crud.task.get(db=db, id=int(task_list[0])).name

    if len(task_list) == 1:
        task_all = f"{first_task_name}"
    else:
        task_all = f"{first_task_name} 외 {len(task_list) - 1}건"

    if not user:
        raise HTTPException(status_code=404, detail="해당 사용자를 찾을 수 없습니다.")
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=400, detail="권한이 없습니다.")

    send_new_task_email(email_to=email_to, project_name=project_name, task_name=task_all)
    return {"msg": "New task email sent"}
