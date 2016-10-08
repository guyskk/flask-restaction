import yaml
from collections import OrderedDict
from yaml import *  # noqa


class SimpleLoader(yaml.SafeLoader):
    """Simple, Ordered and Safe Loader.

    1. treat '@', '&', '*' as plain string, anchors and aliases are disabled
    2. load YAML mapping as OrderedDict
    3. use SafeLoader

    About implements:
    http://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts
    https://github.com/yaml/pyyaml/blob/master/lib3/yaml/scanner.py
    """

    def fetch_alias(self):
        return self.fetch_plain()

    def fetch_anchor(self):
        return self.fetch_plain()

    def check_plain(self):
        # Modified: allow '@'
        if self.peek() == '@':
            return True
        else:
            return super().check_plain()


def construct_mapping(loader, node):
    loader.flatten_mapping(node)
    return OrderedDict(loader.construct_pairs(node))

SimpleLoader.add_constructor(
    yaml.Loader.DEFAULT_MAPPING_TAG,
    construct_mapping
)


def load(stream):
    return yaml.load(stream, SimpleLoader)
