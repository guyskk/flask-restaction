import re
import jwt
import json
import yaml
import textwrap
from collections import defaultdict
from datetime import datetime, timedelta
from flask import request, abort, jsonify, make_response
from werkzeug.wrappers import Response as ResponseBase
from validater import SchemaParser, Invalid
from . import exporters

pattern_action = re.compile(
    r'^(get|post|put|delete|head|options|trace|patch){1}(?:_(.*))?$')
pattern_endpoint = re.compile(r"^(?:(.*)\.)?(\w*)(?:@(.*))?$")

DEFAULT_AUTH = {
    "header": "Authorization",
    "algorithm": "HS256",
    "expiration": 3600
}


def unpack(rv):
    """Convert rv to tuple(data, code, headers)

    :param rv: data or tuple that contain code and headers
    """
    status = headers = None
    if isinstance(rv, tuple):
        rv, status, headers = rv + (None,) * (3 - len(rv))
    if isinstance(status, (dict, list)):
        headers, status = status, headers
    return (rv, status, headers)


def export(rv, code=None, headers=None):
    if isinstance(rv, (ResponseBase, str)):
        return make_response(rv, code, headers)
    else:
        if rv is None:
            rv = ""
        if code is None:
            code = 200
        mediatype = request.accept_mimetypes.best_match(
            exporters.keys(), default='application/json')
        return exporters[mediatype](rv, code, headers)


def parse_docs(text, mark):
    i = text.find(mark)
    if i < 0:
        return {"$desc": text}
    start = text.rfind("\n", 0, i)
    yamltext = textwrap.dedent(text[start + 1:])
    meta = yaml.load(yamltext)
    meta["$desc"] = textwrap.dedent(text[:start].strip('\n'))
    return meta


def get_request_data():
    """Get request data based on request.method"""
    method = request.method.lower()
    if method in ["get", "delete"]:
        return request.args
    elif method in ["post", "put"]:
        if request.mimetype == 'application/json':
            try:
                return request.get_json()
            except:
                abort(400, jsonify({
                    "error": "InvalidData",
                    "message": "invalid json content"
                }))
        else:
            return request.form
    else:
        return None


def parse_request():
    """Parse resource&action"""
    find = pattern_endpoint.findall(request.endpoint)
    if not find:
        abort(500, jsonify({
            "error": "ServerError",
            "message": "invalid endpoint: %s" % request.endpoint
        }))
    __, resource, action_name = find[0]
    if action_name:
        action = request.method.lower() + "_" + action_name
    else:
        action = request.method.lower()
    return resource, action


