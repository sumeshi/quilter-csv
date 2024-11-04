import re
import sys
import logging
from datetime import datetime
from typing import Union

from qsv.controllers.CsvController import CsvController
from qsv.controllers.QuiltController import QuiltController
from qsv.views.TableView import TableView

import polars as pl


logger = logging.getLogger(__name__)
logger.disabled = True


class DataFrameController(object):
    def __init__(self):
        self.df = None

    # -- quilter --
    def quilt(self, config: str, *path: str):
        """[quilter] Loads the specified quilt batch files."""
        logger.debug(f"config: {config}")
        logger.debug(f"{len(path)} files are loaded. [{', '.join(path)}]")
        q = QuiltController()
        configs = q.load_configs(config)
        q.print_configs(configs)

        for c in configs:
            for k, v in c.get('rules').items():
                if k == 'load':
                    self.load(*path)
                elif v:
                    getattr(self, k)(**v)
                else:
                    getattr(self, k)()
        
    # -- initializer --
    def load(self, *path: str):
        """[initializer] Loads the specified CSV files."""
        logger.debug(f"{len(path)} files are loaded. [{', '.join(path)}]")
        self.df = CsvController(path=path).get_dataframe()
        return self

    # -- chainable --
    def select(self, columns: Union[str, tuple[str]]):
        """[chainable] Filter only on the specified columns."""
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
        
        # for quilter
        columns = tuple(columns) if type(columns) is list else columns

        selected_columns = parse_columns(headers=self.df.collect_schema().names(), columns=columns)
        # selected_columns = parse_columns(headers=self.df.columns, columns=columns)
        logger.debug(f"{len(selected_columns)} columns are selected. {', '.join(selected_columns)}")
        self.df = self.df.select(selected_columns)
        return self
    
    def isin(self, colname: str, values: list):
        """[chainable] Filter rows containing the specified values."""
        logger.debug(f"filter condition: {values} in {colname}")
        self.df = self.df.filter(pl.col(colname).is_in(values))
        return self
    
    def contains(self, colname: str, regex: str):
        """[chainable] Filter rows containing the specified regex."""
        logger.debug(f"filter condition: {regex} contains {colname}")
        regex = regex if type(regex) is str else str(regex)
        self.df = self.df.filter(pl.col(colname).str.contains(regex))
        return self

    def sed(self, colname: str, regex: str, replaced_text: str):
        """[chainable] Replace values by specified regex."""
        logger.debug(f"sed condition: {regex} on {colname}")
        regex = regex if type(regex) is str else str(regex)
        self.df = self.df.with_columns(pl.col(colname).cast(pl.String).str.replace(regex, replaced_text))
        return self

    def head(self, number: int = 5):
        """[chainable] Filters only the specified number of lines from the first line."""
        logger.debug(f"heading {number} lines.")
        self.df = self.df.head(number)
        return self

    def tail(self, number: int = 5):
        """[chainable] Filters only the specified number of lines from the last line."""
        logger.debug(f"tailing {number} lines.")
        self.df = self.df.tail(number)
        return self
    
    def sort(self, columns: str, desc: bool = False):
        """[chainable] Sorts all rows by the specified column values."""
        logger.debug(f"sort by {columns} ({'desc' if desc else 'asc'}).")
        self.df = self.df.sort(columns, descending=desc)
        return self
    
    def changetz(
            self,
            colname: str,
            timezone_from: str = "UTC",
            timezone_to: str = "Asia/Tokyo",
            datetime_format: str = None
        ):
        """[chainable] Changes the timezone of the specified date column."""
        logger.debug(f"change {colname} timezone {timezone_from} to {timezone_to}.")

        if datetime_format:
            self.df = self.df.with_columns(pl.col(colname).str.to_datetime(datetime_format))
        else:
            self.df = self.df.with_columns(pl.col(colname).str.to_datetime())

        self.df = self.df.with_columns(pl.col(colname).dt.replace_time_zone(timezone_from))
        self.df = self.df.with_columns(pl.col(colname).dt.convert_time_zone(timezone_to))
        return self

    def renamecol(self, colname: str, new_colname: str):
        """[chainable] Rename specified column name."""
        self.df = self.df.rename({colname: new_colname})
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

    def showtable(self):
        """[finalizer] Outputs the processing results table to the standard output."""
        print(self.df.collect())
    
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
