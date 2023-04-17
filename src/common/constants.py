from enum import Enum

ADQ_WORKING_FOLDER = ".adq"
PROJECTS = "projects"
TASKS = "tasks"
JSON_EXT = ".json"
CHARTS = "charts"

STRADVISION_XML = "STRADVISION XML"
CVAT_XML = "CVAT XML"
PASCAL_VOC_XML = "PASCAL VOC XML"
COCO_JSON = "COCO JSON"
ADQ_JSON = "ADQ JSON"

SUPPORTED_LABEL_FORMATS = [STRADVISION_XML, CVAT_XML, PASCAL_VOC_XML, COCO_JSON, ADQ_JSON]
SUPPORTED_IMAGE_FILE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'gif']
SUPPORTED_VIDEO_FILE_EXTENSIONS = "*.mp4 *.avi *.mov"
SUPPORTED_AUDIO_FILE_EXTENSIONS = "*.mp3 *.wav"

PROJECT_COLUMNS = ['id', 'name', 'file_format_id',
                   'total_count', 'task_total_count', 'task_done_count']

TASK_COLUMNS = ['id', 'name', "project_id"]


class ErrorType(Enum):
    DVE_NOERROR = (0, "No error")       # "무오류"
    DVE_MISS = (1, "Mis-tagged")        # "오태깅"
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
    def get_all_types():
        return [""] + [error_type.description for error_type in ErrorType]


class DomainCode(Enum):
    DMN_FARM = (1, "Farming")   # "농,축,수산업"
    DMN_CULTURE = (2, "Culture, Sports, Tourism")       # "문화,스포츠,관광
    DMN_SAFETY = (3, "Safety & Environment")            # "안전,환경"
    DMN_LANGUAGE = (4, "Language and Voice")            # "음성,자연어
    DMN_HEALTH = (5, "Medical & Health Services")       # "의료,건강서비스
    DMN_TRAFFIC = (6, "Autonomous Driving & Traffic")   # "자율주행,교통
    DMN_STRATEGY = (7, "Strategy")                      # "전략"
    DMN_MANUFACTURE = (8, "Manufacturing")              # "제조,로보틱스
    DMN_COM_GRAPHICS = (9, "Computer Graphics")         # "컴퓨터 그래픽스
    DMN_COM_VISION = (10, "Computer Vision")            # "컴퓨터 비전
    DMN_CONSUMER = (11, "Consumer Products")            # "consumer products
    DMN_ETC = (12, "Etc.")                              # "기타"

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description

        return obj

    @staticmethod
    def get_all_types():
        return [""] + [domain.description for domain in DomainCode]


class ModelTaskType(Enum):
    MODEL_TASK_CONTACT = (1, "Contact")
    MODEL_TASK_TEST = (2, "Test")
    MODEL_TASK_REPORT = (3, "Report")

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description

        return obj

    @staticmethod
    def get_all_types():
        return [""] + [task_type.description for task_type in ModelTaskType]
