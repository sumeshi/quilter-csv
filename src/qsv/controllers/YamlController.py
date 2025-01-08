import yaml
from pathlib import Path

# for allow duplicate keynames.
def rename_duplicate_keys(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        value = loader.construct_object(value_node, deep=deep)

        new_key = key
        while new_key in mapping:
            new_key += "_"

        mapping[new_key] = value

    return mapping

class YamlController(object):
    def __init__(self):
        yaml.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            rename_duplicate_keys,
            Loader=yaml.SafeLoader
        )

    def load_data(self, path):
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            return data
        