class Api(object):
    """Api is a manager of resources

    route all resources to blueprint if blueprint is not None,
    and set Api.url_prefix to blueprint's url_prefix when it registered.

    :param app: Flask
    :param blueprint: Blueprint
    :param docs: api docs
    """

    def __init__(self, app, validaters=None, metafile=None, docs=""):
        """Init app"""
        self.before_request_funcs = []
        self.after_request_funcs = []
        self.handle_error_func = None
        self.get_role_func = None
        self.app = app
        if validaters:
            self.validaters = validaters
        else:
            self.validaters = {}
        if metafile is None:
            self.meta = {}
        else:
            with open(metafile) as f:
                self.meta = json.load(f)
        meta_api = parse_docs(docs, "$shared")
        self.meta["$shared"] = meta_api.get("$shared", {})
        self.meta["$desc"] = meta_api.get("$desc", "")
        auth = DEFAULT_AUTH.copy()
        auth.update(meta_api.get("$auth", {}))
        self.meta["$auth"] = auth
        self.app.add_url_rule("/", view_func=self.meta_view)

    def meta_view(self):
        """Meta data as API"""
        return export(self.meta, 200, {})

    def add_resource(self, resource, *class_args, **class_kwargs):
        """Add resource

        :param resource: resource class
        :param class_args: class_args
        :param class_kwargs: class_kwargs
        """
        name = resource.__name__.lower()
        resource = resource(*class_args, **class_kwargs)
        meta_resource = parse_docs(resource.__doc__, "$shared")
        self.meta[name] = meta_resource
        shared = self.meta["$shared"].copy()
        shared.update(meta_resource.get("$shared", {}))
        sp = SchemaParser(validaters=self.validaters, shared=shared)
        actions = defaultdict(lambda: {})
        for action in dir(resource):
            find = pattern_action.findall(action)
            if not find:
                continue
            httpmethod, action_name = find[0]
            action_group = actions[action_name]
            fn = getattr(resource, action)
            meta_action = parse_docs(fn.__doc__, "$input")
            meta_resource[action] = meta_action
            action_group[httpmethod] = self.make_action(fn, sp, meta_action)

        for action_name in actions:
            if action_name == "":
                url = "/" + name
                endpoint = name
            else:
                url = "/{0}/{1}".format(name, action_name)
                endpoint = "{0}@{1}".format(name, action_name)
            action_group = actions[action_name]
            self.app.add_url_rule(
                url, endpoint=endpoint,
                view_func=self.make_view(action_group),
                methods=set(action_group)
            )

    def make_action(self, fn, schema_parser, meta):
        validate_input = validate_output = None
        if "$input" in meta:
            validate_input = schema_parser.parse(meta["$input"])
        if "$output" in meta:
            validate_output = schema_parser.parse(meta["$output"])

        def action(data):
            if validate_input:
                try:
                    data = validate_input(data)
                except Invalid as ex:
                    return abort(400, jsonify({
                        "error": "InvalidData",
                        "message": str(ex)
                    }))
            if isinstance(data, dict):
                rv = fn(**data)
            else:
                rv = fn(data)
            rv, status, headers = unpack(rv)
            if validate_output:
                try:
                    rv = validate_output(rv)
                except Invalid as ex:
                    return abort(500, jsonify({
                        "error": "InvalidData",
                        "message": str(ex)
                    }))
            return rv, status, headers
        return action

    def make_view(self, action_group):
        def view(*args, **kwargs):
            try:
                resp = self._before_request()
                if resp is None:
                    httpmathod = request.method.lower()
                    if httpmathod not in action_group:
                        abort(405)
                    self.authorize()
                    fn = action_group[httpmathod]
                    data = get_request_data()
                    resp = fn(data)
            except Exception as ex:
                resp = self._handle_error(ex)
                if resp is None:
                    raise
            resp = self._after_request(*unpack(resp))
            return export(*resp)
        return view

    def authorize(self):
        """Check permission"""
        if self.get_role_func:
            resource, action = parse_request()
            token = self.parse_auth_token()
            role = self.get_role_func(token)
            roles = self.meta.get("$roles", {})
            try:
                if action not in roles[role][resource]:
                    abort(403)
            except KeyError:
                abort(403)
                # self.meta[resource][action]:
                # abort(403, jsonify({
                #     "error": "PermissionDeny",
                #     "message": ("%s can't access %s.%s" %
                #                 (role, resource, action))
                # }))

    def get_role(self, f):
        """Decorater"""
        self.get_role_func = f
        return f

    def parse_auth_token(self):
        """Parse Authorization token from request headers"""
        auth = self.meta["$auth"]
        token = request.headers.get(auth["header"])
        options = {'require_exp': True}
        try:
            return jwt.decode(
                token,
                self.app.secret_key,
                algorithms=[auth["algorithm"]],
                options=options
            )
        except jwt.InvalidTokenError:
            pass
        except AttributeError:
            # jwt's bug when token is None or int
            # https://github.com/jpadilla/pyjwt/issues/183
            pass
        if self.app.debug:
            self.app.logger.debug("InvalidToken: %s" % token)
        return None

    def gen_auth_token(self, token, auth_exp=None):
        auth = self.meta["$auth"]
        if auth_exp is None:
            auth_exp = auth["expiration"]
        token["exp"] = datetime.utcnow() + timedelta(seconds=auth_exp)
        return jwt.encode(token, self.app.secret_key,
                          algorithm=auth["algorithm"])

    def gen_auth_header(self, token, auth_exp=None):
        auth = self.meta["$auth"]
        return {auth["header"]: self.gen_auth_token(token, auth_exp)}

    def _before_request(self):
        """Before request"""
        for fn in self.before_request_funcs:
            rv = fn()
            if rv is not None:
                return rv
        return None

    def _after_request(self, rv, status, headers):
        for fn in self.after_request_funcs:
            rv, status, headers = fn(rv, status, headers)
        return rv, status, headers

    def _handle_error(self, ex):
        if self.handle_error_func:
            return self.handle_error_func(ex)
        return None

    def after_request(self, f):
        """Decorater"""
        self.after_request_funcs.append(f)
        return f

    def before_request(self, f):
        """Decorater"""
        self.before_request_funcs.append(f)
        return f

    def error_handler(self, f):
        """Decorater"""
        self.handle_error_func = f
        return f
