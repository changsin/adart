import attr
import json


@attr.s(slots=True, frozen=True)
class Project:
    id = attr.ib(validator=attr.validators.instance_of(int))
    name = attr.ib(validator=attr.validators.instance_of(str))
    # new attributes
    image_files = attr.ib(validator=attr.validators.instance_of(dict))
    label_files = attr.ib(validator=attr.validators.instance_of(dict))

    annotation_type_id = attr.ib(default=1, validator=attr.validators.instance_of(int))
    file_format_id = attr.ib(default=1, validator=attr.validators.instance_of(int))

    created_at = attr.ib(default=None, validator=attr.validators.instance_of(str))
    updated_at = attr.ib(default=None)

    description = attr.ib(default=None)

    progress = attr.ib(default=1, validator=attr.validators.instance_of(int))
    task_total_count = attr.ib(default=0, validator=attr.validators.instance_of(int))
    task_done_count = attr.ib(default=0, validator=attr.validators.instance_of(int))
    total_count = attr.ib(default=0, validator=attr.validators.instance_of(int))
    sample_count = attr.ib(default=0, validator=attr.validators.instance_of(int))
    per_task_count = attr.ib(default=0, validator=attr.validators.instance_of(int))

    # TODO: for backward-compatibility
    dir_name = attr.ib(default=None)

    annotation_classes = attr.ib(default=None)
    customer_company = attr.ib(default=None)
    customer_name = attr.ib(default=None)
    customer_phone = attr.ib(default=None)
    customer_email = attr.ib(default=None)
    annotation_errors = attr.ib(default=None)
    dataset_name = attr.ib(default=None)
    domain_id = attr.ib(default=None)

    def __iter__(self):
        yield from {
            "id": self.id,
            "name": self.name,

            "image_files": self.image_files,
            "label_files": self.label_files,

            "annotation_type_id": self.annotation_type_id,
            "file_format_id": self.file_format_id,

            "created_at": self.created_at,
            "updated_at": self.updated_at,

            "description": self.description,

            "progress": self.progress,
            "task_total_count": self.task_total_count,
            "task_done_count": self.task_done_count,
            "total_count": self.total_count,
            "sample_count": self.sample_count,

            # TODO: for backward-compatibility
            "per_task_count": self.per_task_count,
            "dir_name": self.per_task_count,

            "annotation_classes": self.annotation_classes,
            "customer_company": self.customer_company,
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "customer_email": self.customer_email,
            "annotation_errors": self.annotation_errors,
            "dataset_name": self.dataset_name,
            "domain_id": self.domain_id
        }.items()

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,

            "image_files": self.image_files,
            "label_files": self.label_files,

            "annotation_type_id": self.annotation_type_id,
            "file_format_id": self.file_format_id,

            "created_at": self.created_at,
            "updated_at": self.updated_at,

            "description": self.description,

            "progress": self.progress,
            "task_total_count": self.task_total_count,
            "task_done_count": self.task_done_count,
            "total_count": self.total_count,
            "sample_count": self.sample_count,

            # TODO: for backward-compatibility
            "per_task_count": self.per_task_count,
            "dir_name": self.per_task_count,

            "annotation_classes": self.annotation_classes,
            "customer_company": self.customer_company,
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "customer_email": self.customer_email,
            "annotation_errors": self.annotation_errors,
            "dataset_name": self.dataset_name,
            "domain_id": self.domain_id
        }

    @staticmethod
    def from_json(json_dict: dict):
        return Project(
            id=json_dict["id"],
            name=json_dict["name"],

            image_files=json_dict["image_files"],
            label_files=json_dict["label_files"],

            annotation_type_id=json_dict["annotation_type_id"],
            file_format_id=json_dict["file_format_id"],

            created_at=json_dict["created_at"],
            updated_at=json_dict["updated_at"],

            description=json_dict["description"],

            progress=json_dict["progress"],
            task_total_count=json_dict["task_total_count"],
            task_done_count=json_dict["task_done_count"],
            total_count=json_dict["total_count"],
            sample_count=json_dict["sample_count"],

            # TODO: for backward-compatibility
            per_task_count=json_dict["per_task_count"],
            dir_name=json_dict["dir_name"],

            annotation_classes=json_dict["annotation_classes"],
            customer_company=json_dict["customer_company"],
            customer_name=json_dict["customer_name"],
            customer_phone=json_dict["customer_phone"],
            customer_email=json_dict["customer_email"],
            annotation_errors=json_dict["annotation_errors"],
            dataset_name=json_dict["dataset_name"],
            domain_id=json_dict["domain_id"]
        )

    def __dict__(self):
        return vars(self)


@attr.s(slots=True, frozen=False)
class ProjectsInfo:
    num_count = attr.ib(validator=attr.validators.instance_of(int))
    # NB: add as a json dict to make manipulating in pandas dataframe easier
    projects = attr.ib(validator=attr.validators.instance_of(list))

    def __iter__(self):
        yield from {
            "num_count": self.num_count,
            "projects": self.projects
        }.items()

    def __str__(self):
        return json.dumps(self.to_json(), ensure_ascii=False)

    def add(self, project: Project):
        self.projects.append(project)
        self.num_count = len(self.projects)

    def to_json(self):
        return {
            "num_count": self.num_count,
            "projects": [project.to_json() for project in self.projects]
        }

    def __dict__(self):
        return vars(self)

    def get_next_project_id(self) -> int:
        if len(self.projects) == 0:
            return 0

        project_idx = []
        for project in self.projects:
            project_idx.append(project.id)

        return max(project_idx) + 1

    def get_project_by_id(self, project_id: int) -> Project:
        if len(self.projects) > 0:
            for project in self.projects:
                if project.id == project_id:
                    return project

    @staticmethod
    def from_json(json_dict):
        return ProjectsInfo(num_count=json_dict['num_count'],
                            projects=[Project.from_json(json_project) for json_project in json_dict['projects']])
