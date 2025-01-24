import sys
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


class InvalidRuleException(Exception):
    def __init__(self, title, msg):
        self.title = title
        self.msg = msg

    def __str__(self):
        return f"InvalidRuleException: {self.title}, Reason: {self.msg}"

class YamlController(object):
    def __init__(self):
        yaml.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            rename_duplicate_keys,
            Loader=yaml.SafeLoader
        )

    def load_data(self, path):
        with open(path, 'r') as f:
            try:
                data = yaml.safe_load(f)
                self.verify_rule(data)
                return data
            except InvalidRuleException as e:
                print(e)
                sys.exit(1)
            except yaml.parser.ParserError as e:
                print('yaml.parser.ParserError:')
                print(e)
                sys.exit(1)
        
    def verify_rule(self, data: dict):
        title = data.get('title', 'UNDEFINED')
        stages = data.get('stages')

        # check for existing stages
        if not stages:
            raise InvalidRuleException(title, "No stages defined")

        # check for duplicated stage names
        if not len(stages.keys()) == len(set(stages.keys())):
            raise InvalidRuleException(title, "Stage name is duplicated.")

        # check for malformed stages
        for sk, sv in stages.items():
            stage_type = sv.get('type')
            if not stage_type:
                raise InvalidRuleException(title, f"[{sk}] Stage type is undefined.")
            
            if stage_type == 'process':
                if not sv.get('steps'):
                    raise InvalidRuleException(title, f"[{sk}] Parameter steps is undefined.")

            if stage_type == 'join' or stage_type == 'concat':
                if not sv.get('sources'):
                    raise InvalidRuleException(title, f"[{sk}] Parameter sources is undefined.")
