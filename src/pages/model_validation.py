import streamlit as st
import os

from src.common.constants import ADQ_WORKING_FOLDER


def create_project():
    with st.form("Create Model Validation Project"):
        project_name = st.text_input("**Name:**")

        company_name = st.text_input("**Company Name:**")
        company_url = st.text_input("**Company URL:**")
        company_address = st.text_input("**Company address:**")
        company_contact_person = st.text_input("**Contact person**")
        company_contact_person_email = st.text_input("**Contact person email:**")
        company_contact_person_phone = st.text_input("**Contact person phone number:**")

        domain = st.selectbox("Domain", ["Object recognition", "Motion "])

        first_contact_date = st.date_input("**First contact:**")
        uploaded_artifact = st.file_uploader("Upload contact artifacts")

        new_project_id = get_projects_info().get_next_project_id()

        save_folder = os.path.join(ADQ_WORKING_FOLDER, str(new_project_id))
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)

        if uploaded_artifact:
            # Save the uploaded file
            with open(os.path.join(save_folder, uploaded_artifact.name), "wb") as f:
                f.write(uploaded_artifact.getbuffer())

        test_date = st.date_input("**Test date**")
        uploaded_test_artifacts = st.file_uploader("Upload test artifacts", accept_multiple_files=True)
        if uploaded_test_artifacts:
            for file in uploaded_test_artifacts:
                # Save each uploaded file
                with open(os.path.join(save_folder, file.name), "wb") as f:
                    f.write(file.getbuffer())

        submitted = st.form_submit_button("Create project")
        if submitted:

            st.write("Project {} {} created".format(new_project_id, project_name))


def update_project():
    pass


def delete_project():
    pass


def main():
    menu = {
        "Create Project": lambda: create_project(),
        "Update Project": lambda: update_project(),
        "Delete Project": lambda: delete_project()
    }

    # Create a sidebar with menu options
    selected_action = st.sidebar.radio("Choose action", list(menu.keys()))

    if selected_action:
        # Call the selected method based on the user's selection
        menu[selected_action]()


if __name__ == '__main__':
    main()
