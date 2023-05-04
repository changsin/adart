import datetime
from typing import Optional

from pydantic import BaseModel


# Shared properties
class CustomerBase(BaseModel):
    company: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


# Properties to receive on item creation
class CustomerCreate(CustomerBase):
    name: str


# Properties to receive on item update
class CustomerUpdate(CustomerBase):
    pass


# Properties shared by models stored in DB
class CustomerInDBBase(CustomerBase):
    id: int
    name: str

    class Config:
        orm_mode = True


# Properties to return to client
class Customer(CustomerInDBBase):
    pass


# Properties properties stored in DB
class CustomerInDB(CustomerInDBBase):
    pass
