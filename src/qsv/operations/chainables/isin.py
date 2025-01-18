import sys
import polars as pl
from qsv.utils.DataFrameUtils import exists_colname
from qsv.controllers.LogController import LogController

def isin(df: pl.LazyFrame, colname: str, values: list) -> pl.LazyFrame:
    """[chainable] Filters rows containing the specified values."""
    LogController.debug(f"filter condition: {values} in {colname}")
    if not exists_colname(df=df, colnames=[colname]):
        sys.exit(1)

    return df.filter(pl.col(colname).is_in(values))
