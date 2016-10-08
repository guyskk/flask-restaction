import pytest
from collections import OrderedDict
from flask_restaction import simple_yaml as yaml


def test_order():
    yamltext = """
        a:
            x: 1
            y: 2
            z: 3
        b: 0
        c: 0
        d: 0
    """
    for i in range(100):
        data = yaml.load(yamltext)
        assert isinstance(data, OrderedDict)
        assert isinstance(data['a'], OrderedDict)
        assert list(data['a'].items()) == [('x', 1), ('y', 2), ('z', 3)]
        del data['a']
        assert list(data.items()) == [('b', 0), ('c', 0), ('d', 0)]


@pytest.mark.parametrize("text", [
    '@user', '&user', '*user',
    """
    friends:
        - @user
    """,
    'userid: @userid',
    '&optional&unique'
])
def test_special_yaml_char(text):
    yaml.load(text)


def test_anchors_aliases():
    text = """
    left hand: &A
      name: The Bastard Sword of Eowyn
      weight: 30
    right hand: *A
    """
    with pytest.raises(yaml.YAMLError):
        yaml.load(text)
