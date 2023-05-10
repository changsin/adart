import datetime
import json
import os
from enum import Enum

import attr

import src.common.utils as utils
from src.common.constants import ADQ_WORKING_FOLDER, TASKS, JSON_EXT
from src.common.logger import get_logger

logger = get_logger(__name__)


class TaskState(Enum):
    DVS_NEW = (1, "New")        # "생성"
    DVS_WORKING = (2, "Working")    # "작업중"
    DVS_DONE = (3, "Done")          # "작업완료"
    DVS_CLOSED = (4, "Closed")      # "종료"

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description

        return obj


@attr.s(slots=True, frozen=False)
class Task:
    name = attr.ib(validator=attr.validators.instance_of(str))
    project_id = attr.ib(validator=attr.validators.instance_of(int))
    id = attr.ib(default=-1, validator=attr.validators.instance_of(int))

    dir_name = attr.ib(default=name, validator=attr.validators.instance_of(str))
    anno_file_name = attr.ib(default=None)

    created_at = attr.ib(default=str(datetime.datetime.now()), validator=attr.validators.instance_of(str))
    updated_at = attr.ib(default=str(datetime.datetime.now()), validator=attr.validators.instance_of(str))

    state_id = attr.ib(default=TaskState.DVS_NEW.value, validator=attr.validators.instance_of(int))
    state_name = attr.ib(default=TaskState.DVS_NEW.description, validator=attr.validators.instance_of(str))

    annotator_id = attr.ib(default=-1, validator=attr.validators.instance_of(int))
    annotator_fullname = attr.ib(default=None)

    reviewer_id = attr.ib(default=-1, validator=attr.validators.instance_of(int))
    reviewer_fullname = attr.ib(default=None)

    data_count = attr.ib(default=0, validator=attr.validators.instance_of(int))
    object_count = attr.ib(default=0, validator=attr.validators.instance_of(int))
    error_count = attr.ib(default=0, validator=attr.validators.instance_of(int))

    description = attr.ib(default=None)

    def __iter__(self):
        yield from {
            "id": self.id,
            "name": self.name,
            "project_id": self.project_id,

            "dir_name": self.dir_name,
            "anno_file_name": self.anno_file_name,

            "created_at": self.created_at,
            "updated_at": self.updated_at,

            "state_id": self.state_id,
            "state_name": self.state_name,

            "annotator_id": self.annotator_id,
            "annotator_fullname": self.annotator_fullname,

            "reviewer_id": self.reviewer_id,
            "reviewer_fullname": self.reviewer_fullname,

            "data_count": self.data_count,
            "object_count": self.object_count,
            "error_count": self.error_count,

            "description": self.description
        }.items()

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "project_id": self.project_id,

            "dir_name": self.dir_name,
            "anno_file_name": self.anno_file_name,

            "created_at": self.created_at,
            "updated_at": self.updated_at,

            "state_id": self.state_id,
            "state_name": self.state_name,

            "annotator_id": self.annotator_id,
            "annotator_fullname": self.annotator_fullname,

            "reviewer_id": self.reviewer_id,
            "reviewer_fullname": self.reviewer_fullname,

            "data_count": self.data_count,
            "object_count": self.object_count,
            "error_count": self.error_count,

            "description": self.description
        }

    @staticmethod
    def from_json(json_dict: dict):
        return Task(
            id=json_dict.get("id", -1),
            name=json_dict.get("name", None),
            project_id=json_dict["project_id"],

            dir_name=json_dict["dir_name"],
            anno_file_name=json_dict["anno_file_name"],

            created_at=json_dict["created_at"],
            updated_at=json_dict["updated_at"],

            state_id=json_dict["state_id"],
            state_name=json_dict["state_name"],

            annotator_id=json_dict["annotator_id"],
            annotator_fullname=json_dict["annotator_fullname"],

            reviewer_id=json_dict["reviewer_id"],
            reviewer_fullname=json_dict["reviewer_fullname"],

            data_count=json_dict.get("data_count", 0),
            object_count=json_dict.get("object_count", 0),
            error_count=json_dict.get("error_count", 0),

            description=json_dict.get("description", None)
        )


@attr.s(slots=True, frozen=False)
class TasksInfo:
    num_count = attr.ib(validator=attr.validators.instance_of(int))
    # NB: add as a json dict to make manipulating in pandas dataframe easier
    tasks = attr.ib(validator=attr.validators.instance_of(list))

    def add(self, task: Task):
        self.tasks.append(task)
        self.num_count = len(self.tasks)

    def remove(self, task_to_remove: Task):
        if task_to_remove in self.tasks:
            self.tasks.remove(task_to_remove)
            return
        else:
            for task in self.tasks:
                if task.id == task_to_remove.id:
                    self.tasks.remove(task)
                    return

        logger.error(f"**Error: Task {task_to_remove} not found in the list")

    def to_json(self):
        return {
            "num_count": self.num_count,
            "tasks": [task.to_json() for task in self.tasks]
        }

    def get_next_task_id(self) -> int:
        if len(self.tasks) == 0:
            return 0

        task_idx = []
        for task in self.tasks:
            task_idx.append(task.id)

        return max(task_idx) + 1

    def get_tasks_by_project_id(self, project_id: int) -> list:
        tasks = list()
        if len(self.tasks) > 0:
            for task in self.tasks:
                if task.project_id == project_id:
                    tasks.append(task)
        return tasks

    def get_task_by_id(self, task_id: int) -> Task:
        if len(self.tasks) > 0:
            for task in self.tasks:
                if task.id == task_id:
                    return task

    def update_task(self, task_to_update: Task):
        if len(self.tasks) > 0:
            index_to_update = None
            for index, task in enumerate(self.tasks):
                if task.id == task_to_update.id:
                    index_to_update = index
                    break

            self.tasks[index_to_update] = task_to_update

    def save(self):
        if not os.path.exists(ADQ_WORKING_FOLDER):
            os.mkdir(ADQ_WORKING_FOLDER)
        filename = os.path.join(ADQ_WORKING_FOLDER, TASKS + JSON_EXT)
        utils.to_file(json.dumps(self,
                                 default=utils.default, indent=2),
                      filename)

    @staticmethod
    def from_json(json_dict) -> 'TasksInfo':
        num_count = json_dict["num_count"]
        tasks = []
        for json_task in json_dict["tasks"]:
            tasks.append(Task.from_json(json_task))

        return TasksInfo(num_count=num_count, tasks=tasks)
