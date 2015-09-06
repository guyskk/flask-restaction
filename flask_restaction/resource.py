# coding:utf-8

from flask.views import View
from flask import request, make_response, current_app
from werkzeug.wrappers import Response as ResponseBase
from validater import validate
from validater import ProxyDict
from . import ResourceException, abort, output_json

# Authorization


class Resource(View):

    """docstring for Resource"""

    schema_inputs = {}
    schema_outputs = {}
    types = []
    before_request_funcs = []
    after_request_funcs = []
    error_handler = None

    def _before_request(self):
        """before_request"""
        if self.__class__.before_request_funcs:
            for fn in self.__class__.before_request_funcs:
                rv = fn()
                if rv is not None:
                    return rv
        return None

    def _after_request(self, rv, code, headers):
        if self.__class__.after_request_funcs:
            for fn in self.__class__.after_request_funcs:
                rv, code, headers = fn(rv, code, headers)
        return rv, code, headers

    def _handle_error(self, ex):
        if self.__class__.error_handler:
            rv = self.__class__.error_handler(ex)
            if rv is not None:
                return rv
        if isinstance(ex, ResourceException):
            if ex.code >= 500 and not current_app.debug:
                return {"error": "interal server error"}, ex.code
            else:
                return ex.error, ex.code
        else:
            raise ex

    def dispatch_request(self, *args, **kwargs):
        """
        """
        act = request.endpoint.split('@')
        if len(act) > 1:
            meth_name = request.method.lower() + "_" + act[1]
        else:
            meth_name = request.method.lower()

        meth = getattr(self, meth_name, None)
        if meth is None and request.method == 'HEAD':
            meth_name = "get"
            meth = getattr(self, meth_name, None)
        request.resource = self.__class__.__name__
        request.action = meth_name
        inputs = self.__class__.schema_inputs.get(meth_name)
        outputs = self.__class__.schema_outputs.get(meth_name)
        types = self.__class__.types
        # before_request
        rv = self._before_request()
        if rv is None:
            try:
                rv = self._call_action(meth, meth_name, inputs, outputs, types)
            except Exception as ex:
                # handle_error
                rv = self._handle_error(ex)
        rv, code, headers = expand_rv(rv)
        # after_request
        (rv, code, headers) = self._after_request(rv, code, headers)
        if rv is None:
            return make_response("", code, headers)
        elif isinstance(rv, ResponseBase) or isinstance(rv, basestring):
            return make_response(rv, code, headers)
        else:
            return make_response(output_json(rv), code, headers)

    def _call_action(self, fn, meth_name, inputs, outputs, types):
        if fn is None:
            abort(404, {"error": 'Unimplemented method %r' % meth_name})
        method = request.method.lower()
        if inputs is not None:
            if method in ["get", "delete"]:
                data = request.args.copy()
            elif method in ["post", "put"]:
                if request.headers["Content-Type"] == 'application/json':
                    try:
                        data = request.get_json()
                    except:
                        abort(400, {"error": "request content isn't valid json"})
                else:
                    data = request.form.copy()
            else:
                data = {}
            (errors, values) = validate(data, inputs)
            if errors:
                abort(400, dict(errors))
            else:
                r = fn(**values)
        else:
            r = fn()
        if outputs is not None:
            if types and isinstance(r, tuple(types)):
                (errors, values) = validate(ProxyDict(r, types), outputs)
            else:
                (errors, values) = validate(r, outputs)
            if errors:
                abort(500, dict(errors))
            else:
                r = values
        return r


def expand_rv(rv):
    status = headers = None
    if isinstance(rv, tuple):
        rv, status, headers = rv + (None,) * (3 - len(rv))
    if isinstance(status, (dict, list)):
        headers, status = status, None
    return (rv, status, headers)
