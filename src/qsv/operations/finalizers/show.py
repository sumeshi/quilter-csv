import sys
import polars as pl

def show(df: pl.LazyFrame) -> None:
    """[finalizer] Displays the processing results in a table format to standard output."""
    df.collect().write_csv(sys.stdout)
