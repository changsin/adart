import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class FileFormatBase(BaseModel):
    name: Optional[str] = None


# Properties to receive on item creation
class FileFormatCreate(FileFormatBase):
    name: str


# Properties to receive on item update
class FileFormatUpdate(FileFormatBase):
    pass


# Properties shared by models stored in DB
class FileFormatInDBBase(FileFormatBase):
    id: int
    name: str

    class Config:
        orm_mode = True


# Properties to return to client
class FileFormat(FileFormatInDBBase):
    pass


# Properties properties stored in DB
class FileFormatInDB(FileFormatInDBBase):
    pass
