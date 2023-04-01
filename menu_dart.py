import attr

from projects_info import ProjectsInfo


@attr.s(slots=True, frozen=False)
class MenuDart:
    projects_info = attr.ib(default=None, validator=attr.validators.instance_of(ProjectsInfo))
    tasks_info = attr.ib(default=None)
    users = attr.ib(default=None)
