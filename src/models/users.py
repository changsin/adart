import attr

import src.common.utils as utils

@attr.s(slots=True, frozen=False)
class UserInfo:
    id = attr.ib(validator=attr.validators.instance_of(int))
    email = attr.ib(validator=attr.validators.instance_of(str))
    full_name = attr.ib(validator=attr.validators.instance_of(str))
    is_active = attr.ib(default=False, validator=attr.validators.instance_of(bool))
    group_id = attr.ib(default=0, validator=attr.validators.instance_of(id))
    is_superuser = attr.ib(default=False, validator=attr.validators.instance_of(bool))
    phone = attr.ib(default="", validator=attr.validators.instance_of(str))
    description = attr.ib(default="", validator=attr.validators.instance_of(str))

    def __iter__(self):
        yield from {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "group_id": self.group_id,
            "is_superuser": self.is_superuser,
            "phone": self.phone,
            "description": self.description
        }.items()

    def __str__(self):
        return json.dumps(dict(self), default=utils.default, ensure_ascii=False)

    def to_json(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "group_id": self.group_id,
            "is_superuser": self.is_superuser,
            "phone": self.phone,
            "description": self.description
        }

    @staticmethod
    def from_json(json_dict: dict):
        return UserInfo(
            id = json_dict["id"],
            email = json_dict["email"],
            full_name = json_dict['full_name'],
            is_active = json_dict['is_active'],
            group_id = json_dict['group_id'],
            is_superuser = json_dict['is_superuser'],
            phone = json_dict['phone'],
            description = json_dict['description']
        )

    def __dict__(self):
        return vars(self)

class GroupInfo
    id = attr.ib(validator=attr.validators.instance_of(int))
    name = attr.ib(validator=attr.validators.instance_of(str))
    is_admin = attr.ib(default=False, validator=attr.validators.instance_of(bool))
    read_only = attr.ib(default=True, validator=attr.validators.instance_of(bool))
