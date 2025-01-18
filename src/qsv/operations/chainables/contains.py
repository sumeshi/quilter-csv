import sys
from qsv.utils.DataFrameUtils import exists_colname
from qsv.controllers.LogController import LogController
import polars as pl

def contains(df: pl.LazyFrame, colname: str, pattern: str, ignorecase: bool = False) -> pl.LazyFrame:
    """[chainable] Filters rows where the specified column matches the given regex."""
    if not exists_colname(df=df, colnames=[colname]):
        sys.exit(1)
    
    LogController.debug(f"filter condition: {pattern} contains {colname}")
    pattern = pattern if type(pattern) is str else str(pattern)
    return df.filter(
        pl.col(colname).str.contains(f"(?i){pattern}") if ignorecase else pl.col(colname).str.contains(pattern)
    )
