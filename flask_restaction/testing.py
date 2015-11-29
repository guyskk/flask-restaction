# coding:utf-8

from __future__ import unicode_literals
from __future__ import absolute_import
from flask import g


class RestactionClient(object):
    """RestactionClient"""

    def __init__(self, api, user_id=None):
        self.api = api
        self.user_id = user_id
        try:
            self.app_context = self.api.app.app_context()
        except AttributeError as ex:
            ex.args += ("api didn't inited!!",)
            raise

    def __getattr__(self, resource):
        g.resource = resource
        api = object.__getattribute__(self, "api")
        if resource not in api.resources:
            raise ValueError("resource not found: %s" % resource)
        view = api.resources[resource]["view_func"]
        return ResourceClient(view_func=view)

    def __enter__(self):
        self.app_context.__enter__()
        g._restaction_test = True
        g.me = {
            "id": self.user_id
        }
        return self

    def __exit__(self, exc_type, exc_value, tb):
        return self.app_context.__exit__(exc_type, exc_value, tb)
        g._restaction_test = False

    def __repr__(self):
        return "<RestactionClient user_id=%s>" % self.user_id


class ResourceClient(object):
    """ResourceClient"""

    def __init__(self, view_func):
        self.view_func = view_func

    def __getattr__(self, action):
        g.action = action
        view_func = object.__getattribute__(self, "view_func")

        def view_client(data=None):
            # to avoid validate error 'must be dict' when test
            if data is None:
                data = {}
            g.request_data = data
            return view_func()
        view_client.__doc__ = "action=%s" % action
        return view_client
