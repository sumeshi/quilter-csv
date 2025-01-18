import sys
from pathlib import Path

from qsv.controllers.LogController import LogController

def exists_path(path: tuple[str]) -> bool:
    for p in path:
        if not Path(p).exists():
            LogController.error(f"[Error] File \"{p}\" does not exist.")
            return False
    else:
        return True
