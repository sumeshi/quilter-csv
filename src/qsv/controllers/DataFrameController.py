import re
import sys
import logging
from datetime import datetime
from typing import Union

from qsv.controllers.CsvController import CsvController
from qsv.views.TableView import TableView

import polars as pl


logger = logging.getLogger(__name__)


class DataFrameController(object):
    def __init__(self, logging=False):
        self.df = None

        if logging:
            logger.disabled = True
    
    # -- initializer --
    def load(self, *path: str):
        """[initializer] Loads the specified CSV files."""
        logger.debug(f"{len(path)} files are loaded. {', '.join(path)}")
        self.df = CsvController(path=path).get_dataframe()
        return self

    # -- chainable --
    def select(self, columns: Union[str, tuple[str]]):
        """[chainable] Displays the specified columns."""
        def parse_columns(headers: list[str], columns: Union[str, tuple[str]]):
            # prevent type guessing
            columns: tuple[str] = columns if type(columns) is tuple else (columns, )

            parsed_columns = list()
            for col in columns:
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
        
        selected_columns = parse_columns(headers=self.df.columns, columns=columns)
        logger.debug(f"{len(selected_columns)} columns are selected. {', '.join(selected_columns)}")
        self.df = self.df.select(selected_columns)
        return self
    
    def isin(self, colname: str, values: list):
        """[chainable] Displays rows that contain the specified values."""
        logger.debug(f"filter condition: {values} in {colname}")
        self.df = self.df.filter(pl.col(colname).is_in(values))
        return self
    
    def contains(self, colname: str, regex: str):
        """[chainable] Displays rows that contain the specified string."""
        logger.debug(f"filter condition: {regex} contains {colname}")
        regex = regex if type(regex) is str else str(regex)
        self.df = self.df.filter(pl.col(colname).str.contains(regex))
        return self

    def head(self, number: int = 5):
        """[chainable] Displays the first specified number of rows of the data."""
        logger.debug(f"heading {number} lines.")
        self.df = self.df.head(number)
        return self

    def tail(self, number: int = 5):
        """[chainable] Displays the last specified number of rows of the data."""
        logger.debug(f"tailing {number} lines.")
        self.df = self.df.tail(number)
        return self
    
    def sort(self, columns: str, desc: bool = False):
        """[chainable] Sorts the data by the values of the specified column."""
        logger.debug(f"sort by {columns} ({'desc' if desc else 'asc'}).")
        self.df = self.df.sort(columns, descending=desc)
        return self
    
    def changetz(self, colname: str, timezone_from: str = "UTC", timezone_to: str = "Asia/Tokyo", new_colname: str = None):
        """[chainable] Changes the timezone of the specified date column."""
        logger.debug(f"change {colname} timezone {timezone_from} to {timezone_to}.")
        new_colname = new_colname if new_colname else colname
        self.df.with_columns(pl.col(colname).dt.replace_time_zone(timezone_from))
        self.df = self.df.with_columns(
            pl.col(colname).cast(pl.Datetime).dt.convert_time_zone(timezone_to).alias(new_colname)
        )
        return self
    
    # -- finalizer --
    def headers(self, plain: bool = False):
        """[finalizer] Displays the column names of the data."""
        if plain:
            print(",".join([f"\"{c}\"" for c in self.df.columns]))
        else:
            TableView.print(
                headers=["#", "Column Name"],
                values=[[str(i).zfill(2), c] for i, c in enumerate(self.df.columns)]
            )
    
    def stats(self):
        """[finalizer] Displays the statistical information of the data."""
        print(self.df.describe())       

    def showquery(self):
        """[finalizer] Displays the data processing query."""
        print(self.df)

    def show(self):
        """[finalizer] Outputs the processing results to the standard output."""
        self.df.collect().write_csv(sys.stdout)
    
    def dump(self, path: str = None):
        """[finalizer] Outputs the processing results to a CSV file."""
        def autoname():
            now = datetime.now().strftime('%Y%m%d-%H%M%S')
            query = self.df.explain(optimized=False).splitlines()[0]
            temp = re.sub(r'[^\w\s]', '-', query)
            temp = re.sub(r'-+', '-', temp)
            temp = temp.strip('-')
            temp = temp.replace(' ', '')
            temp = temp.lower()
            return f"{now}_{temp}.csv"

        path = path if path else autoname()
        self.df.collect().write_csv(path)
        logger.info(f"csv dump successfully: {path}")
    
    def __str__(self):
        if self.df is not None:
            print(self.df.collect())
        return ''
