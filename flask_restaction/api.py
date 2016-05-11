#!/usr/bin/env python
# coding: utf-8
"""
flask_restaction.api
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionchanged:: 0.19.3

   - request.me removed, use g.me instead.
   - request.resource, request.action removed removed,
     use g.resource, g.action instead.
   - parse_reslist removed, use api.resources instead.
   - is_blueprint removed.
"""
from __future__ import unicode_literals, absolute_import, print_function
import six
from flask import request, abort, g, make_response
from werkzeug.wrappers import Response as ResponseBase
from werkzeug.exceptions import HTTPException
from collections import namedtuple
import functools
import inspect
from flask import json
from . import exporters, unpack, pattern_action, pattern_endpoint
import validater
import types
import textwrap


def ensure_unicode(s):
    """decode s to unicode string by encoding='utf-8'"""
    if s is None:
        return ""
    if not isinstance(s, six.text_type):
        return six.text_type(s, encoding="utf-8")
    else:
        return s


def format_docs(s):
    return textwrap.dedent(ensure_unicode(s).strip('\n'))


def _schema_to_json(obj):
    """change lamada validate to string"""
    if isinstance(obj, validater.Schema):
        return obj.data
    elif isinstance(obj, (types.FunctionType, types.LambdaType)):
        return obj.__name__
    else:
        return six.text_type(obj)

dumps = functools.partial(json.dumps, indent=2, sort_keys=True,
                          ensure_ascii=False, default=_schema_to_json)


def load_options(default, app, *dicts):
    """combine options of default config, app.config and kwargs config"""
    options = default.copy()
    for k in default:
        key = 'API_' + k.upper()
        if key in app.config:
            options[k] = app.config[key]
    for d in dicts:
        options.update(d)
    return options


def get_request_data():
    """get request data based on request.method"""
    method = request.method.lower()
    if method in ["get", "delete"]:
        return request.args
    elif method in ["post", "put"]:
        if request.mimetype == 'application/json':
            try:
                return request.get_json()
            except:
                abort(400, "invalid json content")
        else:
            return request.form
    else:
        return None


def parse_request():
    """parse resource&action"""
    find = pattern_endpoint.findall(request.endpoint)
    if not find:
        abort(500, "invalid endpoint: %s" % request.endpoint)
    blueprint, resource, act = find[0]
    if act:
        action = request.method.lower() + "_" + act
    else:
        action = request.method.lower()
    return resource, action


def export(rv, code, headers):
    if isinstance(rv, (ResponseBase, six.string_types)):
        return make_response(rv, code, headers)
    else:
        if rv is None:
            rv = ""
        if code is None:
            code = 200
        mediatype = request.accept_mimetypes.best_match(
            exporters.keys(), default='application/json')
        return exporters[mediatype](rv, code, headers)


DEFAULT_OPTIONS = {
    "blueprint": None,
    "docs": "",
}


class CustomValidater(object):
    """support custom validater

    these methods is samilar as in validater, except the param `validaters`:

        *add_validater*
            add custom validater
        *remove_validater*
            remove custom validater
        *parse*
            parse schema use custom validaters
    """

    def __init__(self):
        self.validaters = {}
        self.validaters.update(validater.default_validaters)
        self.add_validater = functools.partial(
            validater.add_validater, validaters=self.validaters)
        self.remove_validater = functools.partial(
            validater.remove_validater, validaters=self.validaters)
        self.parse = functools.partial(
            validater.parse, validaters=self.validaters)
        self.validate = validater.validate


