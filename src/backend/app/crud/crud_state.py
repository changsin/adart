from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.state import State 
from app.schemas.state import StateCreate, StateUpdate


class CRUDState(CRUDBase[State, StateCreate, StateUpdate]):
    pass


state = CRUDState(State)
