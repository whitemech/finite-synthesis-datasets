import inspect
from pathlib import Path

CUR_PATH = Path(inspect.getfile(inspect.currentframe())).parent  # type: ignore
ROOT_DIR = Path(CUR_PATH, "..").resolve().absolute()
