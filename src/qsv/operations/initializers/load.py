import sys
from qsv.utils.FileUtils import exists_path
from qsv.controllers.CsvController import CsvController
from qsv.controllers.LogController import LogController

def load(path: tuple[str], separator: str = ',', low_memory: bool = False):
    """[initializer] Loads the specified CSV files."""
    if not exists_path(path=path):
        sys.exit(1)

    LogController.debug(msg=f"{len(path)} files are loaded. [{', '.join(path)}]")
    return CsvController(path=path).get_dataframe(separator=separator, low_memory=low_memory)
