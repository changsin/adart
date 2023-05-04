import datetime
from typing import Any, List, Optional, Union, Dict

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, lazyload
from sqlalchemy import and_

from app.crud.base import CRUDBase
from app.models.project import Project
from app.models.task import Task
from app.models.state import State
from app.models.domain import Domain
from app.models.annotation_type import AnnotationType
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectUpdateTotal,
    ProjectDetail,
    ProjectSummary,
)


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    def get_multi_order_by_created_at(
        self,
        db: Session,
        *,
        is_dir_null: bool = False,
        name: str = "",
        skip: int = 0,
        limit: int = 100,
        date_start: None,
        date_end: None
    ) -> List[ProjectSummary]:
        if is_dir_null:
            query = (
                db.query(self.model)
                .filter(Project.dir_name == None)
                .order_by(self.model.created_at.desc())
            )
        else:
            name_search = "%{}%".format(name)
            date_end = (
                datetime.datetime.strptime(date_end, "%Y-%m-%d")
                + datetime.timedelta(days=1)
            ).strftime("%Y-%m-%d")
            query = (
                db.query(self.model)
                .filter(
                    and_(
                        Project.name.ilike(name_search),
                        Project.created_at >= date_start,
                        Project.created_at <= date_end,
                    )
                )
                .order_by(self.model.created_at.desc())
            )
        count = query.count()
        query_off_lim = query.offset(skip).limit(limit).all()

        outputs = []
        for q in query_off_lim:
            task_states = db.query(Task.state_id).filter(Task.project_id == q.id).all()
            count_done = 0
            for state in task_states:
                if state[0] == 4:
                    count_done += 1
            project_summary = ProjectSummary(**q.__dict__)
            project_summary.task_done_count = count_done
            project_summary.task_total_count = len(task_states)
            outputs.append(project_summary)

        return count, outputs

    def get_multi_by_task_owner(
        self,
        db: Session,
        *,
        owner_id: int,
        name: str = "",
        skip: int = 0,
        limit: int = 100,
        date_start: None,
        date_end: None
    ) -> List[Project]:
        name_search = "%{}%".format(name)
        date_end = (
            datetime.datetime.strptime(date_end, "%Y-%m-%d") + datetime.timedelta(days=1)
        ).strftime("%Y-%m-%d")
        project_ids = (
            db.query(Task.project_id)
            .filter(and_(Task.annotator_id == owner_id))
            .distinct()
            .all()
        )
        if len(project_ids) == 0:
            project_ids = [(None,)]

        query = (
            db.query(self.model)
            .filter(
                and_(
                    Project.id.in_(list(zip(*project_ids))[0]),
                    Project.name.ilike(name_search),
                    Project.created_at >= date_start,
                    Project.created_at <= date_end,
                )
            )
            .order_by(self.model.created_at.desc())
        )
        count = query.count()
        query_off_lim = query.offset(skip).limit(limit).all()

        outputs = []
        for q in query_off_lim:
            task_states = db.query(Task.state_id).filter(Task.project_id == q.id).all()
            count_done = 0
            for state in task_states:
                if state[0] == 4:
                    count_done += 1
            project_summary = ProjectSummary(**q.__dict__)
            project_summary.task_done_count = count_done
            project_summary.task_total_count = len(task_states)
            outputs.append(project_summary)

        return count, outputs

    def get_multi_by_email(
        self,
        db: Session,
        *,
        is_dir_null: bool = False,
        current_user_email: str = "",
        name: str = "",
        skip: int = 0,
        limit: int = 100,
        date_start: None,
        date_end: None
    ) -> List[ProjectSummary]:
        if is_dir_null:
            query = (
                db.query(self.model)
                .filter(Project.dir_name == None)
                .order_by(self.model.created_at.desc())
            )
        else:
            name_search = "%{}%".format(name)
            date_end = (
                datetime.datetime.strptime(date_end, "%Y-%m-%d")
                + datetime.timedelta(days=1)
            ).strftime("%Y-%m-%d")
            query = (
                db.query(self.model)
                .filter(
                    and_(
                        Project.name.ilike(name_search),
                        Project.created_at >= date_start,
                        Project.created_at <= date_end,
                        Project.customer_email == current_user_email,
                    )
                )
                .order_by(self.model.created_at.desc())
            )
        count = query.count()
        query_off_lim = query.offset(skip).limit(limit).all()
        print(query_off_lim)
        outputs = []
        for q in query_off_lim:
            task_states = db.query(Task.state_id).filter(Task.project_id == q.id).all()
            count_done = 0
            for state in task_states:
                if state[0] == 4:
                    count_done += 1
            project_summary = ProjectSummary(**q.__dict__)
            project_summary.task_done_count = count_done
            project_summary.task_total_count = len(task_states)
            outputs.append(project_summary)

        return count, outputs

    def create_with_annotation_errors_and_classes(
        self,
        db: Session,
        *,
        obj_in: ProjectCreate,
        anno_errors: List[int],
        anno_classes: List[str]
    ) -> Project:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        for anno_error in anno_errors:
            db_obj.annotation_errors.append(anno_error)
        for anno_class in anno_classes:
            db_obj.annotation_classes.append(anno_class)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_with_annotation_errors_and_classes(
        self,
        db: Session,
        *,
        db_obj: Project,
        obj_in: Union[ProjectUpdateTotal, Dict[str, Any]],
        anno_errors: List[int],
        anno_classes: List[str]
    ) -> Project:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        if anno_errors is not None:
            db_obj.annotation_errors = anno_errors
        if anno_classes is not None:
            db_obj.annotation_classes = anno_classes
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_with_string_classes(self, db: Session, id: Any) -> Optional[ProjectDetail]:
        project = db.query(self.model).filter(self.model.id == id).first()
        if project == None:
            return project
        classes = []
        for c in project.annotation_classes:
            classes.append(c.name)
        string_classes = ",".join(classes)

        anno_errors = []
        for e in project.annotation_errors:
            anno_errors.append(e.id)

        task_states = db.query(Task.state_id).filter(Task.project_id == project.id).all()
        count_done = 0
        for state in task_states:
            if state[0] == 4:
                count_done += 1

        project_dict = project.__dict__
        project_dict["annotation_errors"] = anno_errors
        project_dict["annotation_classes"] = string_classes
        project_string_classes = ProjectDetail(**project_dict)
        # project_string_classes.annotation_errors = anno_errors
        # project_string_classes.annotation_class = string_classes
        project_string_classes.task_done_count = count_done
        project_string_classes.task_total_count = len(task_states)

        return project_string_classes

    def get_distinct_annotator_count(self, db: Session, *, project_id: Any) -> Dict:
        annotator_count = (
            db.query(Task.annotator_id)
            .filter(Task.annotator_id != None)
            .filter(Task.project_id == project_id)
            .distinct()
            .count()
        )
        reviewer_count = (
            db.query(Task.reviewer_id)
            .filter(Task.reviewer_id != None)
            .filter(Task.project_id == project_id)
            .distinct()
            .count()
        )
        count = {
            "annotator_count": annotator_count,
            "reviewer_count": reviewer_count,
        }

        # query = db.query(self.model).filter(Project.id.in_(list(zip(*project_ids))[0])).order_by(self.model.created_at.desc())
        # count = query.count()
        # query_off_lim = query.offset(skip).limit(limit).all()
        return count

    def get_state_count(self, db: Session) -> Any:
        state_ids = db.query(State.id).all()

        count = {}
        for i in state_ids:
            count[i[0]] = db.query(Project.id).filter(Project.state_id == i[0]).count()

        return count

    def get_domain_count(self, db: Session) -> Any:
        domain_ids = db.query(Domain.id)

        count = {}
        for i in domain_ids:
            count[i[0]] = db.query(Project.id).filter(Project.domain_id == i[0]).count()

        return count

    def get_annotation_type_count(self, db: Session) -> Any:
        anno_type_ids = db.query(AnnotationType.id)

        count = {}
        for i in anno_type_ids:
            count[i[0]] = (
                db.query(Project.id).filter(Project.annotation_type_id == i[0]).count()
            )

        return count

    def get_by_domain_id(self, db: Session, *, domain_id: Any) -> Optional[Project]:
        return db.query(Project).filter(Project.domain_id == domain_id).first()

    def exist_error_id(self, db: Session, id: Any) -> Optional[ProjectDetail]:
        catch = False
        projects = db.query(self.model).all()
        for project in projects:
            for e in project.annotation_errors:
                if e.id == id:
                    catch = True
                    return catch
        return catch


project = CRUDProject(Project)
