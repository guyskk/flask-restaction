# coding:utf-8

from __future__ import unicode_literals
from __future__ import absolute_import
import six
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
from flask import Blueprint, request, abort, current_app, g, make_response
from werkzeug.wrappers import Response as ResponseBase
import os
from os.path import join, exists
import jwt
import inspect
from datetime import datetime, timedelta
from jinja2 import Template
from werkzeug.exceptions import HTTPException
from collections import namedtuple
import functools
import json
from .permission import Permission, load_config, parse_config, permit
from . import exporters, unpack, logger
from . import pattern_action, pattern_endpoint
from . import res_js, res_docs
from .testing import RestactionClient

_default_config = {
    "auth_header": "Authorization",
    "auth_token_name": "res_token",
    "auth_secret": "SECRET",
    "auth_alg": "HS256",
    "auth_exp": 1200,
    "resource_json": "resource.json",
    "permission_json": "permission.json",
    "fn_user_role": None,
    "resjs_name": "res.js",
    "resdocs_name": "resdocs.html",
    "bootstrap": "http://apps.bdimg.com/libs/bootstrap/3.3.4/css/bootstrap.css",
    "docs": "",
    "enable_profiler": False,
}


def _ensure_unicode(s):
    """decode s to unicode string by encoding='utf-8'"""
    if s is not None and not isinstance(s, six.text_type):
        return six.text_type(s, encoding="utf-8")
    else:
        return s


def _normal_validate(obj):
    """change lamada validate to string"""
    if not isinstance(obj, six.string_types):
        return six.text_type(obj)


def _do_combine(res_cls, schema):
    """lazy_combine tuple_like schema"""
    for k, v in schema.items():
        if six.callable(v):
            try:
                schema[k] = v(res_cls.__dict__)
            except KeyError as ex:
                raise ValueError("%s not in Resource class: %s" % (
                    str(ex), res_cls.__name__))


def get_request_data():
    method = request.method.lower()
    if method in ["get", "delete"]:
        return request.args
    elif method in ["post", "put"]:
        if request.mimetype == 'application/json':
            try:
                data = request.get_json()
                if data is not None:
                    return data
                else:
                    return {}
            except:
                abort(400, "Invalid json content")
        else:
            return request.form
    else:
        return {}


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


def parse_resource(res_cls, name=None):
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
            "Action", "action httpmethod act url endpoint docs inputs outputs")

    .. versionchanged:: 0.19.3
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
        "Action", "action httpmethod act url endpoint docs inputs outputs")

    _do_combine(res_cls, res_cls.schema_inputs)
    _do_combine(res_cls, res_cls.schema_outputs)

    actions = []

    dumps = functools.partial(json.dumps, indent=2, sort_keys=True,
                              ensure_ascii=False, default=_normal_validate)

    for action, (meth, act) in zip(methods, meth_act):
        if act == "":
            url = "/" + name
            endpoint = name
        else:
            url = "/{0}/{1}".format(name, act)
            endpoint = "{0}@{1}".format(name, act)
        docs = _ensure_unicode(getattr(res_cls, action).__doc__)
        inputs = dumps(res_cls.schema_inputs.get(action))
        outputs = dumps(res_cls.schema_outputs.get(action))
        actions.append(Action(action, meth, act, url,
                              endpoint, docs, inputs, outputs))
    httpmethods = set([x.httpmethod for x in actions])
    rules = set([(x.url, x.endpoint) for x in actions])

    res = {
        "class": res_cls,
        "docs": _ensure_unicode(res_cls.__doc__),
        "actions": actions,
        "httpmethods": httpmethods,
        "rules": rules,
    }
    return name, res


def export(rv, code, headers):
    if isinstance(rv, (ResponseBase, six.string_types)):
        return make_response(rv, code, headers)
    else:
        if rv is None:
            rv = ""
        mediatype = request.accept_mimetypes.best_match(
            exporters.keys(), default='application/json')
        return exporters[mediatype](rv, code, headers)


