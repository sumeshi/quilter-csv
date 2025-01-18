import sys
import polars as pl
from typing import Union
from qsv.utils.DataFrameUtils import exists_colname
from qsv.controllers.LogController import LogController

def sort(df: pl.LazyFrame, colnames: Union[str, tuple[str], list[str]], desc: bool = False) -> pl.LazyFrame:
    """[chainable] Sorts all rows by the specified column values."""
    # prevent type guessing
    colnames: tuple[str]
    if type(colnames) is list:
        colnames = tuple(colnames)
    elif type(colnames) is str:
        colnames = (colnames, )

    if not exists_colname(df=df, colnames=colnames):
        sys.exit(1)

    LogController.debug(f"sort by {colnames} ({'desc' if desc else 'asc'}).")
    return df.sort(colnames, descending=desc)
