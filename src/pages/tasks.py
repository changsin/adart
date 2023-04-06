import importlib.util
import os.path

import pandas as pd

spec = importlib.util.find_spec("src")
if spec is None:
    import sys
    from pathlib import Path

    path_root = Path(__file__).parents[2]
    sys.path.append(str(path_root))

from src.common.charts import *
from src.home import select_project
from src.pages import label_metrics
from src.models.projects_info import Project


def step_size(value):
    if value < 10:
        return 1.0
    elif value < 100:
        return 10.0
    else:
        return 100.0


# def sample_data(selected_project: Project, df_sample_count: pd.DataFrame):
#     for index, row in df_sample_count.iterrows():
#         label_file
#         label_file_path = os.path.join(constants.ADQ_WORKING_FOLDER, selected_project.id, row)


def calculate_sample_count(count, percent):
    return int((count * percent) / 100)


def calculate_sample_distribution(df_total_count: pd.DataFrame,
                                  sample_percent: int) -> pd.DataFrame:
    df_sample_count = df_total_count.copy()

    for index, row in df_total_count.iterrows():
        sample_count = calculate_sample_count(row['count'], sample_percent)
        if sample_count < 1.0:
            st.warning("Please set a higher percentage to pick at least one file per folder")
            return None
        else:
            df_sample_count['count'] = sample_count

    return df_sample_count


def main():
    selected_project = select_project()

    if selected_project:
        label_objects_dict = label_metrics.load_label_files(selected_project.label_files)
        images_per_label_file_dict = dict()
        if label_objects_dict.items() is not None:
            for labels_file, dart_labels in label_objects_dict.items():
                images_per_label_file_dict[labels_file] = len(dart_labels.images)

        df_total_count = pd.DataFrame(images_per_label_file_dict.items(), columns=['filename', 'count'])
        df_total_count['filename'] = df_total_count['filename'].apply(lambda file: os.path.basename(file))
        st.dataframe(df_total_count)

        with st.form("Create Tasks"):
            sample_percent = st.number_input("% of samples", step=step_size(0.0), format="%.2f")
            is_keep_folders = st.checkbox("Keep folder structures", value=True)

            submitted = st.form_submit_button("Create tasks")
            if submitted:
                if sample_percent <= 0:
                    st.warning("Please enter a valid percent value")
                    return
                else:
                    st.write("Alright")
                    total_count = df_total_count['count'].sum()
                    total_sample_count = calculate_sample_count(total_count, sample_percent)

                    if is_keep_folders:
                        df_sample_count = calculate_sample_distribution(df_total_count, sample_percent)
                        if df_sample_count is None:
                            return

                        total_sample_count = df_sample_count['count'].sum()

                    if total_sample_count > total_count:
                        st.warning("Please enter a valid percent value")
                        return

                    st.write("Here is how the image files will be sampled")
                    st.dataframe(df_sample_count)
                    return


if __name__ == '__main__':
    main()
