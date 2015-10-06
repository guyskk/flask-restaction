# coding:utf-8

from __future__ import unicode_literals

"""Flask-Restaction is a powerful flask ext for creat restful api"""
from flask import request
import re
import pkg_resources

pattern_action = re.compile(r'^(get|post|put|delete|head|options|trace|patch){1}(?:_(.*))?$')
pattern_endpoint = re.compile(r"^(?:(.*)\.)?(\w*)(?:@(.*))?$")
res_js = pkg_resources.resource_string(__name__, "js/res.js")
res_js = res_js.decode("utf-8")
res_docs = pkg_resources.resource_string(__name__, "html/res_docs.html")
res_docs = res_docs.decode("utf-8")

http_status_code_text = {
    100: "Continue",
    101: "Switching Protocol",
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    300: "Multiple Choice",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    306: "Unused",
    307: "Temporary Redirect",
    308: "Permanent Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Request Entity Too Large",
    414: "Request-URI Too Long",
    415: "Unsupported Media Type",
    416: "Requested Range Not Satisfiable",
    417: "Expectation Failed",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
}


class ResourceException(Exception):

    """RescurceException

    :param code: http status code
    :param error: dict, error message
    """

    def __init__(self, code, error):
        self.code = code
        self.error = error


def abort(code, error=None):
    """raise a RescurceException

    :param code: http status code
    :param error: dict or string, error message
    """

    if error is None and code in http_status_code_text:
        error = http_status_code_text[code]
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
           "exporters", "exporter", "res_docs"]
