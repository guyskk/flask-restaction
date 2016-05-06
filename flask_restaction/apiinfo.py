#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function
from flask_restaction import Resource
from jinja2 import Environment
import codecs
from pkg_resources import resource_string
import os
import textwrap


def parse_api(api):
    """parse api"""
    data = {"url_prefix": "", "auth_header": ""}
    data["docs"] = api.docs
    if api.url_prefix:
        data["url_prefix"] = api.url_prefix
    if api.auth:
        data["auth_header"] = api.auth.auth_header
    resources = []
    for name, res in api.resources.items():
        reaource = {"name": name, "docs": res["docs"]}
        actions = [dict(x._asdict()) for x in res["actions"]]
        reaource["actions"] = actions
        resources.append(reaource)
    data["resources"] = resources
    return data


class ApiInfo(Resource):
    """ApiInfo

    :param api: Api
    """
    action = {
        "action": "str",  # post_login
        "method": "str",  # post
        "url": "str",  # /api/user/login
        "endpoint": "str",  # user@login
        "docs": "str",  # docs of post_login
        "inputs": "str",  # schema_inputs[action]
        "outputs": "str",  # schema_outputs[action]
    }
    schema_outputs = {
        "get": {
            "url_prefix": "str",  # /api
            "auth_header": "str",  # Authorization
            "docs": "str",  # docs of api
            "resources": [{
                "name": "str",  # user
                "docs": "str",  # docs of user
                "actions": [action]
            }],
        }
    }

    def __init__(self, api):
        self.data = parse_api(api)

    def get(self):
        return self.data


class Gen(object):
    """Generate tools for docs res.js

    if dest param of generate methods is not absolute path,
    then join app.root_path and dest as dest path.
    :param api: Api
    """

    def __init__(self, api):
        self.api = api
        self.data = parse_api(api)
        app = self.api.app
        self.jinja = Environment()
        self.jinja.filters['firstline'] = self.firstline_filter
        if not os.path.exists(app.static_folder):
            os.makedirs(app.static_folder)

    def firstline_filter(self, value):
        if value is None:
            return ""
        return textwrap.dedent(value).split('\n')[0]

    def _read_file(self, *paths):
        strs = [resource_string(__name__, path).decode("utf-8")
                for path in paths]
        return os.linesep.join(strs)

    def _save_file(self, dest, content):
        if not os.path.isabs(dest):
            dest = os.path.join(self.api.app.root_path, dest)
        with codecs.open(dest, "w", encoding="utf-8") as f:
            f.write(content)

    def resjs(self, dest='static/res.js'):
        """generate res.js

        :param dest: dest path
        """
        tmpl = self._read_file('tmpl/res-core.js')
        rendered = self.jinja.from_string(tmpl).render(apiinfo=self.data)

        resjs = self._read_file('resjs/dist/res.js')
        resjs = resjs.replace('"#res-core.js#"', rendered)
        self._save_file(dest, resjs)

        resminjs = self._read_file('resjs/dist/res.min.js')
        resminjs = resminjs.replace('"#res-core.js#"', rendered)
        self._save_file(dest.replace('.js', '.min.js'), resminjs)

    def resdocs(self, dest='static/resdocs.html', resjs='/static/res.js',
                bootstrap='http://cdn.bootcss.com/bootstrap/3.3.6/css/bootstrap.min.css'):
        """generate resdocs.html

        :param dest: dest path
        :param resjs: res.js file's path
        :param bootstrap: bootstrap.css file's path
        """
        tmpl = self._read_file('tmpl/resdocs.html')
        rendered = self.jinja.from_string(tmpl).render(
            apiinfo=self.data, resjs=resjs, bootstrap=bootstrap)
        self._save_file(dest, rendered)

    def permission(self, dest='static/permission.html', resjs='/static/res.js',
                   bootstrap='http://cdn.bootcss.com/bootstrap/3.3.6/css/bootstrap.min.css',
                   vuejs='http://cdn.bootcss.com/vue/1.0.16/vue.min.js'):
        """generate permission.html

        :param dest: dest path
        :param resjs: res.js file's path
        :param bootstrap: bootstrap.css file's path
        :param vuejs: vuejs.js file's path
        """
        tmpl = self._read_file('tmpl/permission.html')
        rendered = self.jinja.from_string(tmpl).render(
            apiinfo=self.data, resjs=resjs, bootstrap=bootstrap, vuejs=vuejs)
        self._save_file(dest, rendered)
