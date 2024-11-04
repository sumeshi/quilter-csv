from pathlib import Path
import polars as pl

from qsv.controllers.YamlController import YamlController
from qsv.views.TableView import TableView

class QuiltController(object):
    def __init__(self):
        pass

    def load_configs(self, config) -> list[dict]:
        configs = list()
        if Path(config).is_dir():
            # I think the yaml format is great, the only drawback is that it has two extensions, .yaml and .yml.
            for f in Path(config).glob("**/*.yaml"):
                configs.append(YamlController().load_data(f))
            for ff in Path(config).glob("**/*.yml"):
                configs.append(YamlController().load_data(ff))
        else:
            configs.append(YamlController().load_data(Path(config)))

        return configs

    def print_configs(self, configs: list[dict]):
        print('Loaded Rules')
        TableView.print(
            headers=['title', 'description', 'version', 'author'],
            values=[[
                c.get('title'),
                c.get('description'),
                c.get('version'),
                c.get('author')
            ] for c in configs]
        )
