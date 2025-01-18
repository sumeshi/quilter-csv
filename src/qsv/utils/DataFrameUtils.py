import polars as pl
from qsv.controllers.LogController import LogController

def exists_colname(df: pl.LazyFrame, colnames: list[str]) -> bool:
    columns = df.collect_schema().names()
    for colname in colnames:
        if colname not in columns:
            LogController.error(f"Column \"{colname}\" does not exist in the dataframe.")
            return False
    else:
        return True
