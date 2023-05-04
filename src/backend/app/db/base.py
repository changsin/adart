# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.item import Item  # noqa
from app.models.user import User  # noqa
from app.models.group import Group
from app.models.project import Project
from app.models.file_format import FileFormat
from app.models.annotation_type import AnnotationType
from app.models.task import Task
from app.models.state import State
from app.models.statistics import Statistics
from app.models.domain import Domain
