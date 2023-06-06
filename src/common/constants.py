from enum import Enum

ADQ_WORKING_FOLDER = ".adq"
PROJECTS = "projects"
PROJECT = "project"
TASKS = "tasks"
TASK = "task"
USERS = "users"
JSON_EXT = ".json"
CHARTS = "charts"

STRADVISION_XML = "STRADVISION XML"
CVAT_XML = "CVAT XML"
PASCAL_VOC_XML = "PASCAL VOC XML"
GPR_JSON = "GPR JSON"
COCO_JSON = "COCO JSON"
ADQ_JSON = "ADQ JSON"
YOLO_V5_TXT = "YOLO_V5 TXT"

SUPPORTED_LABEL_FILE_EXTENSIONS = ['json', 'xml', 'txt']
SUPPORTED_LABEL_FORMATS = [STRADVISION_XML, CVAT_XML, PASCAL_VOC_XML, GPR_JSON, ADQ_JSON, YOLO_V5_TXT]
SUPPORTED_IMAGE_FILE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'gif']
SUPPORTED_VIDEO_FILE_EXTENSIONS = "*.mp4 *.avi *.mov"
SUPPORTED_AUDIO_FILE_EXTENSIONS = "*.mp3 *.wav"

PROJECT_COLUMNS = ['id', 'name', 'task_total_count', 'task_done_count']

TASK_COLUMNS = ['id', 'name', "project_id"]

USER_TYPES = ["user", "reviewer", "inspector", "administrator"]


class ErrorType(Enum):
    # DVE_NOERROR = (0, "No error")       # "무오류"
    DVE_MISS = (1, "Mis-tagged")        # "오태깅"
    DVE_UNTAG = (2, "Untagged")        # "미태깅"
    DVE_OVER = (3, "Over-tagged")       # "과태깅"
    DVE_RANGE = (4, "Range_error")      # "범위오류"
    DVE_ATTR = (5, "Attributes_error")  # "속성오류"

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description

        return obj

    @staticmethod
    def get_all_types():
        return [""] + [error_type.description for error_type in ErrorType]


class DomainCode(Enum):
    DMN_FARM = (1, "Farming")                           # "농,축,수산업"
    DMN_CULTURE = (2, "Culture")                        # "문화,스포츠,관광
    DMN_SAFETY = (3, "Safety")                          # "안전,환경"
    DMN_LANGUAGE = (4, "Language")                      # "음성,자연어
    DMN_HEALTH = (5, "Health")                          # "의료,건강서비스
    DMN_TRAFFIC = (6, "Traffic")                        # "자율주행,교통
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


# Type1
class Type1Shape1Q(Enum):
    NONE = (0, "None")
    SOLID = (1, "Solid")
    DOTTED = (2, "Dotted")
    CATSEYE = (3, "CatsEye")
    ZIGZAG = (4, "Zigzag")

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

    @staticmethod
    def get_index(value):
        for i, member in enumerate(Type1Shape1Q):
            if member.value == value:
                return i
        raise ValueError('Invalid value {}'.format(value))

    @staticmethod
    def get_all_types():
        return [item.description for item in Type1Shape1Q]


# Type2
class Type2SingleDoubleW(Enum):
    NONE = (0, "None")
    SINGLE = (1, "Single")
    DOUBLE = (2, "Double")
    ACCESSORIES = (3, "Accessories")

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

    @staticmethod
    def get_index(value):
        for i, member in enumerate(Type2SingleDoubleW):
            if member.value == value:
                return i
        raise ValueError('Invalid value {}'.format(value))

    @staticmethod
    def get_all_types():
        return [item.description for item in Type2SingleDoubleW]


# Type3
class Type3PositionE(Enum):
    NONE = (0, "None")
    L = (-255, "L")     # together with Opposite Type4
    L1 = (1, "L1")
    L1_2 = (1537, "L1_2")
    L2 = (257, "L2")
    L3 = (513, "L3")
    L4 = (769, "L4")
    L5 = (1025, "L5")
    L6 = (1281, "L6")
    LU = (1793, "U(LU)")

    R = (-254, "R")     # together with Opposite Type4
    R1 = (2, "R1")
    R1_2 = (1538, "R1_2")
    R2 = (258, "R2")
    R3 = (514, "R3")
    R4 = (770, "R4")
    R5 = (1026, "R5")
    R6 = (1282, "R6")
    RU = (1794, "U(RU)")

    U = (-253, "U")

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

    @staticmethod
    def get_index(value):
        for i, member in enumerate(Type3PositionE):
            if member.value == value:
                return i
        raise ValueError('Invalid value {}'.format(value))

    @staticmethod
    def get_all_types():
        return [item.description for item in Type3PositionE]


