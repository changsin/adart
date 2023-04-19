import attr


@attr.s(slots=True, frozen=False)
class Metrics:
    data_files = attr.ib(validator=attr.validators.instance_of(list))
    label_files = attr.ib(validator=attr.validators.instance_of(list))
