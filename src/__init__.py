import importlib.util
from pathlib import Path
spec = importlib.util.find_spec("src")
if spec is None:
    import sys

    path_root = Path(__file__).parent.parent if Path(__file__).parent.name == 'src' else Path(__file__).parent
    sys.path.append(str(path_root))

__version__ = "v0.1"
