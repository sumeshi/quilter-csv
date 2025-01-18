import sys
import polars as pl
from qsv.utils.DataFrameUtils import exists_colname
from qsv.controllers.LogController import LogController

def sed(df: pl.LazyFrame, colname: str, pattern: str, replacement: str, ignorecase: bool = False) -> pl.LazyFrame:
    """[chainable] Replaces values using the specified regex."""
    if not exists_colname(df=df, colnames=[colname]):
        sys.exit(1)

    LogController.debug(f"sed condition: {pattern} on {colname}")
    pattern = pattern if type(pattern) is str else str(pattern)
    return df.with_columns(
        pl.col(colname).cast(pl.String).str.replace(f"(?i){pattern}", replacement) if ignorecase else pl.col(colname).cast(pl.String).str.replace(pattern, replacement)
    )
