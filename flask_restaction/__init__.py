# coding:utf-8
from flask import request
import re
import pkg_resources

pattern_action = re.compile(ur'^(get|post|put|delete|head|options|trace|patch){1}(?:_(.*))?$')
res_js = pkg_resources.resource_string(__name__, "js/res.js")
res_js = res_js.decode("utf-8")


class ResourceException(Exception):

    """docstring for RescurceException"""

    def __init__(self, code, error):
        self.code = code
        self.error = error


def abort(code, error):
    if isinstance(error, basestring):
        error = {"error": error}
    raise ResourceException(code, error)


def abort_if_not_me(_id):
    if request.me["id"] != _id:
        raise ResourceException(403, {"error": "permission deny"})

from exporters import exporters, exporter
from permission import Permission
from resource import Resource
from api import Api
__all__ = ["Api", "Resource", "Permission", "abort",
           "abort_if_not_me", "ResourceException",
           "exporters", "exporter"]
