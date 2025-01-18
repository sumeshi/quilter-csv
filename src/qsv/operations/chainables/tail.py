import polars as pl
from qsv.controllers.LogController import LogController

def tail(df: pl.LazyFrame, number: int = 5) -> pl.LazyFrame:
    """[chainable] Selects only the last N lines."""
    LogController.debug(f"tailing {number} lines.")
    return df.tail(number)
