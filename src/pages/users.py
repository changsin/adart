import pandas as pd
import streamlit as st

from .home import (
    is_authenticated,
    api_target,
    login,
    logout)
from src.common.constants import USER_TYPES, USERS
from src.models.users_info import User, UsersInfo


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
            print(users_info)
            return users_info.get_user_by_id(int(user_id))


def list_users():
    users_info_dict = api_target().list_users()
    users_info = UsersInfo.from_json(users_info_dict)
    if users_info and users_info.num_count > 0:
        df_users = pd.DataFrame(users_info.to_json()[USERS])
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
        is_active = st.checkbox("Is active?", False)
        group_id = st.radio("Group", USER_TYPES)
        phone = st.text_input("**Phone number:**")

        submitted = st.form_submit_button("Add User")
        if submitted:
            new_user = User(
                id=0,
                email=email,
                full_name=full_name,
                is_active=is_active,
                group_id=USER_TYPES.index(group_id) + 1,
                is_superuser=False,
                phone=phone,
                description=description)
            new_user_dict = new_user.to_json()
            new_user_dict['password'] = password
            del new_user_dict['id']
            response = api_target().create_user(new_user_dict)
            if response:
                st.markdown(f"### User ({new_user}) ({email}) added with {response}")
            else:
                st.warning(f"### Create user ({new_user}) ({email}) failed with {response}")


def update_user():
    selected_user = select_user()
    if selected_user:
        with st.form("Update User"):
            email = st.text_input("**Email:**", selected_user.email)
            full_name = st.text_input("**Full Name:**", selected_user.full_name)
            description = st.text_area("**Description**", selected_user.description)
            is_active = st.checkbox("Is active?", selected_user.is_active)
            group_id = st.radio("Group",
                                options=USER_TYPES,
                                index=selected_user.group_id)
            phone = st.text_input("**Phone number:**", selected_user.phone)

            submitted = st.form_submit_button("Update User")
            if submitted:
                selected_user.email = email
                selected_user.full_name = full_name
                selected_user.is_active = is_active
                selected_user.group_id = USER_TYPES.index(group_id)
                selected_user.phone = phone
                selected_user.description = description

                users_info = UsersInfo.get_users_info()
                users_info.update_user(selected_user)
                users_info.save()

                st.markdown("### User ({}) ({}) updated".format(selected_user, email))


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
