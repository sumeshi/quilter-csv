import sys
import polars as pl
from typing import Union
from qsv.utils.DataFrameUtils import exists_colname
from qsv.controllers.LogController import LogController

def uniq(df: pl.LazyFrame, colnames: Union[str, tuple[str], list[str]]) -> pl.LazyFrame:
    """[chainable] Remove duplicate rows based on the specified column names."""
    # prevent type guessing
    colnames: tuple[str]
    if type(colnames) is list:
        colnames = tuple(colnames)
    elif type(colnames) is str:
        colnames = (colnames, )

    if not exists_colname(df=df, colnames=colnames):
        sys.exit(1)

    LogController.debug(f"unique by {colnames}.")
    return df.unique(subset=colnames)
