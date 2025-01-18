import sys
import polars as pl
from qsv.utils.DataFrameUtils import exists_colname
from qsv.controllers.LogController import LogController

def changetz(df: pl.LazyFrame, colname: str, tz_from: str = "UTC", tz_to: str = "UTC", dt_format: str = None) -> pl.LazyFrame:
    """[chainable] Changes the timezone of the specified date column."""
    # convert string to datetime
    if df.select(colname).collect_schema().dtypes()[0] != pl.Datetime:
        if dt_format:
            df = df.with_columns(pl.col(colname).str.to_datetime(dt_format))
        else:
            df = df.with_columns(pl.col(colname).str.to_datetime())

    if not exists_colname(df=df, colnames=[colname]):
        sys.exit(1)

    LogController.debug(f"change {colname} timezone {tz_from} to {tz_to}.")

    # setup and change timezone
    df = df.with_columns(pl.col(colname).dt.replace_time_zone(tz_from))
    df = df.with_columns(pl.col(colname).dt.convert_time_zone(tz_to))
    return df
