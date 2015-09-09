# coding:utf-8

from flask.views import View
from flask import request, make_response, current_app
from werkzeug.wrappers import Response as ResponseBase
from validater import validate
from validater import ProxyDict
from . import ResourceException, abort, exporters


class Resource(View):

    """Resource代表一个资源"""

    schema_inputs = {}
    schema_outputs = {}
    output_types = []
    before_request_funcs = []
    after_request_funcs = []
    handle_error_func = None

    @classmethod
    def _before_request(cls):
        """before_request"""
        for fn in cls.before_request_funcs:
            rv = fn()
            if rv is not None:
                return rv
        return None

    @classmethod
    def _after_request(cls, rv, code, headers):
        for fn in cls.after_request_funcs:
            rv, code, headers = fn(rv, code, headers)
        return rv, code, headers

    @classmethod
    def _handle_error(cls, ex):
        if cls.handle_error_func:
            rv = cls.handle_error_func(ex)
            if rv is not None:
                return rv
        if isinstance(ex, ResourceException):
            if ex.code >= 500 and not current_app.debug:
                return {"error": "interal server error"}, ex.code
            else:
                return ex.error, ex.code
        else:
            raise ex

    @classmethod
    def after_request(cls, f):
        """装饰器"""
        cls.after_request_funcs.append(f)
        return f

    @classmethod
    def before_request(cls, f):
        """装饰器"""
        cls.before_request_funcs.append(f)
        return f

    @classmethod
    def error_handler(cls, f):
        """装饰器"""
        cls.handle_error_func = f
        return f

    def dispatch_request(self, *args, **kwargs):
        """处理和分发请求
        """
        act = request.endpoint.split('@')
        if len(act) > 1:
            meth_name = request.method.lower() + "_" + act[1]
        else:
            meth_name = request.method.lower()
        if not hasattr(self, meth_name) and request.method == 'HEAD':
            meth_name = "get"
        request.resource = self.__class__.__name__
        request.action = meth_name
        try:
            # before_request
            rv = self._before_request()
            if rv is None:
                rv = self.full_dispatch_request(*args, **kwargs)
        except Exception as ex:
            rv = self._handle_error(ex)
        rv, code, headers = unpack(rv)
        rv, code, headers = self._after_request(rv, code, headers)
        if rv is None:
            return make_response("", code, headers)
        elif isinstance(rv, (ResponseBase, basestring)):
            return make_response(rv, code, headers)
        else:
            mediatype = request.accept_mimetypes.best_match(
                exporters.keys(), default='application/json')
            export = exporters[mediatype]
            return export(rv, code, headers)

    def full_dispatch_request(self, *args, **kwargs):
        """实际处理请求
        """
        fn = getattr(self, request.action, None)
        if fn is None:
            abort(404, 'Unimplemented action %r' % fn.name)
        inputs = self.__class__.schema_inputs.get(request.action)
        outputs = self.__class__.schema_outputs.get(request.action)
        output_types = self.__class__.output_types
        method = request.method.lower()
        if inputs is not None:
            if method in ["get", "delete"]:
                data = request.args.copy()
            elif method in ["post", "put"]:
                if request.headers["Content-Type"] == 'application/json':
                    try:
                        data = request.get_json()
                    except:
                        abort(400, "Invalid json content")
                else:
                    data = request.form.copy()
            else:
                data = {}
            (errors, values) = validate(data, inputs)
            if errors:
                abort(400, dict(errors))
            else:
                rv = fn(**values)
        else:
            rv = fn()
        if outputs is not None:
            if output_types and isinstance(rv, tuple(output_types)):
                (errors, values) = validate(ProxyDict(rv, output_types), outputs)
            else:
                (errors, values) = validate(rv, outputs)
            if errors:
                abort(500, dict(errors))
            else:
                rv = values
        return rv


def unpack(rv):
    """将rv转成(data, code, headers)"""
    status = headers = None
    if isinstance(rv, tuple):
        rv, status, headers = rv + (None,) * (3 - len(rv))
    if isinstance(status, (dict, list)):
        headers, status = status, None
    return (rv, status, headers)
