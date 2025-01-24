from typing import Union

from qsv.operations.initializers import *
from qsv.operations.chainables import *
from qsv.operations.finalizers import *
from qsv.operations.quilters import *


class DataFrameController(object):
    def __init__(self):
        self.df = None
        
    # -- initializers --
    def load(self, *path: tuple[str], separator: str = ',', low_memory: bool = False):
        self.df = load(path=path, separator=separator, low_memory=low_memory)
        return self

    # -- chainables --
    def select(self, colnames: Union[str, tuple[str]]):
        self.df = select(df=self.df, colnames=colnames)
        return self
    
    def isin(self, colname: str, values: list):
        self.df = isin(df=self.df, colname=colname, values=values)
        return self
    
    def contains(self, colname: str, pattern: str, ignorecase: bool = False):
        self.df = contains(df=self.df, colname=colname, pattern=pattern, ignorecase=ignorecase)
        return self

    def sed(self, colname: str, pattern: str, replacement: str, ignorecase: bool = False):
        self.df = sed(df=self.df, colname=colname, pattern=pattern, replacement=replacement, ignorecase=ignorecase)
        return self
    
    def grep(self, pattern: str, ignorecase: bool = False):
        self.df = grep(df=self.df, pattern=pattern, ignorecase=ignorecase)
        return self

    def head(self, number: int = 5):
        self.df = head(df=self.df, number=number)
        return self

    def tail(self, number: int = 5):
        self.df = tail(df=self.df, number=number)
        return self
    
    def sort(self, colnames: Union[str, tuple[str], list[str]], desc: bool = False):
        self.df = sort(df=self.df, colnames=colnames, desc=desc)
        return self
    
    def count(self):
        self.df = count(df=self.df)
        return self
    
    def uniq(self, colnames: Union[str, tuple[str], list[str]]):
        self.df = uniq(df=self.df, colnames=colnames)
        return self
    
    def changetz(self, colname: str, tz_from: str = "UTC", tz_to: str = "UTC", dt_format: str = None):
        self.df = changetz(df=self.df, colname=colname, tz_from=tz_from, tz_to=tz_to, dt_format=dt_format)
        return self

    def renamecol(self, colname: str, new_colname: str):
        self.df = renamecol(df=self.df, colname=colname, new_colname=new_colname)
        return self

    def drop(self):
        self.df = None
        return self
    
    # -- finalizer --
    def headers(self, plain: bool = False) -> None:
        headers(df=self.df, plain=plain)
    
    def stats(self) -> None:
        stats(df=self.df)

    def showquery(self) -> None:
        showquery(df=self.df)

    def show(self) -> None:
        show(df=self.df)

    def showtable(self) -> None:
        showtable(df=self.df)
    
    def dump(self, path: str = None) -> None:
        dump(df=self.df, path=path)

    # -- quilter --
    def quilt(self, config: str, *path: tuple[str], debug: bool = False) -> None:
        quilt(dfc=self, config=config, path=path, debug=debug)

    def quilt_visualize(self, config: str) -> None:
        quilt_visualize(config=config)
    
    def __str__(self):
        if self.df is not None:
            print(self.df.collect())
        return ''
