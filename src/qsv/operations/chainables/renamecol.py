import sys
from qsv.utils.DataFrameUtils import exists_colname
import polars as pl

def renamecol(df: pl.LazyFrame, colname: str, new_colname: str) -> pl.LazyFrame:
    """[chainable] Renames the specified column."""
    if not exists_colname(df=df, colnames=[colname]):
        sys.exit(1)

    return df.rename({colname: new_colname})
