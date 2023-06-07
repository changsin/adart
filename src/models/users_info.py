import attr
import json
import os

from src.common.constants import (
    ADQ_WORKING_FOLDER,
    JSON_EXT,
    USERS
)
import src.common.utils as utils


@attr.s(slots=True, frozen=False)
class User:
    id = attr.ib(validator=attr.validators.instance_of(int))
    email = attr.ib(validator=attr.validators.instance_of(str))
    full_name = attr.ib(default="", validator=attr.validators.instance_of(str))
    is_active = attr.ib(default=False, validator=attr.validators.instance_of(bool))
    group_id = attr.ib(default=0, validator=attr.validators.instance_of(int))
    is_superuser = attr.ib(default=False, validator=attr.validators.instance_of(bool))
    phone = attr.ib(default="", validator=attr.validators.instance_of(str))
    description = attr.ib(default="", validator=attr.validators.instance_of(str))

    def to_json(self) -> dict:
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
    def from_json(json_dict: dict) -> 'User':
        return User(
            id=json_dict["id"],
            email=json_dict["email"],
            full_name=json_dict["full_name"] if json_dict["full_name"] else "",
            is_active=json_dict["is_active"],
            group_id=json_dict["group_id"],
            is_superuser=json_dict["is_superuser"],
            phone=json_dict["phone"] if json_dict["phone"] else "",
            description=json_dict["description"] if json_dict["description"] else ""
        )


@attr.s(slots=True, frozen=False)
class UsersInfo:
    num_count = attr.ib(validator=attr.validators.instance_of(int))
    users = attr.ib(validator=attr.validators.instance_of(list))

    def add(self, user: User):
        self.users.append(user)
        self.num_count = len(self.users)

    def get_next_user_id(self) -> int:
        return len(self.users) + 1

    def get_user_by_id(self, user_id: int) -> User:
        if len(self.users) > 0:
            for user in self.users:
                if user.id == user_id:
                    return user

    def get_user_by_email(self, email: str) -> User:
        if len(self.users) > 0:
            for user in self.users:
                if user.email == email:
                    return user

    def to_json(self) -> dict:
        return {
            "num_count": self.num_count,
            "users": [user.to_json() for user in self.users]
        }

    def update_user(self, user_to_update: User):
        if len(self.users) > 0:
            index_to_update = None
            for index, user in enumerate(self.users):
                if user.id == user_to_update.id:
                    index_to_update = index
                    break

            self.users[index_to_update] = user_to_update

    def save(self):
        if not os.path.exists(ADQ_WORKING_FOLDER):
            os.mkdir(ADQ_WORKING_FOLDER)
        filename = os.path.join(ADQ_WORKING_FOLDER, USERS + JSON_EXT)
        utils.to_file(json.dumps(self,
                                 default=utils.default, indent=2),
                      filename)

    @staticmethod
    def from_json(json_dict) -> 'UsersInfo':
        return UsersInfo(num_count=json_dict['num_count'],
                         users=[User.from_json(json_task) for json_task in json_dict['users']])

    @staticmethod
    def get_users_info() -> 'UsersInfo':
        # TODO: later, get the users_info from an actual server
        users_filename = os.path.join(ADQ_WORKING_FOLDER, USERS + JSON_EXT)
        json_users = utils.from_file(users_filename, "{\"num_count\": 0, \"users\":[]}")

        return UsersInfo.from_json(json_users)
        # users = list()
        # if json_users:
        # for json_user in json_users:
        #     user_info = User.from_json(json_user)
        #     users.append(user_info)
        # return users


@attr.s(slots=True, frozen=False)
class GroupInfo:
    id = attr.ib(validator=attr.validators.instance_of(int))
    name = attr.ib(validator=attr.validators.instance_of(str))
    is_admin = attr.ib(default=False, validator=attr.validators.instance_of(bool))
    read_only = attr.ib(default=True, validator=attr.validators.instance_of(bool))

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "is_admin": self.is_admin,
            "read_only": self.read_only,
        }

    @staticmethod
    def from_json(json_dict: dict) -> 'GroupInfo':
        return GroupInfo(
            id=json_dict["id"],
            name=json_dict["name"],
            is_admin=json_dict["is_admin"],
            read_only=json_dict["read_only"]
        )
