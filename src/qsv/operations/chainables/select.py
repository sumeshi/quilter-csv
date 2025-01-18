import sys
from typing import Union
from qsv.utils.DataFrameUtils import exists_colname
from qsv.controllers.LogController import LogController
import polars as pl

def parse_columns(headers: list[str], colnames: tuple[str]) -> list[str]:
    parsed_columns = list()
    for col in colnames:
        if '-' in col:
            # parse 'startcol-endcol' string
            flag_extract = False
            start, end = col.split('-')
            for h in headers:
                if h == start:
                    flag_extract = True
                if flag_extract:
                    parsed_columns.append(h)
                if h == end:
                    flag_extract = False
        else:
            parsed_columns.append(col)
    return parsed_columns


def select(df: pl.LazyFrame, colnames: Union[str, tuple[str]]) -> pl.LazyFrame:
    """[chainable] Selects only the specified columns."""

    # prevent type guessing
    colnames: tuple[str]
    if type(colnames) is list:
        colnames = tuple(colnames)
    elif type(colnames) is str:
        colnames = (colnames, )

    if not exists_colname(df=df, colnames=colnames):
        sys.exit(1)

    selected_columns = parse_columns(headers=df.collect_schema().names(), colnames=colnames)
    LogController.debug(msg=f"{len(selected_columns)} columns are selected. {', '.join(selected_columns)}")
    return df.select(selected_columns)
