from typing import List, Optional

from pydantic import BaseModel


# Shared properties
class TaskBase(BaseModel):
    name: Optional[str] = None
    count: Optional[int] = None
    anno_file_name: Optional[str] = None
    annotator_id: Optional[int] = None
    reviewer_id: Optional[int] = None
    project_id: Optional[int] = None
    state_id: Optional[int] = None


# Properties to receive on item creation
class TaskCreate(TaskBase):
    name: str
    count: int
    project_id: int


# Properties to receive on item update
class TaskUpdate(TaskBase):
    pass


# Properties shared by models stored in DB
class TaskInDBBase(TaskBase):
    id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Task(TaskInDBBase):
    pass


class TaskOuterjoinUserState(TaskInDBBase):
    annotator_fullname: Optional[str]
    state_name: str
    reviewer_fullname: Optional[str]


class TasksOuterjoinUserStateWithCount(BaseModel):
    num_count: Optional[int]
    tasks: List[TaskOuterjoinUserState]


class TaskIdList(BaseModel):
    task_id_list: Optional[str]


# Properties properties stored in DB
class TaskInDB(TaskInDBBase):
    pass
