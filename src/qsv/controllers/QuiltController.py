from pathlib import Path
from qsv.views.TableView import TableView
from qsv.controllers.YamlController import YamlController

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
        print(f"Loaded {len(configs)} Rules")
        digits = len(str(len(configs)))
        TableView.print(
            headers=[
                f"{''.join([' ' for _ in range(0, digits-1)])}#",
                'title',
                'description',
                'version',
                'author'
            ],
            values=[
                [
                    str(i).zfill(digits),
                    c.get('title'),
                    c.get('description'),
                    c.get('version'),
                    c.get('author')
                ] for i, c in enumerate(configs, 1)
            ]
        )
