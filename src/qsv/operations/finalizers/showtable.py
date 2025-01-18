import polars as pl

def showtable(df: pl.LazyFrame) -> None:
    """[finalizer] Outputs the processing results table to the standard output."""
    print(df.collect())
