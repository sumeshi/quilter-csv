import re
import sys
import logging
from typing import Union
from datetime import datetime
from pathlib import Path

from qsv.controllers.CsvController import CsvController
from qsv.controllers.QuiltController import QuiltController
from qsv.views.TableView import TableView

import polars as pl


logger = logging.getLogger(__name__)
logger.disabled = True


class DataFrameController(object):
    def __init__(self):
        self.df = None
    
    # -- private methods --
    def __check_exists_path(self, path: tuple[str]) -> None:
        for p in path:
            if not Path(p).exists():
                print(f"[Error] File \"{p}\" does not exist.")
                sys.exit(1)

    def __check_exists_colnames(self, colnames: list[str]) -> None:
        columns = self.df.collect_schema().names()
        for colname in colnames:
            if colname not in columns:
                print(f"[Error] Column \"{colname}\" does not exist in the dataframe.")
                sys.exit(1)

    # -- quilter --
    def quilt(self, config: str, *path: tuple[str], debug: bool = False) -> None:
        """[quilter] Loads the specified quilt batch files."""
        logger.debug(f"config: {config}")
        logger.debug(f"{len(path)} files are loaded. [{', '.join(path)}]")
        q = QuiltController()
        configs = q.load_configs(config)
        q.print_configs(configs)

        for c in configs:
            for k, v in c.get('rules').items():
                # for allow duplicated rulenames.
                k = k if not k.endswith('_') else re.sub(r'_+$', '', k) 

                if debug:
                    print(f"{k}: {v}")

                if k == 'load':
                    self.load(*path)
                elif v:
                    getattr(self, k)(**v)
                else:
                    getattr(self, k)()

                if debug:
                    print(self.df.collect())
                    print()
        
    # -- initializer --
    def load(self, *path: tuple[str], separator: str = ',', low_memory: bool = False):
        """[initializer] Loads the specified CSV files."""
        logger.debug(f"{len(path)} files are loaded. [{', '.join(path)}]")
        self.__check_exists_path(path)
        self.df = CsvController(path=path).get_dataframe(separator=separator, low_memory=low_memory)
        return self

    # -- chainable --
    def select(self, colnames: Union[str, tuple[str]]):
        """[chainable] Selects only the specified columns."""
        def parse_columns(headers: list[str], colnames: tuple[str]):
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
        
        # prevent type guessing
        colnames: tuple[str]
        if type(colnames) is list:
            colnames = tuple(colnames)
        elif type(colnames) is str:
            colnames = (colnames, )
        self.__check_exists_colnames(colnames)
        selected_columns = parse_columns(headers=self.df.collect_schema().names(), colnames=colnames)
        logger.debug(f"{len(selected_columns)} columns are selected. {', '.join(selected_columns)}")
        self.df = self.df.select(selected_columns)
        return self
    
    def isin(self, colname: str, values: list):
        """[chainable] Filters rows containing the specified values."""
        logger.debug(f"filter condition: {values} in {colname}")
        self.__check_exists_colnames([colname])
        self.df = self.df.filter(pl.col(colname).is_in(values))
        return self
    
    def contains(self, colname: str, pattern: str, ignorecase: bool = False):
        """[chainable] Filters rows where the specified column matches the given regex."""
        logger.debug(f"filter condition: {pattern} contains {colname}")
        self.__check_exists_colnames([colname])
        pattern = pattern if type(pattern) is str else str(pattern)
        self.df = self.df.filter(
            pl.col(colname).str.contains(f"(?i){pattern}") if ignorecase else pl.col(colname).str.contains(pattern)
        )
        return self

    def sed(self, colname: str, pattern: str, replacement: str, ignorecase: bool = False):
        """[chainable] Replaces values using the specified regex."""
        logger.debug(f"sed condition: {pattern} on {colname}")
        self.__check_exists_colnames([colname])
        pattern = pattern if type(pattern) is str else str(pattern)
        self.df = self.df.with_columns(
            pl.col(colname).cast(pl.String).str.replace(f"(?i){pattern}", replacement) if ignorecase else pl.col(colname).cast(pl.String).str.replace(pattern, replacement)
        )
        return self
    
    def grep(self, pattern: str, ignorecase: bool = False):
        """[chainable] Treats all columns as strings and filters rows where any column matches the specified regex."""
        self.df = self.df.with_columns(
            pl.concat_str(
                [pl.col(colname).cast(pl.String).fill_null("") for colname in self.df.collect_schema().names()],
                separator=","
            ).alias('___combined')
        )
        self.df = self.df.filter(
            pl.col('___combined').str.contains(f"(?i){pattern}") if ignorecase else pl.col('___combined').str.contains(pattern)
        )
        self.df = self.df.drop(['___combined'])
        return self

    def head(self, number: int = 5):
        """[chainable] Selects only the first N lines."""
        logger.debug(f"heading {number} lines.")
        self.df = self.df.head(number)
        return self

    def tail(self, number: int = 5):
        """[chainable] Selects only the last N lines."""
        logger.debug(f"tailing {number} lines.")
        self.df = self.df.tail(number)
        return self
    
    def sort(self, colnames: Union[str, tuple[str], list[str]], desc: bool = False):
        """[chainable] Sorts all rows by the specified column values."""
        logger.debug(f"sort by {colnames} ({'desc' if desc else 'asc'}).")
        # prevent type guessing
        colnames: tuple[str]
        if type(colnames) is list:
            colnames = tuple(colnames)
        elif type(colnames) is str:
            colnames = (colnames, )
        self.__check_exists_colnames(colnames)
        self.df = self.df.sort(colnames, descending=desc)
        return self
    
    def uniq(self, colnames: Union[str, tuple[str], list[str]]):
        """[chainable] Remove duplicate rows based on the specified column names."""
        logger.debug(f"unique by {colnames}.")
        # prevent type guessing
        colnames: tuple[str]
        if type(colnames) is list:
            colnames = tuple(colnames)
        elif type(colnames) is str:
            colnames = (colnames, )
        self.__check_exists_colnames(colnames)
        self.df = self.df.unique(subset=colnames)
        return self
    
    def changetz(
            self,
            colname: str,
            timezone_from: str = "UTC",
            timezone_to: str = "UTC",
            datetime_format: str = None
        ):
        """[chainable] Changes the timezone of the specified date column."""
        logger.debug(f"change {colname} timezone {timezone_from} to {timezone_to}.")
        self.__check_exists_colnames([colname])

        # convert string to datetime
        if self.df.select(colname).collect_schema().dtypes()[0] != pl.Datetime:
            if datetime_format:
                self.df = self.df.with_columns(pl.col(colname).str.to_datetime(datetime_format))
            else:
                self.df = self.df.with_columns(pl.col(colname).str.to_datetime())

        # setup and change timezone
        self.df = self.df.with_columns(pl.col(colname).dt.replace_time_zone(timezone_from))
        self.df = self.df.with_columns(pl.col(colname).dt.convert_time_zone(timezone_to))
        return self

    def renamecol(self, colname: str, new_colname: str):
        """[chainable] Renames the specified column."""
        self.__check_exists_colnames([colname])
        self.df = self.df.rename({colname: new_colname})
        return self
    
    # -- finalizer --
    def headers(self, plain: bool = False) -> None:
        """[finalizer] Displays the column names of the data."""
        if plain:
            print(",".join([f"\"{c}\"" for c in self.df.collect_schema().names()]))
        else:
            digits = len(str(len(self.df.collect_schema().names())))
            TableView.print(
                headers=[f"{''.join([' ' for _ in range(0, digits-1)])}#", "Column Name"],
                values=[[str(i).zfill(digits), c] for i, c in enumerate(self.df.collect_schema().names())]
            )
    
    def stats(self) -> None:
        """[finalizer] Displays the statistical information of the data."""
        print(self.df.describe())       

    def showquery(self) -> None:
        """[finalizer] Displays the data processing query."""
        print(self.df)

    def show(self) -> None:
        """[finalizer] Displays the processing results in a table format to standard output."""
        self.df.collect().write_csv(sys.stdout)

    def showtable(self) -> None:
        """[finalizer] Outputs the processing results table to the standard output."""
        print(self.df.collect())
    
    def dump(self, path: str = None) -> None:
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
