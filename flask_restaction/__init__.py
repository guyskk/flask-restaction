# coding:utf-8

from __future__ import unicode_literals
from __future__ import absolute_import

"""Flask-Restaction is a powerful flask ext for creat restful api

.. versionchanged:: 0.19.0
   ``ResourceException`` removed.
   ``http_status_code_text`` removed.
   ``abort_if_not_me`` removed.
   ``abort`` removed, use flask.abort instead.
   ``Resource.userrole`` removed, use Api.fn_user_role instead.
"""
import re
import pkg_resources
__version__ = "0.19.6"


import logging
from logging import Formatter
LOG_FORMAT = '[Flask-Restaction] %(asctime)s %(levelname)s: %(message)s'
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setFormatter(Formatter(LOG_FORMAT))
ch.setLevel(logging.WARNING)
logger.addHandler(ch)

pattern_action = re.compile(
    r'^(get|post|put|delete|head|options|trace|patch){1}(?:_(.*))?$')
pattern_endpoint = re.compile(r"^(?:(.*)\.)?(\w*)(?:@(.*))?$")
res_js = pkg_resources.resource_string(__name__, "js/res.js")
res_docs = pkg_resources.resource_string(__name__, "html/res_docs.html")

res_js = res_js.decode("utf-8")
res_docs = res_docs.decode("utf-8")


def unpack(rv):
    """convert rv to tuple(data, code, headers)

    :param rv: data or tuple that contain code and headers
    """
    status = headers = None
    if isinstance(rv, tuple):
        rv, status, headers = rv + (None,) * (3 - len(rv))
    if isinstance(status, (dict, list)):
        headers, status = status, headers
    return (rv, status, headers)


from .exporters import exporters, exporter
from .permission import Permission
from .resource import Resource
from .api import Api
from validater import schema


# __all__ can't be unicode
__all__ = ["Api", "Resource", "schema", "Permission",
           "exporters", "exporter", "__version__"]
__all__ = [str(x) for x in __all__]
