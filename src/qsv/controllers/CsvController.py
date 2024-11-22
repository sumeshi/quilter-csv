from pathlib import Path
import polars as pl

class CsvController(object):
    def __init__(self, path):
        self.path: Path = path

    def get_dataframe(self, separator: str = ',', low_memory: bool = False) -> pl.DataFrame:
        df = pl.scan_csv(
            self.path,
            try_parse_dates=True,
            rechunk=True,
            truncate_ragged_lines=True,
            separator=separator,
            low_memory=low_memory,
        )
        return df
