"""API - Resource Manager"""
import re
import json
import textwrap
from os.path import join, basename, dirname
from collections import defaultdict, OrderedDict
from flask import (
    Response, request, make_response, send_from_directory,
    current_app, abort as flask_abort
)
from werkzeug.wrappers import Response as ResponseBase
from validr import SchemaParser, Invalid
from validr.schema import MarkKey
from . import simple_yaml as yaml
from .exporters import exporters
from .res import Res
from .cli import generate_code, parse_meta


PATTERN_ACTION = re.compile(
    r'^(get|post|put|delete|head|options|trace|patch){1}(?:_(.*))?$')
PATTERN_ENDPOINT = re.compile(r"^(?:(.*)\.)?(\w*)(?:@(.*))?$")
DEFAULT_AUTH = {
    "header": "Authorization",
    "algorithm": "HS256",
    "expiration": 3600,
    "cookie": None,
    "refresh": True
}
BUILTIN_ERROR = {
    "400.InvalidData": "request data invalid",
    "403.PermissionDeny": "permission deny",
    "500.ServerError": "internal server error"
}
DOCS_DIST = join(dirname(__file__), 'docs/dist')
DOCS_HTML = join(dirname(__file__), 'docs/docs.html')


def abort(code, error=None, message=None):
    """Abort with suitable error response

    :param code: status code
    :parma error: error symbol or flask.Response
    :param message: error message
    """
    if error is None:
        flask_abort(code)
    elif isinstance(error, Response):
        error.status_code = code
        flask_abort(code, response=error)
    else:
        body = {
            "status": code,
            "error": error,
            "message": message
        }
        flask_abort(code, response=export(body, code))


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
    """Create a suitable response"""
    if isinstance(rv, ResponseBase):
        return make_response(rv, code, headers)
    else:
        if code is None:
            code = 200
        mediatype = request.accept_mimetypes.best_match(
            exporters.keys(), default='application/json')
        return exporters[mediatype](rv, code, headers)


def parse_docs(docs, marks):
    """Parse YAML syntax content from docs

    If docs is None, return {}
    If docs has no YAML content, return {"$desc": docs}
    Else, parse YAML content, return {"$desc": docs, YAML}

    :param docs: docs to be parsed
    :param marks: list of which indicate YAML content starts, eg: ``$input``
    """
    if docs is None:
        return {}
    indexs = []
    for mark in marks:
        i = docs.find(mark)
        if i >= 0:
            indexs.append(i)
    if not indexs:
        return {"$desc": textwrap.dedent(docs).strip()}
    start = min(indexs)
    start = docs.rfind("\n", 0, start)
    yamltext = textwrap.dedent(docs[start + 1:])
    meta = yaml.load(yamltext)
    meta["$desc"] = textwrap.dedent(docs[:start]).strip()
    return meta


def get_request_data():
    """Get request data based on request.method

    If method is GET or DELETE, get data from request.args
    If method is POST, PATCH or PUT, get data from request.form or request.json
    """
    method = request.method.lower()
    if method in ["get", "delete"]:
        return request.args
    elif method in ["post", "put", "patch"]:
        if request.mimetype == 'application/json':
            try:
                return request.get_json()
            except:
                abort(400, "InvalidData", "invalid json content")
        else:
            return request.form
    else:
        return None


def parse_request():
    """Parse endpoint and return (resource, action)"""
    find = None
    if request.endpoint is not None:
        find = PATTERN_ENDPOINT.findall(request.endpoint)
    if not find:
        raise ValueError("invalid endpoint %s" % request.endpoint)
    __, resource, action_name = find[0]
    if action_name:
        action = request.method.lower() + "_" + action_name
    else:
        action = request.method.lower()
    return resource, action


def get_title(desc, default=None):
    """Get title of desc"""
    if not desc:
        return default
    lines = desc.strip('\n').split('\n')
    if not lines:
        return default
    return lines[0].lstrip('# ').rstrip(' ')


