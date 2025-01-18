import polars as pl

def stats(df: pl.LazyFrame) -> None:
    """[finalizer] Displays the statistical information of the data."""
    print(df.describe())
