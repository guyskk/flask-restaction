from flask import json, current_app


def output_json(data):
    """Creates a :class:`~flask.Response` with the JSON representation of
    the given arguments with an :mimetype:`application/json` mimetype.
    Note: to avoid CSRF attack, don't use cookie to store session.
    see `flask json-security`
    """

    # sort_keys in debug mode
    sort_keys = current_app.debug

    # Note that we add '\n' to end of response
    # (see https://github.com/mitsuhiko/flask/pull/1262)
    # https://github.com/Runscope/httpbin/issues/168
    rv = current_app.response_class(
        (json.dumps(data, indent=2, sort_keys=sort_keys),
         '\n'),
        mimetype='application/json')
    return rv