class Api(object):

    """Api is a manager of resources

    :param app: Flask or Blueprint
    :param resource_json: resource.json,
    :param permission_json: permission.json,
    :param auth_header: http header name
    :param auth_token_name: token_name for saving auth_token in local_storge
    :param auth_secret: jwt secret
    :param auth_alg: jwt algorithm
    :param auth_exp: jwt expiration time (seconds)
    :param resjs_name: res.js file name
    :param resdocs_name: resdocs.html file name
    :param bootstrap: url for bootstrap.css, used for resdocs
    :param fn_user_role: a function that return user's role.
    :param docs: api docs
    :param enable_profiler: enable profiler

    .. versionadded:: 0.19.3
        docs: api docs
        test_client: a test_client

    .. versionadded:: 0.19.6
        enable_profiler: enable profiler

    .. versionchanged:: 0.19.6
        permission_path removed, resource_json, permission_json added.
        fn_user_role's param 'user' removed.

    default value::

        {
            "auth_header": "Authorization",
            "auth_token_name": "res_token",
            "auth_secret": "SECRET",
            "auth_alg": "HS256",
            "auth_exp": 1200,
            "resource_json": "resource.json",
            "permission_json": "permission.json",
            "fn_user_role": None,
            "resjs_name": "res.js",
            "resdocs_name": "resdocs.html",
            "bootstrap": "http://apps.bdimg.com/libs/bootstrap/3.3.4/css/bootstrap.css",
            "docs": "",
            "enable_profiler": False
        }

    fn_user_role::

        def fn_user_role(user_id):
            # query user from database
            # return user's role

    other attrs::

        permission Permission object

    """

    def __init__(self, app=None, **config):

        self.resources = {}
        self.before_request_funcs = []
        self.after_request_funcs = []
        self.handle_error_func = None
        self.app = None
        self.blueprint = None
        if app is not None:
            self.init_app(app)
        self._config(**config)

    def _config(self, **config):

        for k, v in _default_config.items():
            if k in config:
                # from params
                setattr(self, k, config[k])
            elif self.app is not None and not isinstance(self.app, Blueprint):
                # from app.config
                key = "API_" + k.upper()
                if key in self.app.config:
                    setattr(self, k, self.app.config[key])
            if not hasattr(self, k):
                # don't set to default value if already hasattr k
                setattr(self, k, v)

        self.docs = _ensure_unicode(self.docs)

    def config(self, cfg):
        """config api with cfg

        :param cfg: a dict
        """
        c = {}
        for k in _default_config:
            key = "API_" + k.upper()
            if key in cfg:
                c[k] = cfg[key]

        self._config(**c)

    def init_app(self, app, **config):
        """init_app

        :param app: Flask or Blueprint
        """
        self.app = app
        self._config(**config)
        self.url_prefix = None
        if isinstance(app, Blueprint):
            self.blueprint = app
            self.blueprint.record(lambda s: setattr(
                self, "url_prefix", s.url_prefix))
            self.blueprint.record(lambda s: setattr(self, "app", s.app))
            self.blueprint.record(lambda s: self.init_permission(s.app))
        else:
            self.blueprint = None
            self.init_permission(app)

    def init_permission(self, app):
        """init_permission

        :param app: Flask or Blueprint
        """
        if not os.path.isabs(self.resource_json):
            self.resource_json = join(app.root_path, self.resource_json)
        if not os.path.isabs(self.permission_json):
            self.permission_json = join(app.root_path, self.permission_json)

        try:
            resource, permission = load_config(
                self.resource_json, self.permission_json)
            config = parse_config(resource, permission)
            self.permission_resource = resource
            self.permission_permission = permission
            self.permission_config = config
        except IOError as ex:
            logger.warning(ex)
            self.permission_resource = None
            self.permission_permission = None
            self.permission_config = None

    def _permit(self, user_role, resource, action):
        if self.permission_config is None:
            # allow all requests
            return True, None
        else:
            return permit(self.permission_config, user_role, resource, action)

    def _before_resource_init(self):

        if not getattr(g, "_restaction_test", False):
            resource, action = parse_request()
            me = self.parse_auth_header()
            request_data = get_request_data()
            g.resource = resource
            g.action = action
            g.me = me
            g.request_data = request_data

        user_role = self._fn_user_role(g.me["id"])
        permit, res_role = self._permit(user_role, g.resource, g.action)
        g.me["role"] = res_role
        if not permit:
            if g.me["id"] is None:
                abort(403, "permission deny: your token is invalid")
            else:
                abort(403, "You don't have permission: user_role=%s" % user_role)

    def _fn_user_role(self, user_id):
        """exec fn_user_role"""
        if self.fn_user_role:
            try:
                return self.fn_user_role(user_id)
            except Exception as ex:
                current_app.logger.exception(
                    "Error raised when get user_role: %s" % str(ex))
        return None

    def add_permission_resource(self, name=None):
        """add_resource Permission"""
        self.add_resource(Permission, name=name, api=self)

    def make_view(self, view):
        """Converts the class into an actual view function that can be used
        with the routing system. Copyed from flask.views.py.

        :param cls: resource class
        :param name: resource name
        :param test_config: some data used in test

        test_config::

            {
                "resource":"resource name",
                "action":"action name",
                "user_id":"user_id",
                "data":"a dict of data that will passed to view",
            }
        """
        @functools.wraps(view)
        def wrapper(*args, **kwargs):
            try:
                resp = self._before_request()
                if resp is None:
                    resp = view(*args, **kwargs)
            except Exception as ex:
                resp = self._handle_error(ex)
                if resp is None:
                    raise
            resp = self._after_request(*unpack(resp))
            if getattr(g, "_restaction_test", False):
                ResponseTuple = namedtuple("ResponseTuple", "rv code header")
                return ResponseTuple(*resp)
            else:
                return export(*resp)

        return wrapper

    def add_resource(self, res_cls, name=None, *class_args, **class_kwargs):
        """add_resource

        :param res_cls: resource class
        :param name: display resource name, used in url
        :param class_args: class_args
        :param class_kwargs: class_kwargs
        """
        name, res = parse_resource(res_cls, name)
        view = res_cls.as_view(name, before_init=self._before_resource_init,
                               *class_args, **class_kwargs)
        view = self.make_view(view)
        res["view_func"] = view
        for url, end in res["rules"]:
            self.app.add_url_rule(url, endpoint=end, view_func=view,
                                  methods=res["httpmethods"])
        self.resources[name] = res

    def _gen_from_template(self, tmpl, name):
        """genarate something and write to static_folder

        :param tmpl: template unicode string
        :param name: file name to write
        """
        template = Template(tmpl)
        apiinfo = {
            "auth_header": self.auth_header,
            "auth_token_name": self.auth_token_name,
            "url_prefix": self.url_prefix or "",
            "docs": self.docs
        }
        rendered = template.render(resjs_name=self.resjs_name,
                                   bootstrap=self.bootstrap, apiinfo=apiinfo,
                                   resources=self.resources)
        if not exists(self.app.static_folder):
            os.makedirs(self.app.static_folder)
        path = join(self.app.static_folder, name)
        with open(path, "w") as f:
            if six.PY2:
                f.write(rendered.encode("utf-8"))
            else:
                f.write(rendered)

    def gen_resjs(self):
        """genarate res.js, should be called after added all resources
        """
        self._gen_from_template(res_js, self.resjs_name)

    def gen_resdocs(self):
        """genarate resdocs.html, should be called after added all resources
        """
        self._gen_from_template(res_docs, self.resdocs_name)

    def gen_token(self, me, auth_exp=None):
        """generate token, ``id`` must in param ``me``

        :param me: a dict like ``{"id": user_id, ...}``
        :param auth_exp: seconds of jwt token expiration time
                         , default is ``self.auth_exp``
        :return: string
        """
        if auth_exp is None:
            auth_exp = self.auth_exp
        me["exp"] = datetime.utcnow() + timedelta(seconds=auth_exp)
        token = jwt.encode(me, self.auth_secret, algorithm=self.auth_alg)
        return token

    def gen_auth_header(self, me, auth_exp=None):
        """generate auth_header, ``id`` must in param ``me``

        :return: ``{self.auth_header: self.gen_token(me)}``
        """
        auth = {self.auth_header: self.gen_token(me)}
        return auth

    def parse_auth_header(self):
        """parse http header auth token

        :return:

            a dict::

                {"id": user_id, ...}

            if token not exists or id not exists or token invalid::

                {"id": None}
        """
        token = request.headers.get(self.auth_header)
        options = {
            'require_exp': True,
        }
        try:
            me = jwt.decode(token, self.auth_secret,
                            algorithms=[self.auth_alg], options=options)
            if "id" not in me:
                current_app.logger.warning(
                    "set id to None because it not in me: %s" % me)
                me["id"] = None
            return me
        except jwt.InvalidTokenError:
            pass
        except AttributeError:
            # jwt's bug when token is None or int
            # https://github.com/jpadilla/pyjwt/issues/183
            pass
        current_app.logger.debug("InvalidToken: %s" % token)
        return {"id": None}

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

    def test_client(self, user_id=None):
        """A api test client, test your api without request context.

        Note that you can't access ``request`` because flask.request context not exist.
        You can access app context, such ``flask.g``.
        The return value is namedtuple("ResponseTuple", "rv code header"),
        while rv is a dict, so it's easy to assert and compare.

        Usage::

            with api.test_client() as c:
                rv,code,header = c.resource.action(data)
                assert code == 200
                assert rv == {"hello":"world"}
                assert c.resource.action_need_login(data).code == 403

            with api.test_client(user_id) as c:
                assert c.resource.action_need_login(data).code == 200
                assert c.resource.action_need_login(data).rv == {"hello":"guyskk"}
        """
        return RestactionClient(self, user_id)
