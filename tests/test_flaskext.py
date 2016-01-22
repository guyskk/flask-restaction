# coding:utf-8

from __future__ import unicode_literals
from __future__ import absolute_import
import pytest

try:
    from flask_restaction import *
except Exception as ex:
    pytest.fail("import * cause exception: " + str(ex))


def test_ext_import():
    from flask_restaction import Api, Resource
