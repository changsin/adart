import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class StatisticsBase(BaseModel):
    category: Optional[str] = None
    verbose: Optional[str] = None
    file_path: Optional[str] = None
    project_id: Optional[int] = None
    created_at: Optional[datetime.datetime] = None


# Properties to receive on item creation
class StatisticsCreate(StatisticsBase):
    category: str
    verbose: str
    project_id: int
    created_at: datetime.datetime


# Properties to receive on item update
class StatisticsUpdate(StatisticsBase):
    pass


# Properties shared by models stored in DB
class StatisticsInDBBase(StatisticsBase):
    id: int

    class Config:
        orm_mode = True


# Properties to return to client
class Statistics(StatisticsInDBBase):
    pass


# Properties properties stored in DB
class StatisticsInDB(StatisticsInDBBase):
    pass
