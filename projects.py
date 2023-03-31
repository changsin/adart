import attr
import json


@attr.s(slots=True, frozen=True)
class Projects:
    num = attr.ib(validator=attr.validators.instance_of(int))
    projects = attr.ib(validator=attr.validators.instance_of(list))

    @staticmethod
    def from_json(json_dict):
        return Projects(json_dict['num'], json_dict['projects'])


@attr.s(slots=True, frozen=True)
class Project:
    id = attr.ib(validator=attr.validators.instance_of(int))
    name = attr.ib(validator=attr.validators.instance_of(str))
    # new attributes
    images_folder = attr.ib(validator=attr.validators.instance_of(str))
    labels_folder = attr.ib(validator=attr.validators.instance_of(str))

    annotation_type_id = attr.ib(default=1, validator=attr.validators.instance_of(int))
    file_format_id = attr.ib(default=1, validator=attr.validators.instance_of(int))

    created_at = attr.ib(default=None, validator=attr.validators.instance_of(str))
    updated_at = attr.ib(default=None)

    description = attr.ib(default=None)

    progress = attr.ib(default=1, validator=attr.validators.instance_of(int))
    task_total_count = attr.ib(default=0, validator=attr.validators.instance_of(int))
    task_done_count = attr.ib(default=1, validator=attr.validators.instance_of(int))
    total_count = attr.ib(default=1, validator=attr.validators.instance_of(int))
    sample_count = attr.ib(default=1, validator=attr.validators.instance_of(int))
    per_task_count = attr.ib(default=1, validator=attr.validators.instance_of(int))

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

            "images_folder": self.images_folder,
            "labels_folder": self.labels_folder,

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

            "images_folder": self.images_folder,
            "labels_folder": self.labels_folder,

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
