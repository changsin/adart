import pandas as pd
import streamlit as st

from src.common.constants import USER_TYPES, USERS
from src.home import (
    is_authenticated,
    api_target,
    login,
    logout)
from src.models.users_info import User, UsersInfo


def select_user(is_sidebar=True):
    users_info = UsersInfo.get_users_info()
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
    users_info = api_target().get_users_info()
    if users_info.num_count > 0:
        df_users = pd.DataFrame(users_info.to_json()[USERS])
        st.dataframe(df_users)


def add_user():
    with st.form("Add User"):
        email = st.text_input("**Email:**")
        full_name = st.text_input("**Full Name:**")
        description = st.text_area("**Description**")
        is_active = st.checkbox("Is active?", False)
        group_id = st.radio("Group", USER_TYPES)
        phone = st.text_input("**Phone number:**")

        submitted = st.form_submit_button("Add User")
        if submitted:
            users_info = UsersInfo.get_users_info()
            next_user_id = users_info.get_next_user_id()
            new_user = User(
                id=next_user_id,
                email=email,
                full_name=full_name,
                is_active=is_active,
                group_id=USER_TYPES.index(group_id),
                is_superuser=False,
                phone=phone,
                description=description)
            users_info.add(new_user)
            users_info.save()

            st.markdown("### User ({}) ({}) added".format(new_user, email))


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
            users_info = UsersInfo.get_users_info()
            users_info.users.remove(selected_user)
            users_info.save()

            st.markdown("### User ({}) ({}) deleted".format(selected_user, selected_user.email))


def main():
    menu = {
        "List Users": lambda: list_users(),
        "Add User": lambda: add_user(),
        "Update User": lambda: update_user(),
        "Delete User": lambda: delete_user(),
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
