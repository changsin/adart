import os
import streamlit as st
from PIL import Image 

from src.common.constants import (
    ADQ_WORKING_FOLDER,
    UserType
)
from src.common.utils import get_window_size
from src.pages import (
    home,
    dashboard,
    projects,
    reports,
    reviews,
    tasks,
    users,
)
from src.pages.home import (
    is_authenticated,
    login,
    logout,
    get_user_by_email
)
from src.common.logger import get_logger

logger = get_logger(__name__)


def main():
    admin_menu = {
        "Home": home.main,
        "Dashboard": dashboard.main,
        "Projects": projects.main,
        "Tasks": tasks.main,
        "Reviews": reviews.main,
        "Reports": reports.main,
        "Users": users.main,
    }

    user_menu = {
        "Home": home.main,
        "Dashboard": dashboard.main,
        "Reports": reports.main,
    }

    reviewer_menu = {
        "Home": home.main,
        "Dashboard": dashboard.main,
        "Reviews": reviews.main,
        "Reports": reports.main,
    }

    username = st.session_state.get("username")
    user = get_user_by_email(username)
    if user:
        menu = user_menu
        if user.group_id == UserType.ADMINISTRATOR.value:
            menu = admin_menu
        elif user.group_id == UserType.REVIEWER.value:
            menu = reviewer_menu

        # Create a sidebar with menu options
        selected_action = st.sidebar.selectbox("Go to page", list(menu.keys()))
        if selected_action:
            # Call the selected method based on the user's selection
            menu[selected_action]()


if __name__ == '__main__':
    st.set_page_config(page_title="Adart", layout="wide")
    # window_width, _ = get_window_size()
    # max_width = window_width * 0.95 if window_width > 0 else 700
    # st.session_state.sidebar_state = "collapsed"
    # with st.container():
    #     st.markdown(
    #         f"""
    #         <style>
    #         .stApp {{
    #             max-width: {max_width}px;
    #             margin: 0 auto;
    #             padding: 0px;
    #             border: 1px solid #ccc;
    #             top: 5px solid #333;
    #             border-radius: 5px;
    #             box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    #         }}
    #         </style>
    #         """,
    #         unsafe_allow_html=True,
    #     )

    def add_logo(logo_path, width, height):
        """Read and return a resized logo"""
        logo = Image.open(logo_path)
        modified_logo = logo.resize((width, height))
        return modified_logo

    resources_dir = "resources"
    my_logo = add_logo(logo_path=os.path.join(resources_dir, 'ADaRT_blue.png'), width=350, height=150)
    st.sidebar.image(my_logo)
    username = st.session_state.get("username")
    if username:
        st.sidebar.header(username)

    #def add_logo(logo_path, width, height):
    #"""Read and return a resized logo"""
    #    logo = Image.open(logo_path)
    #    modified_logo = logo.resize((width, height))
    #    return modified_logo

    #resources_dir = "resources"
    #my_logo = add_logo(logo_path=os.path.join(resources_dir, 'ADaRT_blue.png'), width=350, height=150)
    #st.sidebar.image(my_logo)
    if not os.path.exists(ADQ_WORKING_FOLDER):
        os.mkdir(ADQ_WORKING_FOLDER)

    if not is_authenticated():
        login()
    else:
        main()
        logout()


