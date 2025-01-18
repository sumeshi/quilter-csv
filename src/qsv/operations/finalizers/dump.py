import re
from datetime import datetime
from qsv.controllers.LogController import LogController
import polars as pl

def autoname(df: pl.LazyFrame) -> str:
    now = datetime.now().strftime('%Y%m%d-%H%M%S')
    query = df.explain(optimized=False).splitlines()[0]
    temp = re.sub(r'[^\w\s]', '-', query)
    temp = re.sub(r'-+', '-', temp)
    temp = temp.strip('-')
    temp = temp.replace(' ', '')
    temp = temp.lower()
    return f"{now}_{temp}.csv"


def dump(df: pl.LazyFrame, path: str = None) -> None:
    """[finalizer] Outputs the processing results to a CSV file."""
    path = path if path else autoname(df=df)
    df.collect().write_csv(path)
    LogController.info(f"csv dump successfully: {path}")