# Type4
class Type4UnusualCaseR(Enum):
    NONE = (0, "None")
    COMBINATION = (1, "Combination")
    BRANCH = (2, "Branch")
    UNUSED = (3, "Unused")
    OPPOSITE = (4, "Opposite")

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

    @staticmethod
    def get_index(value):
        for i, member in enumerate(Type4UnusualCaseR):
            if member.value == value:
                return i
        raise ValueError('Invalid value {}'.format(value))

    @staticmethod
    def get_all_types():
        return [item.description for item in Type4UnusualCaseR]


# Type4
class BoundaryType2R(Enum):
    NONE = (0, "None")
    BEACON = (9, "Beacon(1)")
    PLASTIC_WALL = (7, "Plastic wall(2)")
    DRUM = (8, "Drum(3)")
    CONE = (10, "Cone(4)")
    WALL = (1, "Wall(5)")
    GUARDRAIL = (3, "Guardrail(6)")
    FIXED_DIVIDER = (4, "Fixed divider(7)")
    TEMPORARY_DIVIDER = (6, "Temporary divider(8)")
    FIXED_PARKING = (2, "Fixed parking(9)")
    STRUCTURE = (14, "Structure(10)")
    CURB = (5, "Curb(11)")
    EDGE = (11, "Edge(12)")
    INDOOR_PARKING_LOT = (12, "Indoor parking lot(13)")
    UNEXPLAINABLE = (13, "Unexplainable(14)")
    ETC = (15, "Etc.(15)")
    LOW_CURB = (16, "Low curb(16)")
    LOW_BOUNDARY = (17, "Low boundary(17)")
    SNOW_PILE = (18, "Snow pile(18)")
    SNOW_WALL = (19, "Snow wall(19)")

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

    @staticmethod
    def get_index(value):
        for i, member in enumerate(BoundaryType2R):
            if member.value == value:
                return i
        raise ValueError('Invalid value {}'.format(value))

    @staticmethod
    def get_all_types():
        return [item.description for item in BoundaryType2R]


# Type5
class Type5ColorS(Enum):
    NONE = (0, "None")
    WHITE = (1, "White")
    YELLOW = (2, "Yellow")
    BLUE = (3, "Blue")
    OTHER = (4, "Other")

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

    @staticmethod
    def get_index(value):
        for i, member in enumerate(Type5ColorS):
            if member.value == value:
                return i
        raise ValueError('Invalid value {}'.format(value))

    @staticmethod
    def get_all_types():
        return [item.description for item in Type5ColorS]


# Type6
class Type6BicycleD(Enum):
    NONE = (0, "None")
    BICYCLED = (1, "Bicycle")

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

    @staticmethod
    def get_index(value):
        for i, member in enumerate(Type6BicycleD):
            if member.value == value:
                return i
        raise ValueError('Invalid value {}'.format(value))

    @staticmethod
    def get_all_types():
        return [item.description for item in Type6BicycleD]


# Type road marker
class TypeRoadMarkerQ(Enum):
    NONE = (0, "Uncertain/difficult to classify")
    STOP_LINE = (1, "Stop line")
    PEDESTRIAN_CROSSING = (2, "Pedestrian crossing")
    DIRECTIONAL_ARROWS = (3, "Directional arrows")
    SPEED_BREAKER = (4, "Speed bump/Speed breaker")

    def __new__(cls, value, description):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

    @staticmethod
    def get_index(value):
        for i, member in enumerate(TypeRoadMarkerQ):
            if member.value == value:
                return i
        raise ValueError('Invalid value {}'.format(value))

    @staticmethod
    def get_all_types():
        return [item.description for item in TypeRoadMarkerQ]


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
