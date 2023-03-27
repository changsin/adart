import attr


@attr.s(slots=True, frozen=True)
class Project:
    id = attr.ib(validator=attr.validators.instance_of(int))
    name = attr.ib(validator=attr.validators.instance_of(str))
    images_folder = attr.ib(validator=attr.validators.instance_of(str))
    labels_folder = attr.ib(validator=attr.validators.instance_of(str))

    annotation_type_id = attr.ib(default=1, validator=attr.validators.instance_of(int))
    file_format_id = attr.ib(default=1, validator=attr.validators.instance_of(int))

    description = attr.ib(default=None, validator=attr.validators.instance_of(str))
    created_at = attr.ib(default=None, validator=attr.validators.instance_of(str))
    updated_at = attr.ib(default=None, validator=attr.validators.instance_of(str))

    task_count = attr.ib(default=0, validator=attr.validators.instance_of(int))
    progress = attr.ib(default=1, validator=attr.validators.instance_of(int))
    task_total_count = attr.ib(default=0, validator=attr.validators.instance_of(int))
    task_done_count = attr.ib(default=1, validator=attr.validators.instance_of(int))
    Total_count = attr.ib(default=1, validator=attr.validators.instance_of(int))
    sample_count = attr.ib(default=1, validator=attr.validators.instance_of(int))
    per_task_count = attr.ib(default=1, validator=attr.validators.instance_of(int))

    # TODO: for backward-compatibility
    dir_name = attr.ib(default=None, validator=attr.validators.instance_of(str))

    annotation_classes = attr.ib(default=None, validator=attr.validators.instance_of(str))
    customer_company = attr.ib(default=None, validator=attr.validators.instance_of(str))
    customer_name = attr.ib(default=None, validator=attr.validators.instance_of(str))
    customer_phone = attr.ib(default=None, validator=attr.validators.instance_of(str))
    customer_email = attr.ib(default=None, validator=attr.validators.instance_of(str))
    annotation_errors = attr.ib(default=None, validator=attr.validators.instance_of(list))
    dataset_name = attr.ib(default=None, validator=attr.validators.instance_of(str))
    domain_id = attr.ib(default=None, validator=attr.validators.instance_of(int))