class Api(object):

    """Api is a manager of resources

    route all resources to blueprint if blueprint is not None,
    and set Api.url_prefix to blueprint's url_prefix when it registered.

    :param app: Flask
    :param blueprint: Blueprint
    :param docs: api docs

    .. versionadded:: 0.19.3
        docs: api docs
        test_client: a test_client

    .. versionadded:: 0.19.6
        enable_profiler: enable profiler

    .. versionchanged:: 0.19.6
        permission_path removed, resource_json, permission_json added.
        fn_user_role's param 'user' removed.

    .. versionchanged:: 0.20.0
        fn_user_role, resource_json, permission_json,
        auth_header, auth_token_name, auth_secret, auth_alg, auth_exp removed,
        use flask_restaction.Auth instead.

        resjs_name, resdocs_name, bootstrap, gen_resjs, gen_resdocs removed,
        use flask_restaction.Gen instead.

        test_client removed, use flask's test tools instead.

    .. versionadded:: 0.20.1
        validater: support custom validater

    """

    def __init__(self, app=None, **kwargs):
        self.validater = CustomValidater()
        self.resources = {}
        self.before_request_funcs = []
        self.after_request_funcs = []
        self.handle_error_func = None
        self._options = kwargs
        if app:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        """init_app

        params is the same as __init__
        """
        self.app = app
        self.url_prefix = None
        self.auth = None
        options = load_options(DEFAULT_OPTIONS, app, self._options, kwargs)
        options["docs"] = format_docs(options["docs"])
        self.__dict__.update(options)
        if self.blueprint:
            self.blueprint.record(lambda x: setattr(
                self, "url_prefix", x.url_prefix))

    def make_view(self, view):
        """Converts the class into an actual view function that can be used
        with the routing system.
        """
        @functools.wraps(view)
        def wrapper(*args, **kwargs):
            try:
                g.resource, g.action = parse_request()
                g.request_data = get_request_data()
                resp = self._before_request()
                if resp is None:
                    resp = view(*args, **kwargs)
            except Exception as ex:
                resp = self._handle_error(ex)
                if resp is None:
                    raise
            resp = self._after_request(*unpack(resp))
            return export(*resp)
        return wrapper

    def add_resource(self, res_cls, name=None, *class_args, **class_kwargs):
        """add_resource

        :param res_cls: resource class
        :param name: resource name used in url
        :param class_args: class_args
        :param class_kwargs: class_kwargs
        """
        name, res = self.parse_resource(res_cls, name)
        view = res_cls.as_view(name, *class_args, **class_kwargs)
        view = self.make_view(view)
        if self.blueprint:
            root = self.blueprint
        else:
            root = self.app
        for url, end in res["rules"]:
            root.add_url_rule(url, endpoint=end, view_func=view,
                              methods=res["httpmethods"])
        self.resources[name] = res

    def parse_resource(self, res_cls, name=None):
        """
        :param res_cls: resource class
        :param name: resource name
        :return: name, res

        name::

            resource name

        res::

            {
                "class": res_cls,
                "docs": res_cls.__doc__,
                "actions": actions,
                "httpmethods": httpmethods,
                "rules": rules,
            }

        action::

            namedtuple(
                "Action", "action method url endpoint docs inputs outputs")

        .. versionchanged:: 0.19.3
            the return value changed.

        .. versionchanged:: 0.20.0
            the return value changed.
        """
        if not inspect.isclass(res_cls):
            raise ValueError("%s is not class" % res_cls)
        if name is None:
            name = res_cls.__name__.lower()
        else:
            name = name.lower()

        methods = [x for x in dir(res_cls) if pattern_action.match(x)]
        meth_act = [pattern_action.findall(x)[0] for x in methods]
        Action = namedtuple(
            "Action", "action method url endpoint docs inputs outputs")

        try:
            self._parse_schema(res_cls.schema_inputs)
            self._parse_schema(res_cls.schema_outputs)
        except Exception as ex:
            ex.args += (res_cls,)
            raise

        actions = []

        for action, (meth, act) in zip(methods, meth_act):
            if act == "":
                url = "/" + name
                endpoint = name
            else:
                url = "/{0}/{1}".format(name, act)
                endpoint = "{0}@{1}".format(name, act)
            docs = format_docs(getattr(res_cls, action).__doc__)
            inputs = dumps(res_cls.schema_inputs.get(action))
            outputs = dumps(res_cls.schema_outputs.get(action))
            actions.append(Action(action, meth, url, endpoint,
                                  docs, inputs, outputs))
        httpmethods = set([x.method for x in actions])
        rules = set([(x.url, x.endpoint) for x in actions])

        res = {
            "docs": format_docs(res_cls.__doc__),
            "actions": actions,
            "httpmethods": httpmethods,
            "rules": rules,
        }
        return name, res

    def _parse_schema(self, schema):
        for action, sche in schema.items():
            if sche is not None:
                try:
                    schema[action] = self.validater.parse(sche)
                except Exception as ex:
                    ex.args += (action,)
                    raise

    def _before_request(self):
        """before_request"""

        for fn in self.before_request_funcs:
            rv = fn()
            if rv is not None:
                return rv
        return None

    def _after_request(self, rv, code, headers):
        """after_request"""
        for fn in self.after_request_funcs:
            rv, code, headers = fn(rv, code, headers)
        return rv, code, headers

    def _handle_error(self, ex):
        if self.handle_error_func:
            rv = self.handle_error_func(ex)
            if rv is not None:
                return rv
        if isinstance(ex, HTTPException):
            return ex.description, ex.code
        else:
            return None

    def after_request(self, f):
        """decorater"""
        self.after_request_funcs.append(f)
        return f

    def before_request(self, f):
        """decorater"""
        self.before_request_funcs.append(f)
        return f

    def error_handler(self, f):
        """decorater"""
        self.handle_error_func = f
        return f
