from qsv.views.TableView import TableView
import polars as pl

def headers(df=pl.LazyFrame, plain: bool = False) -> None:
    """[finalizer] Displays the column names of the data."""
    if plain:
        print(",".join([f"\"{c}\"" for c in df.collect_schema().names()]))
    else:
        digits = len(str(len(df.collect_schema().names())))
        TableView.print(
            headers=[f"{''.join([' ' for _ in range(0, digits-1)])}#", "Column Name"],
            values=[[str(i).zfill(digits), c] for i, c in enumerate(df.collect_schema().names())]
        )
