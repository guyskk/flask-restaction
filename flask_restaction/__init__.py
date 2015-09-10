# coding:utf-8

"""Flask-Restaction is a powerful flask ext for creat restful api"""
from flask import request
import re
import pkg_resources

pattern_action = re.compile(ur'^(get|post|put|delete|head|options|trace|patch){1}(?:_(.*))?$')
res_js = pkg_resources.resource_string(__name__, "js/res.js")
res_js = res_js.decode("utf-8")


class ResourceException(Exception):

    """RescurceException

    :param code: http status code
    :param error: dict, error message
    """

    def __init__(self, code, error):
        self.code = code
        self.error = error


def abort(code, error):
    """raise a RescurceException

    :param code: http status code
    :param error: dict or string, error message
    """
    if isinstance(error, basestring):
        error = {"error": error}
    raise ResourceException(code, error)


def abort_if_not_me(_id):
    """``if request.me["id"] != _id``, 
    raise a RescurceException with code 403"""
    if request.me["id"] != _id:
        raise ResourceException(403, {"error": "permission deny"})

from exporters import exporters, exporter
from permission import Permission
from resource import Resource
from api import Api
__all__ = ["Api", "Resource", "Permission", "abort",
           "abort_if_not_me", "ResourceException",
           "exporters", "exporter"]
