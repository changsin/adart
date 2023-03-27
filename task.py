import attr


@attr.s(slots=True, frozen=True)
class Task:
    id = attr.ib(validator=attr.validators.instance_of(int))
    name = attr.ib(validator=attr.validators.instance_of(str))
    project_id = attr.ib(validator=attr.validators.instance_of(int))
    state_name = attr.ib(validator=attr.validators.instance_of(str))
    count = attr.ib(validator=attr.validators.instance_of(int))
    anno_file_name = attr.ib(default=None, validator=attr.validators.instance_of(str))
    state_id = attr.ib(default=1, validator=attr.validators.instance_of(int))
    annotator_id = attr.ib(default=None, validator=attr.validators.instance_of(int))
    annotator_fullname = attr.ib(default=None, validator=attr.validators.instance_of(str))
    reviewer_id = attr.ib(default=None, validator=attr.validators.instance_of(int))
    reviewer_fullname = attr.ib(default=None, validator=attr.validators.instance_of(str))