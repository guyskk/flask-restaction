#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function
import json
import six
from collections import namedtuple

Response = namedtuple("Response", "rv code headers")


def loads(data):
    """load json string compat"""
    if not isinstance(data, six.text_type):
        data = data.decode('utf-8')
    try:
        return json.loads(data)
    except:
        return data


def call_action(api, resource, action, data=None, headers=None):
    """call api resource action"""
    actions = api.resources[resource]['actions']
    for act in actions:
        if act.action == action:
            action = act
            break
    else:
        raise ValueError('action=%s not exists' % action)
    url = action.url
    if api.url_prefix:
        url = api.url_prefix + url
    if headers is None:
        headers = {}
    data_param = {}
    if action.method in ["get", "delete"]:
        data_param["query_string"] = data
    elif action.method in ["post", "put"]:
        data_param["data"] = json.dumps(data, ensure_ascii=False)
    with api.app.test_client() as c:
        resp = c.open(url, method=action.method, headers=headers,
                      content_type="application/json", **data_param)
        return Response(loads(resp.data), resp.status_code, resp.headers)


class Res(object):
    """a tool like res.js

    usage::

        res = Res(api)
        data = {'username':'xxx','password':'123456'}
        rv,code,headers = res.user.post_login(data)
        # after login, we can call permission required api
        res = Res(api,headers=headers)
        todos,code,headers=res.todo.get_list()

    :param api: Api
    :param headers: headers used for all request
    """

    def __init__(self, api, headers=None):
        self.api = api
        if headers is None:
            headers = {}
        self.headers = headers

    def __getattr__(self, resource):
        self.resource = resource
        return ResourceClient(self)

    def __repr__(self):
        return "<Res resource=%s>" % self.resource


class ResourceClient(object):
    """ResourceClient"""

    def __init__(self, res):
        self.res = res

    def __getattr__(self, action):
        self.action = action
        res = object.__getattribute__(self, 'res')

        def view_client(data=None, headers=None):
            if headers is None:
                headers = {}
            headers = dict(res.headers, **headers)
            return call_action(res.api, res.resource, action, data, headers)
        view_client.__doc__ = "resource=%s, action=%s" % (res.resource, action)
        return view_client
