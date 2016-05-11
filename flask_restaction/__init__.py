#!/usr/bin/env python
# coding: utf-8
"""Flask-Restaction is a powerful flask ext for creat restful api

.. versionchanged:: 0.19.0
   ``ResourceException`` removed.
   ``http_status_code_text`` removed.
   ``abort_if_not_me`` removed.
   ``abort`` removed, use flask.abort instead.
   ``Resource.userrole`` removed, use Api.fn_user_role instead.
"""
from __future__ import absolute_import, print_function
import re
import pkg_resources

__flask_restaction__ = pkg_resources.get_distribution("flask_restaction")
__version__ = __flask_restaction__.version

import logging
LOG_FORMAT = '[Flask-Restaction] %(asctime)s %(levelname)s: %(message)s'
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter(LOG_FORMAT))
ch.setLevel(logging.WARNING)
logger.addHandler(ch)

pattern_action = re.compile(
    r'^(get|post|put|delete|head|options|trace|patch){1}(?:_(.*))?$')
pattern_endpoint = re.compile(r"^(?:(.*)\.)?(\w*)(?:@(.*))?$")


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
from .resource import Resource
from .api import Api
from .permission import Permission
from .apiinfo import ApiInfo, Gen
from .auth import Auth
from .res import Res

__all__ = ["Api", "Resource", "Auth", "exporters", "exporter",
           "Gen", "Res", "Permission", "ApiInfo"]
