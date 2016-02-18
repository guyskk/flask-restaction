#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function
from flask import current_app
from flask import json

exporters = {}


def exporter(mediatype):
    """decorater for register exporter

    :param mediatype: mediatype, such as ``application/json``
    """
    def wraper(fn):
        register_exporter(mediatype, fn)
        return fn
    return wraper


def register_exporter(mediatype, fn):
    """register exporter

    :param mediatype: mediatype, such as ``application/json``
    """
    exporters[mediatype] = fn


@exporter('application/json')
def export_json(data, code, header):
    """Creates a :class:`~flask.Response` with the JSON representation of
    the given arguments with an :mimetype:`application/json` mimetype.
    Note: to avoid CSRF attack, don't use cookie to store session.
    see ~ flask json-security

    default indent=2,
    sort_keys when current_app.debug

    :param data: flask.Response or any type object that can dump to json
    :param code: http status code
    :param header: http header
    """

    # sort_keys in debug mode
    sort_keys = current_app.debug

    # Note that we add '\n' to end of response
    # (see https://github.com/mitsuhiko/flask/pull/1262)
    # https://github.com/Runscope/httpbin/issues/168

    # use str("\n") to avoid exception when dumped can't be implicit decode to unicode on PY2
    dumped = json.dumps(data, indent=2,
                        ensure_ascii=False, sort_keys=sort_keys) + str("\n")
    resp = current_app.response_class(
        dumped, status=code, headers=header, mimetype='application/json')

    return resp
