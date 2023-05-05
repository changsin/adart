from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, aliased

from app.crud.base import CRUDBase
from app.models.task import Task
from app.models.state import State
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskOuterjoinUserState


class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    def get_multi_by_project(
        self,
        db: Session,
        *,
        project_id: int,
        annotator_id: int = None,
        name: str = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TaskOuterjoinUserState]:
        return_data = []
        annotator = aliased(User)
        reviewer = aliased(User)

        if annotator_id is None:
            query_results = (
                db.query(self.model, annotator.full_name, State.name, reviewer.full_name)
                .outerjoin(annotator, Task.annotator_id == annotator.id)
                .outerjoin(State, Task.state_id == State.id)
                .outerjoin(reviewer, Task.reviewer_id == reviewer.id)
                .filter(Task.project_id == project_id)
            )
            if name is not None:
                search = "%{}%".format(name)
                query_results = query_results.filter(Task.name.like(search)).order_by(
                    self.model.name
                )
            else:
                query_results = query_results.order_by(self.model.name)
        else:
            query_results = (
                db.query(self.model, annotator.full_name, State.name, reviewer.full_name)
                .outerjoin(annotator, Task.annotator_id == annotator.id)
                .outerjoin(State, Task.state_id == State.id)
                .outerjoin(reviewer, Task.reviewer_id == reviewer.id)
                .filter(Task.project_id == project_id)
                .filter(Task.annotator_id == annotator_id)
            )
            if name is not None:
                search = "%{}%".format(name)
                query_results = query_results.filter(Task.name.like(search)).order_by(
                    self.model.name
                )
            else:
                query_results = query_results.order_by(self.model.name)
        # print(query_results)
        count = query_results.count()
        query_off_lim = query_results.offset(skip).limit(limit).all()
        # print(query_off_lim)
        for r in query_off_lim:
            t = TaskOuterjoinUserState(
                id=r[0].id,
                name=r[0].name,
                count=r[0].count,
                anno_file_name=r[0].anno_file_name,
                annotator_id=r[0].annotator_id,
                annotator_fullname=r[1],
                reviewer_id=r[0].reviewer_id,
                reviewer_fullname=r[3],
                project_id=r[0].project_id,
                state_id=r[0].state_id,
                state_name=r[2],
            )
            return_data.append(t)
        return count, return_data

    def get_not_done_count_by_project(
        self, db: Session, *, project_id: int
    ) -> List[TaskOuterjoinUserState]:
        query_results = db.query(self.model).filter(
            Task.project_id == project_id, Task.state_id != 4
        )
        count = query_results.count()
        return count

    def get_by_user(self, db: Session, *, user_id: str) -> Optional[Task]:
        annotator_exist = bool(
            db.query(Task).filter(Task.annotator_id == user_id).first()
        )
        reviewer_exist = bool(db.query(Task).filter(Task.reviewer_id == user_id).first())
        return annotator_exist or reviewer_exist


task = CRUDTask(Task)
