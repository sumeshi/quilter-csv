from pathlib import Path
import polars as pl

class CsvController(object):
    def __init__(self, path):
        self.path: Path = path

    def get_dataframe(self) -> pl.DataFrame:
        df = pl.scan_csv(
            self.path,
            try_parse_dates=True,
            rechunk=True,
            truncate_ragged_lines=True,
        )
        return df
