import attr


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
    description = attr.ib(default=None)
    updated_at = attr.ib(default=None)

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
