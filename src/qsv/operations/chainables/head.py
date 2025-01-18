import polars as pl
from qsv.controllers.LogController import LogController

def head(df: pl.LazyFrame, number: int = 5) -> pl.LazyFrame:
    """[chainable] Selects only the first N lines."""
    LogController.debug(f"heading {number} lines.")
    return df.head(number)
