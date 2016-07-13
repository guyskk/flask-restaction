from flask import current_app
from flask import json

exporters = {}


def exporter(mediatype):
    """Decorater for register exporter

    :param mediatype: mediatype, eg: ``application/json``
    """
    def wraper(fn):
        register_exporter(mediatype, fn)
        return fn
    return wraper


def register_exporter(mediatype, fn):
    """Register exporter

    :param mediatype: mediatype, eg: ``application/json``
    """
    exporters[mediatype] = fn


@exporter('application/json')
def export_json(data, status, headers):
    """Creates a JSON response

    :param data: flask.Response or any type object that can dump to json
    :param status: http status code
    :param headers: http headers
    """
    dumped = json.dumps(data, indent=2, ensure_ascii=False)
    resp = current_app.response_class(
        dumped, status=status, headers=headers, mimetype='application/json')
    return resp
