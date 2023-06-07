import pandas as pd
import streamlit as st

from src.api.security import get_password_hash
from src.common.constants import (
    UserType,
    USERS
)
from src.common.logger import get_logger
from src.models.users_info import User, UsersInfo
from .home import (
    is_authenticated,
    api_target,
    login,
    logout)

logger = get_logger(__name__)


def select_user(is_sidebar=True):
    users_info_dict = api_target().list_users()
    users_info = UsersInfo.from_json(users_info_dict)
    if users_info.num_count > 0:
        df_users = pd.DataFrame(users_info.to_json()[USERS])
        df_users_id_names = df_users[["id", "email"]]
        options = ["{}-{}".format(user_id, name)
                   for user_id, name in df_users_id_names[["id", "email"]].values.tolist()]
        # set an empty string as the default selection - no action
        options.append("")
        if is_sidebar:
            selected_user_id_name = st.sidebar.selectbox("Select user",
                                                         options=options,
                                                         index=len(options) - 1)
        else:
            selected_user_id_name = st.selectbox("Select user",
                                                 options=options,
                                                 index=len(options) - 1)

        if selected_user_id_name:
            user_id, email, = selected_user_id_name.split('-', maxsplit=1)
            return users_info.get_user_by_id(int(user_id))
    else:
        st.warning("Please create a user first")


def list_users():
    users_info_dict = api_target().list_users()
    users_info = UsersInfo.from_json(users_info_dict)
    if users_info and users_info.num_count > 0:
        df_users = pd.DataFrame(users_info.to_json()[USERS])
        # Remove the "password" column
        df_users = df_users.drop("password", axis=1)
        st.dataframe(df_users)


def list_groups():
    groups_dict = api_target().list_groups()
    st.dataframe(groups_dict)


def create_user():
    with st.form("Create User"):
        email = st.text_input("**Email:**")
        password = st.text_input("**Password:**", type="password")
        full_name = st.text_input("**Full Name:**")
        description = st.text_area("**Description**")
        is_active = st.checkbox("Is active?", True)
        group_id = st.radio("Group", UserType.get_all_types())
        phone = st.text_input("**Phone number:**")

        submitted = st.form_submit_button("Add User")
        if submitted:
            password_hash = get_password_hash(password)
            logger.info(password_hash)
            new_user = User(
                id=0,
                email=email,
                full_name=full_name,
                is_active=is_active,
                group_id=UserType.get_value_from_description(group_id),
                is_superuser=False,
                phone=phone,
                description=description,
                password=password_hash)
            new_user_dict = new_user.to_json()
            new_user_dict['password'] = password
            response = api_target().create_user(new_user_dict)
            if response:
                st.markdown(f"### User ({full_name}) ({email}) created")
            else:
                st.warning(f"### Create user ({new_user}) ({email}) failed with {response}")


def update_user():
    selected_user = select_user()
    if selected_user:
        with st.form("Update User"):
            email = st.text_input("**Email:**", selected_user.email)
            password = st.text_input("**Password:**", type="password")
            full_name = st.text_input("**Full Name:**", selected_user.full_name)
            description = st.text_area("**Description**", selected_user.description)
            is_active = st.checkbox("Is active?", selected_user.is_active)
            group_id = st.radio("Group",
                                options=UserType.get_all_types(),
                                index=selected_user.group_id - 1)
            phone = st.text_input("**Phone number:**", selected_user.phone)

            submitted = st.form_submit_button("Update User")
            if submitted:
                password_hash = get_password_hash(password)
                logger.info(password_hash)

                selected_user.email = email
                selected_user.full_name = full_name
                selected_user.is_active = is_active
                selected_user.group_id = UserType.get_value_from_description(group_id)
                selected_user.phone = phone
                selected_user.description = description
                selected_user.password = password_hash

                users_info = UsersInfo.get_users_info()
                users_info.update_user(selected_user)
                users_info.save()

                st.markdown("### User ({}) ({}) updated".format(selected_user.full_name, email))


def delete_user():
    selected_user = select_user()
    if selected_user:
        delete_confirmed = st.sidebar.button("Are you sure you want to delete the user {}-{}?"
                                             .format(selected_user.id, selected_user.email))
        if delete_confirmed:
            response = api_target().delete_user(selected_user.id)
            st.markdown(f"### User ({selected_user.id}) deleted {response}")


def main():
    # Clear the sidebar
    st.sidebar.empty()
    # Clear the main page
    st.empty()

    menu = {
        "List Users": lambda: list_users(),
        "Create User": lambda: create_user(),
        "Update User": lambda: update_user(),
        "Delete User": lambda: delete_user(),
        "List Groups": lambda: list_groups(),
    }

    # Create a sidebar with menu options
    selected_action = st.sidebar.radio("Choose action", list(menu.keys()))

    if selected_action:
        # Call the selected method based on the user's selection
        menu[selected_action]()


if __name__ == '__main__':
    if not is_authenticated():
        login()
    else:
        main()
        logout()
