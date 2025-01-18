import polars as pl

def grep(df: pl.LazyFrame, pattern: str, ignorecase: bool = False) -> pl.LazyFrame:
    """[chainable] Treats all columns as strings and filters rows where any column matches the specified regex."""
    df = df.with_columns(
        pl.concat_str(
            [pl.col(colname).cast(pl.String).fill_null("") for colname in df.collect_schema().names()],
            separator=","
        ).alias('___combined')
    )
    df = df.filter(
        pl.col('___combined').str.contains(f"(?i){pattern}") if ignorecase else pl.col('___combined').str.contains(pattern)
    )
    df = df.drop(['___combined'])
    return df
