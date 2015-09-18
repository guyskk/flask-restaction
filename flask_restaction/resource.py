# coding:utf-8

from flask.views import View
from flask import request, make_response, current_app
from flask._compat import with_metaclass
from werkzeug.wrappers import Response as ResponseBase
from validater import validate
from validater import ProxyDict
from . import ResourceException, abort, exporters


class ResourceViewType(type):

    """Used to provide standalone::

        before_request_funcs
        after_request_funcs
        handle_error_func

    for each actual Resource class
    """
    def __new__(cls, name, bases, d):
        rv = type.__new__(cls, name, bases, d)
        rv.before_request_funcs = []
        rv.after_request_funcs = []
        # In order to aviod TypeError: unbound method
        # handle_error_func is list with just one item
        # 函数和方法是不同的：
        # 1. 将函数赋给class, class得到的是另一个对象（方法），
        # 这个方法是那个函数被包装之后的对象。
        # 2. 一般方法要使用实例调用，你用类直接调用，
        # 调用的只能是类方法或静态方法。
        rv.handle_error_func = []
        return rv


class Resource(with_metaclass(ResourceViewType, View)):

    """Resource代表一个资源

    - schema_inputs is a dict of scheams for validate inputs.
        it's key is method name
    - schema_outputs is a dict of scheams for validate outputs.
        it's key is method name
    - output_types is a list of custom type of outputs
        , the custom type object will be proxy by validater.ProxyDict
    - before_request_funcs is a list of functions::

        def fn():
            return (rv, [code, headers]) or None

    - after_request_funcs is a list of functions,
        Must return ``tuple(rv, code, headers)``::

            def fn(rv, code, headers):
                return (rv, code, headers) or None

    - handle_error_func is is list with just one function::

        def fn(ex):
            return (rv, [code, headers])

    """

    schema_inputs = {}
    schema_outputs = {}
    output_types = []

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
            rv = cls.handle_error_func[0](ex)
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
        """decorater"""
        cls.after_request_funcs.append(f)
        return f

    @classmethod
    def before_request(cls, f):
        """decorater"""
        cls.before_request_funcs.append(f)
        return f

    @classmethod
    def error_handler(cls, f):
        """decorater"""
        cls.handle_error_func = [f]
        return f

    def dispatch_request(self, *args, **kwargs):
        """preproccess request and dispatch request
        """
        act = request.endpoint.split('@')
        if len(act) > 1:
            meth_name = request.method.lower() + "_" + act[1]
        else:
            meth_name = request.method.lower()
        if not hasattr(self, meth_name) and request.method == 'HEAD':
            meth_name = "get"
        request.resource = self.__class__.__name__.lower()
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
        if isinstance(rv, (ResponseBase, basestring)):
            return make_response(rv, code, headers)
        else:
            if rv is None:
                rv = {}
            mediatype = request.accept_mimetypes.best_match(
                exporters.keys(), default='application/json')
            export = exporters[mediatype]
            return export(rv, code, headers)

    def full_dispatch_request(self, *args, **kwargs):
        """actual dispatch request, validate inputs and outputs
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
        rv, code, headers = unpack(rv)
        if outputs is not None:
            if output_types and isinstance(rv, tuple(output_types)):
                (errors, values) = validate(ProxyDict(rv, output_types), outputs)
            else:
                (errors, values) = validate(rv, outputs)
            if errors:
                abort(500, dict(errors))
            else:
                rv = values
        return rv, code, headers


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
