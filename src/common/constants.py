from enum import Enum

ADQ_WORKING_FOLDER = ".adq"
PROJECTS = "projects"
TASKS = "tasks"
JSON_EXT = ".json"
CHARTS = "charts"

CVAT_XML = "CVAT XML"
PASCAL_VOC_XML = "PASCAL VOC XML"
COCO_JSON = "COCO JSON"
ADQ_JSON = "ADQ JSON"

SUPPORTED_FORMATS = [CVAT_XML, PASCAL_VOC_XML, COCO_JSON, ADQ_JSON]
SUPPORTED_IMAGE_FILE_EXTENSIONS = "*.jpg *.jpeg *.png *.bmp *.tiff *.gif"
SUPPORTED_VIDEO_FILE_EXTENSIONS = "*.mp4 *.avi *.mov"
SUPPORTED_AUDIO_FILE_EXTENSIONS = "*.mp3 *.wav"

PROJECT_COLUMNS = ['id', 'name', 'file_format_id',
                   'total_count', 'task_total_count', 'task_done_count']

TASK_COLUMNS = ['id', 'name', "project_id"]


class ErrorType(Enum):
    DVE_NOERROR = (0, "No error")       # "무오류"
    DVE_MISS = (1, "Mis-tagged")      # "오태깅"
    DVE_UNTAG = (2, "Un-tagged")        # "미태깅"
    DVE_OVER = (3, "Over-tagged")       # "과태깅"
    DVE_RANGE = (4, "Range error")      # "범위오류"
    DVE_ATTR = (5, "Attributes error")  # "속성오류"

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description

        return obj

    @staticmethod
    def get_all_error_types():
        return [""] + [error_type.description for error_type in ErrorType]
