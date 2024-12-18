from rich import box
from rich.table import Table
from rich.console import Console


class TableView(object):
    @staticmethod
    def print(headers: list[str], values: list[list[str]]):
        table = Table(show_header=True, box=box.SQUARE_DOUBLE_HEAD)

        for header in headers:
            table.add_column(header)
        
        for value in values:
            table.add_row(*value)

        console = Console()
        console.print(table)