from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.domain import Domain
from app.schemas.domain import DomainCreate, DomainUpdate


class CRUDDomain(CRUDBase[Domain, DomainCreate, DomainUpdate]):
    pass


domain = CRUDDomain(Domain)
