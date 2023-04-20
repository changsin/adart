from fastapi import APIRouter

from app.api.api_v1.endpoints import items, login, users, group, utils, project, annotation_class, annotation_error, annotation_type, file_format, task, state, statistics, domain, dashboard

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(group.router, prefix="/group", tags=["group"])
api_router.include_router(project.router, prefix="/project", tags=["project"])
api_router.include_router(task.router, prefix="/task", tags=["task"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(annotation_error.router, prefix="/annoerror", tags=["annotation_error"])
api_router.include_router(domain.router, prefix="/domain", tags=["domain"])
api_router.include_router(annotation_class.router, prefix="/annoclass", tags=["annotation_class"])
api_router.include_router(annotation_type.router, prefix="/annotype", tags=["annotation_type"])
api_router.include_router(file_format.router, prefix="/fileformat", tags=["file_format"])
api_router.include_router(state.router, prefix="/state", tags=["state"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["statistics"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
