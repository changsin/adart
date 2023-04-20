from .crud_item import item
from .crud_user import user
from .crud_group import group
from .crud_project import project
from .crud_annotation_class import annotation_class
from .crud_annotation_error import annotation_error
from .crud_annotation_type import annotation_type
from .crud_file_format import file_format
from .crud_task import task
from .crud_state import state
from .crud_statistics import statistics
from .crud_domain import domain

# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
