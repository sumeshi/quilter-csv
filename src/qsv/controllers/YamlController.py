import yaml
from pathlib import Path

class YamlController(object):
    def __init__(self):
        pass

    def load_data(self, path):
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return data
