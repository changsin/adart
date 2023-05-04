from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.file_format import FileFormat
from app.schemas.file_format import FileFormatCreate, FileFormatUpdate


class CRUDFileFormat(CRUDBase[FileFormat, FileFormatCreate, FileFormatUpdate]):
    pass


file_format = CRUDFileFormat(FileFormat)
