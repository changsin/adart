from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.statistics import Statistics 
from app.schemas.statistics import StatisticsCreate, StatisticsUpdate


class CRUDStatistics(CRUDBase[Statistics, StatisticsCreate, StatisticsUpdate]):
    pass


statistics = CRUDStatistics(Statistics)
