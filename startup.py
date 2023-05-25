import os
import streamlit as st
from PIL import Image 

from src.common.constants import ADQ_WORKING_FOLDER
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
    logout
)


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

    # Create a sidebar with menu options
    selected_action = st.sidebar.selectbox("Go to page", list(admin_menu.keys()))

    if selected_action:
        # Call the selected method based on the user's selection
        admin_menu[selected_action]()


if __name__ == '__main__':
    st.set_page_config(page_title="Adart", layout="wide")
    def add_logo(logo_path, width, height):
    #"""Read and return a resized logo"""
        logo = Image.open(logo_path)
        modified_logo = logo.resize((width, height))
        return modified_logo

    resources_dir = "resources"
    my_logo = add_logo(logo_path=os.path.join(resources_dir, 'ADaRT_blue.png'), width=350, height=150)
    st.sidebar.image(my_logo)
    if not os.path.exists(ADQ_WORKING_FOLDER):
        os.mkdir(ADQ_WORKING_FOLDER)

    if not is_authenticated():
        login()
    else:
        main()
        logout()


