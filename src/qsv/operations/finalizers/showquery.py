import polars as pl

def showquery(df: pl.LazyFrame) -> None:
    """[finalizer] Displays the data processing query."""
    print(df)
