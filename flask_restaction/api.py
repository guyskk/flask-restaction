# coding:utf-8

from flask import Blueprint, request
import os
from os.path import join, exists
import jwt
from jinja2 import Template
from . import Permission
from . import pattern_action
from . import abort
from . import res_js


class Api(object):

    """docstring for Api

    RESOURCE_PERMISSION_PATH = "permission.json"
    RESOURCE_AUTH_HEADER = "Authorization"
    RESOURCE_AUTH_SECRET = "SECRET"
    RESOURCE_AUTH_ALGORITHM = "HS256"
    """

    def __init__(self, app=None, permission_path="permission.json",
                 auth_header="Authorization", auth_secret="SECRET",
                 auth_algorithm="HS256"):
        self.permission_path = permission_path
        self.auth_header = auth_header
        self.auth_secret = auth_secret
        self.auth_algorithm = auth_algorithm

        self.resources = []

        self.before_request_funcs = []
        self.after_request_funcs = []
        self.handle_error_func = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        if self.is_blueprint():
            self.app.record(lambda s: self.init_permission(s.app))
        else:
            self.init_permission(app)

    def init_permission(self, app):
        ppath = join(app.root_path, self.permission_path)
        if exists(ppath):
            self.permission_path = ppath
            self.permission = Permission(filepath=ppath)
        else:
            self.permission = Permission()
            # allow all request
            self.permission.add("*", "*", None)

    def is_blueprint(self):
        return isinstance(self.app, Blueprint)

    def parse_resource(self, res_cls):
        if not type(res_cls) is type:
            raise ValueError("%s is not class" % res_cls)
        classname = res_cls.__name__
        actions = [tuple(pattern_action.findall(x)[0]) for x in dir(res_cls)
                   if pattern_action.match(x)]
        methods = set()
        rules = [("/{0}", "{0}")]
        for meth, act in actions:
            methods.add(meth.upper())
            if act != "":
                rules.append(("/{0}/{1}".format("{0}", act),
                              "{0}@{1}".format("{0}", act)))
        return {
            "classname": classname,
            "actions": actions,
            "methods": methods,
            "rules": rules,
            "inputs": res_cls.schema_inputs,
            "outputs": res_cls.schema_outputs,
        }

    def add_resource(self, res_cls, name=None, *class_args, **class_kwargs):
        res = self.parse_resource(res_cls)
        if name is None:
            name = res["classname"]
        name = name.lower()
        res["name"] = name
        res_cls.before_request_funcs.insert(0, self._before_request)
        res_cls.after_request_funcs.append(self._after_request)

        def view(*args, **kwargs):
            try:
                fn = res_cls.as_view(name, *class_args, **class_kwargs)
                return fn(*args, **kwargs)
            except Exception as ex:
                if self.handle_error_func:
                    rv = self.handle_error_func(ex)
                    if rv is not None:
                        return rv
                raise

        for url, end in res["rules"]:
            self.app.add_url_rule(
                url.format(name), end.format(res["classname"]),
                view, methods=res["methods"])
        self.resources.append(res)

    def gen_res_js(self):
        template = Template(res_js)
        reslist = []
        for res in self.resources:
            actions = []
            reslist.append((res["name"], actions))
            for meth, act in res["actions"]:
                if act:
                    url = "/{0}/{1}".format(res["name"], act)
                else:
                    url = "/{0}".format(res["name"])
                action = meth + "_" + act
                needtoken = self.permission.permit("*", res["name"], action)
                actions.append((url, meth, action, needtoken))
        js = template.render(reslist=reslist)
        if not exists(self.app.static_folder):
            os.makedirs(self.app.static_folder)
        path = join(self.app.static_folder, "res.js")
        with open(path, "w") as f:
            f.write(js.encode("utf-8"))

    def parse_me(self):
        """id and role must in the token"""
        token = request.headers.get(self.auth_header)
        if token is not None:
            try:
                me = jwt.decode(token, self.auth_secret,
                                algorithms=[self.auth_algorithm])
                if "id" in me and "role" in me:
                    return me
            except Exception:
                pass
        return {"id": None, "role": "*"}

    def gen_token(self, me):
        token = jwt.encode(me, self.auth_secret, algorithm=self.auth_algorithm)
        return token

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
        for fn in self.after_request_funcs:
            rv, code, headers = fn(rv, code, headers)
        return rv, code, headers

    def after_request(self, f):
        """装饰器"""
        self.after_request_funcs.append(f)
        return f

    def before_request(self, f):
        """装饰器"""
        self.before_request_funcs.append(f)
        return f

    def error_handler(self, f):
        """装饰器"""
        self.handle_error_func = f
        return f
