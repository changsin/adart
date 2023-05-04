from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.db import base  # noqa: F401

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)

    group = crud.group.get_multi(db)
    if not group:
        for idx in range(len(settings.DEFAULT_GROUP_NAMES)):
            group_in = schemas.group.GroupCreate(
                name=settings.DEFAULT_GROUP_NAMES[idx],
                is_admin=settings.DEFAULT_GROUP_IS_ADMIN[idx],
                is_user=settings.DEFAULT_GROUP_IS_USER[idx],
                is_reviewer=settings.DEFAULT_GROUP_IS_REVIEWER[idx],
                read_only=settings.DEFAULT_GROUP_READ_ONLY[idx],
            )
            group = crud.group.create(db, obj_in=group_in)

    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            group_id=2,
            is_superuser=True,
        )
        user = crud.user.create(db, obj_in=user_in)  # noqa: F841

    annotation_error = crud.annotation_error.get_multi(db)
    if not annotation_error:
        for idx in range(len(settings.DEFAULT_ERROR_NAMES)):
            annotation_error_in = schemas.annotation_error.AnnotationErrorCreate(
                name=settings.DEFAULT_ERROR_NAMES[idx],
                code=settings.DEFAULT_ERROR_CODES[idx],
                is_default=True,
            )
            annotation_error = crud.annotation_error.create(
                db, obj_in=annotation_error_in
            )

    annotation_type = crud.annotation_type.get_multi(db)
    if not annotation_type:
        for idx in range(len(settings.DEFAULT_ANNOTATION_TYPES)):
            annotation_type_in = schemas.annotation_type.AnnotationTypeCreate(
                name=settings.DEFAULT_ANNOTATION_TYPES[idx],
            )
            annotation_type = crud.annotation_type.create(db, obj_in=annotation_type_in)

    file_format = crud.file_format.get_multi(db)
    if not file_format:
        for idx in range(len(settings.DEFAULT_FILE_FORMATS)):
            file_format_in = schemas.file_format.FileFormatCreate(
                name=settings.DEFAULT_FILE_FORMATS[idx],
            )
            file_format = crud.file_format.create(db, obj_in=file_format_in)

    state = crud.state.get_multi(db)
    if not state:
        for idx in range(len(settings.DEFAULT_STATE_NAMES)):
            state_in = schemas.state.StateCreate(
                name=settings.DEFAULT_STATE_NAMES[idx],
                code=settings.DEFAULT_STATE_CODES[idx],
            )
            state = crud.state.create(db, obj_in=state_in)

    domain = crud.domain.get_multi(db)
    if not domain:
        for idx in range(len(settings.DEFAULT_DOMAIN_NAMES)):
            domain_in = schemas.domain.DomainCreate(
                name=settings.DEFAULT_DOMAIN_NAMES[idx],
                code=settings.DEFAULT_DOMAIN_CODES[idx],
            )
            domain = crud.domain.create(db, obj_in=domain_in)
