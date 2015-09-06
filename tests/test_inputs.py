# coding:utf-8
from flask_restaction import validate, addvalidater
from datetime import datetime


def test_126():
    s1 = {
        "desc": "desc of the key",
        "required": True,
        "validate": "int",
        "default": "321",
    }
    obj1 = "sda"
    s2 = [{
        "desc": "desc of the key",
        "required": True,
        "validate": "int",
        "default": "321",
    }]
    obj2 = ["sda", 1, 2, 3]
    s6 = [{
        "key1": {
            "desc": "desc of the key",
            "required": True,
            "validate": "int",
            "default": "321",
        }
    }]
    obj6 = [{
        "key1": "123"
    }, {
        "key": "123"
    }, {
        "key1": "asd"
    }, {
        "kkk": "1234"
    }]
    print validate(obj1, s1)
    print validate(obj2, s2)
    print validate(obj6, s6)


def test_345():
    schema3 = {
        "key1": {
            "desc": "desc of the key",
            "required": True,
            "validate": "int",
            "default": "321",
        },
        "key2": {
            "desc": "desc of the key",
            "required": True,
            "validate": "str",
        },
        "key3": {
            "desc": "desc of the key",
            "required": True,
            "validate": "datetime",
            "default": "",
        }
    }
    obj3 = {
        "key1": "123",
        "key2": u"haha",
        "key3": "2015-9-1 14:42:35"
    }

    schema4 = {
        "key1": [{
            "desc": "desc of the key",
            "required": True,
            "validate": "int",
            "default": "321",
        }]
    }
    obj4 = {
        "key1": ["123", "32", "asd"]
    }

    schema5 = {
        "key1": {
            "desc": "desc of the key",
            "required": True,
            "validate": "int",
            "default": "321",
        },
        "key2": [{
            "desc": "desc of the key",
            "required": True,
            "validate": "int",
        }],
        "key3": {
            "key1": {
                "desc": "desc of the key",
                "required": True,
                "validate": "int",
            },
            "key2": [{
                "desc": "desc of the key",
                "required": True,
                "validate": "int",
            }],
            "key3": {
                "desc": "desc of the key",
                "required": True,
                "validate": "int",
            },
            "key4": {
                "desc": "desc of the key",
                "validate": "int",
            },
        }
    }
    obj5 = {
        "key1": "123",
        "key2": ["123", "32", "asd"],
        "key3": {
            "key1": "123",
            "key2": ["123", "32", "asd"],
        }
    }
    print validate(obj3, schema3)
    print validate(obj4, schema4)
    print validate(obj5, schema5)


def test_addvalidater():
    def plus_int(v):
        try:
            return (True, int(v) > 0)
        except:
            return (False, None)
    addvalidater("+int", plus_int)

    s = {
        "key": [{
            "desc": "datetime",
            "required": True,
            "validate": "+int"
        }]
    }
    obj = {"key": ["123", "0", "-123"]}
    print validate(obj, s)


def test_default():
    s = {
        "key": {
            "desc": "datetime",
            "required": True,
            "validate": "datetime",
            "default": datetime.utcnow
        }
    }
    obj = {"key": None}
    print validate(obj, s)


if __name__ == '__main__':
    test_126()
    test_345()
    test_default()
    test_addvalidater()