class Api:
    """Manager of Resource

    :param app: Flask or Blueprint
    :param validators: custom validators
    :param metafile: path of metafile
    :param docs: api docs
    """

    def __init__(self, app, validators=None, metafile=None, docs=""):
        self.before_request_funcs = []
        self.after_request_funcs = []
        self.handle_error_func = None
        self.app = app
        if validators:
            self.validators = validators
        else:
            self.validators = {}
        if metafile is None:
            self.meta = {}
        else:
            with open(metafile) as f:
                self.meta = json.load(f)
        meta_api = parse_docs(docs, ["$shared", "$error"])
        self.meta["$desc"] = meta_api.get("$desc", "")
        self.meta["$title"] = get_title(self.meta.get('$desc'), 'Document')
        self.meta["$shared"] = meta_api.get("$shared", OrderedDict())
        self.meta["$error"] = BUILTIN_ERROR.copy()
        self.meta["$error"].update(meta_api.get("$error", {}))
        # check shared is valid or not
        if self.meta["$shared"]:
            with MarkKey("$shared"):
                SchemaParser(shared=self.meta["$shared"])
        auth = DEFAULT_AUTH.copy()
        auth.update(self.meta.get("$auth", {}))
        self.meta["$auth"] = auth
        # TODO
        self.requires = {}
        for k, v in self.meta.get("$requires", {}).items():
            self.requires[k] = Res(v)
        self._resjs_cache = None

    def meta_view(self):
        """
        Meta data / API document

        By default, this view func will return API document(HTML),
        you can set request header `Accept` to `application/json`
        or set query string `json` to get meta data(JSON).
        """
        mediatype = request.accept_mimetypes.best_match(
            ['text/html', 'application/json'], default='text/html')
        dumped = json.dumps(
            self.meta, indent=4, sort_keys=True, ensure_ascii=False)
        if mediatype == 'application/json' or 'json' in request.args:
            return make_response(dumped, {
                "Content-Type": "application/json; charset=utf-8"
            })
        filename = request.args.get('f')
        if filename in ["res.js", "res.min.js"]:
            # cache parsed meta
            if self._resjs_cache is None:
                self._resjs_cache = parse_meta(self.meta)
            prefix = current_app.config.get("API_URL_PREFIX")
            min = filename == "res.min.js"
            code = generate_code(self._resjs_cache, prefix=prefix, min=min)
            response = make_response(code, {
                "Content-Type": "application/javascript"
            })
            # handle etag
            response.add_etag()
            return response.make_conditional(request)
        if filename:
            return send_from_directory(DOCS_DIST, basename(filename))
        with open(DOCS_HTML) as f:
            content = f.read()\
                .replace('$(title)', self.meta.get('$title', ''))\
                .replace('$(meta)', dumped)
        return make_response(content)

    def add_resource(self, resource, *class_args, **class_kwargs):
        """Add resource

        Parse resource and it's actions, route actions by naming rule.

        :param resource: resource class
        :param class_args: class_args
        :param class_kwargs: class_kwargs
        """
        name = resource.__name__.lower()
        meta_resource = parse_docs(resource.__doc__, ["$shared"])
        self.meta[name] = meta_resource
        shared = self.meta["$shared"].copy()
        shared.update(meta_resource.get("$shared", {}))
        with MarkKey("%s.$shared" % resource.__name__):
            sp = SchemaParser(validators=self.validators, shared=shared)
        with MarkKey(resource.__name__):
            resource = resource(*class_args, **class_kwargs)
            # group actions by it's name, and
            # make action group a view function
            actions = defaultdict(lambda: {})
            for action in dir(resource):
                find = PATTERN_ACTION.findall(action)
                if not find:
                    continue
                httpmethod, action_name = find[0]
                action_group = actions[action_name]
                fn = getattr(resource, action)
                meta_action = parse_docs(
                    fn.__doc__, ["$input", "$output", "$error"])
                meta_resource[action] = meta_action
                with MarkKey(fn.__name__):
                    action_group[httpmethod] = \
                        self.make_action(fn, sp, meta_action)

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
        """Make resource's method an action

        Validate input, output by schema in meta.
        If no input schema, call fn without params.
        If no output schema, will not validate return value.

        :param fn: resource's method
        :param schema_parser: for parsing schema in meta
        :param meta: meta data of the action
        """
        validate_input = validate_output = None
        if "$input" in meta:
            with MarkKey("$input"):
                validate_input = schema_parser.parse(meta["$input"])
        if "$output" in meta:
            with MarkKey("$output"):
                validate_output = schema_parser.parse(meta["$output"])

        def action(data):
            if validate_input:
                try:
                    data = validate_input(data)
                except Invalid as ex:
                    return abort(400, "InvalidData", str(ex))
                if isinstance(data, dict):
                    rv = fn(**data)
                else:
                    rv = fn(data)
            else:
                rv = fn()
            rv, status, headers = unpack(rv)
            if validate_output:
                try:
                    rv = validate_output(rv)
                except Invalid as ex:
                    return abort(500, "ServerError", str(ex))
            return rv, status, headers
        return action

    def make_view(self, action_group):
        """Create a view function

        Check permission and Dispatch request to action by request.method
        """
        def view(*args, **kwargs):
            try:
                httpmathod = request.method.lower()
                if httpmathod not in action_group:
                    abort(405)
                resp = self._before_request()
                if resp is None:
                    fn = action_group[httpmathod]
                    resp = fn(get_request_data())
            except Exception as ex:
                resp = self._handle_error(ex)
                if resp is None:
                    raise
            resp = self._after_request(*unpack(resp))
            return export(*resp)
        return view

    def authorize(self, role):
        """Check permission"""
        resource, action = parse_request()
        roles = self.meta.get("$roles", {})
        message = "%s can't access %s.%s" % (role, resource, action)
        try:
            if action not in roles[role][resource]:
                abort(403, "PermissionDeny", message)
        except KeyError:
            abort(403, "PermissionDeny", message)

    def _before_request(self):
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
