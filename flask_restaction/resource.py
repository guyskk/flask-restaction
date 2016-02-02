#!/usr/bin/env python
# coding: utf-8
"""
    flask_restaction.resource
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. versionadded:: 0.18.0
       Support tuple_like schema, The ``schema,parse_schema,combine_schema``
       function was added.
"""
from __future__ import unicode_literals, absolute_import, print_function
import six
from flask.views import View
from flask import g, abort
from validater import validate
from . import unpack


class ResourceViewType(type):
    """Used to provide standalone callback functions
       for each actual Resource class::

        before_request_funcs
        after_request_funcs
        handle_error_func
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


class Resource(six.with_metaclass(ResourceViewType, View)):

    """Resource代表一个资源

    - schema_inputs is a dict of scheams for validate inputs.
        it's key is method name
    - schema_outputs is a dict of scheams for validate outputs.
        it's key is method name
    - output_types is a list of custom type of outputs
        , the custom type object will be proxy by validater.ProxyDict
    - before_request_funcs is a list of functions::

        def fn(self):
            return (rv, [code, headers]) or None

    - after_request_funcs is a list of functions,
        Must return ``tuple(rv, code, headers)``::

            def fn(self, rv, code, headers):
                return (rv, code, headers) or None

    - handle_error_func is list with just one function::

        def fn(self, ex):
            return (rv, [code, headers])

    """

    schema_inputs = {}
    schema_outputs = {}
    output_types = []

    @classmethod
    def _before_request(cls, self):
        """before_request"""
        for fn in cls.before_request_funcs:
            rv = fn(self)
            if rv is not None:
                return rv
        return None

    @classmethod
    def _after_request(cls, self, rv, code, headers):
        for fn in cls.after_request_funcs:
            rv, code, headers = fn(self, rv, code, headers)
        return rv, code, headers

    @classmethod
    def _handle_error(cls, self, ex):
        if cls.handle_error_func:
            rv = cls.handle_error_func[0](self, ex)
            if rv is not None:
                return rv

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
        try:
            rv = self._before_request(self)
            if rv is None:
                rv = self.full_dispatch_request()
        except Exception as ex:
            rv = self._handle_error(self, ex)
            if rv is None:
                raise
        rv, code, headers = unpack(rv)
        rv, code, headers = self._after_request(self, rv, code, headers)
        return rv, code, headers

    def full_dispatch_request(self):
        """actual dispatch request, validate inputs and outputs
        """
        fn = getattr(self, g.action, None)
        if fn is None:
            abort(404, 'Unimplemented action %r' % g.action)
        inputs = self.__class__.schema_inputs.get(g.action)
        outputs = self.__class__.schema_outputs.get(g.action)
        output_types = self.__class__.output_types
        if inputs is not None:
            (errors, values) = validate(g.request_data, inputs)
            if errors:
                return dict(errors), 400
            else:
                if isinstance(values, dict):
                    rv = fn(**values)
                else:
                    rv = fn(values)
        else:
            rv = fn()
        rv, code, headers = unpack(rv)
        if outputs is not None:
            (errors, values) = validate(rv, outputs, proxy_types=output_types)
            if errors:
                return dict(errors), 500
            else:
                rv = values
        return rv, code, headers
