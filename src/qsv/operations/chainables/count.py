import polars as pl
from typing import Union
from qsv.utils.DataFrameUtils import exists_colname
from qsv.controllers.LogController import LogController

def count(df: pl.LazyFrame) -> pl.LazyFrame:
    """[chainable] Count duplicate rows in the DataFrame."""
    LogController.debug("Counting all duplicate rows")
    return df.group_by(df.collect_schema().names()).agg(pl.count().alias("Count"))
