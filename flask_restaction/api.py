# coding:utf-8

from __future__ import unicode_literals

from flask import Blueprint, request
import os
from os.path import join, exists
import jwt
import inspect
from datetime import datetime, timedelta
from jinja2 import Template
from copy import deepcopy
import json
from . import Permission
from . import pattern_action
from . import abort
from . import res_js, res_docs


class Api(object):

    """Api is a manager of resources

    :param app: Flask or Blueprint
    :param permission_path: permission file path
    :param auth_header: http header name
    :param auth_secret: jwt secret
    :param auth_alg: jwt algorithm
    :param auth_exp: jwt expiration time (seconds)
    :param resjs_name: res.js file name
    :param resdocs_name: resdocs.html file name
    """

    def __init__(self, app=None, permission_path="permission.json",
                 auth_header="Authorization", auth_secret="SECRET",
                 auth_alg="HS256", auth_exp=1200, resjs_name="res.js",
                 resdocs_name="resdocs.html"):
        self.permission_path = permission_path
        self.auth_header = auth_header
        self.auth_secret = auth_secret
        self.auth_alg = auth_alg
        self.auth_exp = auth_exp
        self.resjs_name = resjs_name
        self.resdocs_name = resdocs_name

        self.resources = []

        self.before_request_funcs = []
        self.after_request_funcs = []
        self.handle_error_func = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """init_app

        :param app: Flask or Blueprint
        """
        self.app = app
        if self.is_blueprint():
            self.app.record(lambda s: self.init_permission(s.app))
            self.app.record(lambda s: setattr(self, "url_prefix", s.url_prefix))
        else:
            self.init_permission(app)
            self.url_prefix = None

    def init_permission(self, app):
        """init_permission

        :param app: Flask or Blueprint
        """
        ppath = join(app.root_path, self.permission_path)
        if exists(ppath):
            self.permission_path = ppath
            self.permission = Permission(filepath=ppath)
        else:
            self.permission = Permission()
            # allow all request
            self.permission.add("*", "*", None)

    def is_blueprint(self):
        """self.app is_blueprint or not"""
        return isinstance(self.app, Blueprint)

    def parse_resource(self, res_cls, name=None):
        """parse resource class

        :param res_cls: resource class
        :param name: display resource name, used in url
        :return:

            info of resource class::

                {
                    "name": name,
                    "classname": classname,
                    "docs": res_cls.__doc__,
                    "meth_act": meth_act,
                    "actions": actions,
                    "methods": methods,
                    "rules": rules,
                    "schema_inputs": res_cls.schema_inputs
                    "schema_outputs": res_cls.schema_outputs
                    "docstrings": docstrings
                }

            meth_act is a list of tuple(meth, act)::

                'get' -> ('get', '')
                'get_list' -> ('get', 'list')
                'post' -> ('post', '')

            actions is a list of tuple(meth, act, url, endpoint, action)::

                meth, act:   the same as meth_act
                url:         '/name/act' or '/name'
                endpoint:    'classname@action' or 'classname'
                action:      resource's method name

            methods is a list of availble httpmethod in resource

            rules is a list of availble tuple(url, endpoint) in resource
        """
        if not inspect.isclass(res_cls):
            raise ValueError("%s is not class" % res_cls)
        classname = res_cls.__name__.lower()
        if name is None:
            name = classname
        else:
            name = name.lower()
        meth_act = [tuple(pattern_action.findall(x)[0]) for x in dir(res_cls)
                    if pattern_action.match(x)]
        actions = []
        docstrings = {}
        for meth, act in meth_act:
            if act == "":
                action = meth
                url = "/" + name
                endpoint = classname
            else:
                action = meth + "_" + act
                url = "/{0}/{1}".format(name, act)
                endpoint = "{0}@{1}".format(classname, act)
            docstrings[action] = getattr(res_cls, action).__doc__
            actions.append((meth, act, url, endpoint, action))

        methods = set([x[0] for x in actions])
        rules = set([(x[2], x[3]) for x in actions])

        return {
            "name": name,
            "classname": classname,
            "docs": res_cls.__doc__,
            "meth_act": meth_act,
            "actions": actions,
            "methods": methods,
            "rules": rules,
            "schema_inputs": deepcopy(res_cls.schema_inputs),
            "schema_outputs": deepcopy(res_cls.schema_outputs),
            "docstrings": docstrings
        }

    def add_resource(self, res_cls, name=None, *class_args, **class_kwargs):
        """add_resource

        :param res_cls: resource class
        :param name: display resource name, used in url
        :param class_args: class_args
        :param class_kwargs: class_kwargs
        """
        res = self.parse_resource(res_cls, name)
        res_cls.before_request_funcs.insert(0, self._before_request)
        res_cls.after_request_funcs.append(self._after_request)

        def view(*args, **kwargs):
            try:
                fn = res_cls.as_view(res["name"], *class_args, **class_kwargs)
                return fn(*args, **kwargs)
            except Exception as ex:
                if self.handle_error_func:
                    rv = self.handle_error_func(ex)
                    if rv is not None:
                        return rv
                raise

        for url, end in res["rules"]:
            self.app.add_url_rule(url, endpoint=end, view_func=view, methods=res["methods"])
        self.resources.append(res)

    def _normal_validate(self, obj):
        """change lamada validate to string ``'~'`` """
        if not isinstance(obj, basestring):
            return "~"

    def parse_reslist(self):
        """parse_reslist

        :return: resources

        - resources::

            {
                "auth_header": self.auth_header,
                "blueprint": bp_name,
                "url_prefix": url_prefix,
                "reslist": reslist
            }

        - reslist: list of tuple(res_name, res_doc, actions)
        - actions: list of tuple(url, http_method, action,
            needtoken, schema_input, schema_output, action_doc)

        """
        if self.is_blueprint():
            bp_name = self.app.name
        else:
            bp_name = None
        reslist = []
        resources = {
            "auth_header": self.auth_header,
            "blueprint": bp_name,
            "url_prefix": self.url_prefix,
            "reslist": reslist
        }
        for res in self.resources:
            schema_inputs = res["schema_inputs"]
            schema_outputs = res["schema_outputs"]
            docstrings = res["docstrings"]
            actions = []
            reslist.append((res["name"], res["docs"], actions))
            for meth, act, url, endpoint, action in res["actions"]:
                if self.url_prefix:
                    url = self.url_prefix + url
                needtoken = not self.permission.permit("*", res["name"], action)
                inputs = json.dumps(schema_inputs.get(action), indent=2, sort_keys=True,
                                    ensure_ascii=False, default=self._normal_validate)
                outputs = json.dumps(schema_outputs.get(action), indent=2, sort_keys=True,
                                     ensure_ascii=False, default=self._normal_validate)
                actions.append(
                    (url, meth, action, needtoken, inputs, outputs,
                        docstrings.get(action)))
        return resources

    def _gen_from_template(self, tmpl, name):
        """genarate something and write to static_folder

        :param tmpl: template unicode string
        :param name: file name to write
        """
        template = Template(tmpl)
        resources = self.parse_reslist()
        rendered = template.render(**resources)
        if not exists(self.app.static_folder):
            os.makedirs(self.app.static_folder)
        path = join(self.app.static_folder, name)
        with open(path, "w") as f:
            f.write(rendered.encode("utf-8"))

    def gen_resjs(self):
        """genarate res.js, should be called after added all resources
        """
        self._gen_from_template(res_js, self.resjs_name)

    def gen_resdocs(self):
        """genarate resdocs.html, should be called after added all resources
        """
        self._gen_from_template(res_docs, self.resdocs_name)

    def parse_me(self):
        """parse http header auth token

        :return:

            a dict::

                {"id": user_id, "role": "role"}

            if token not exists or invalid::

                {"id": None, "role": "*"}
        """
        token = request.headers.get(self.auth_header)
        options = {
            'require_exp': True,
        }
        if token is not None:
            try:
                me = jwt.decode(token, self.auth_secret,
                                algorithms=[self.auth_alg], options=options)
                if "id" in me and "role" in me:
                    return me
            except jwt.InvalidTokenError:
                pass
        return {"id": None, "role": "*"}

    def gen_token(self, me, auth_exp=None):
        """generate token, id and role must in param ``me``

        :param me: a dict like ``{"id": user_id, "role": "role"}``
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
        """generate auth_header, id and role must in param ``me``

        :param me: a dict like ``{"id": user_id, "role": "role"}``
        :param auth_exp: seconds of jwt token expiration time
                         , default is ``self.auth_exp``
        :return: dict
        """
        auth = {self.auth_header: self.gen_token(me)}
        return auth

    def _before_request(self):
        """before_request"""
        request.me = self.parse_me()
        for fn in self.before_request_funcs:
            rv = fn()
            if rv is not None:
                return rv
        if not self.permission.permit(
                request.me["role"], request.resource, request.action):
            abort(403, "permission deny")
        return None

    def _after_request(self, rv, code, headers):
        """after_request"""
        for fn in self.after_request_funcs:
            rv, code, headers = fn(rv, code, headers)
        return rv, code, headers

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
