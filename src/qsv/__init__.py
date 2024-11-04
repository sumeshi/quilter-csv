import logging
import fire
from qsv.controllers.DataFrameController import DataFrameController

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    handlers=[
        logging.StreamHandler()
    ]
)

# entrypoint
def main():
    fire.Fire(DataFrameController)

if __name__ == '__main__':
    main()