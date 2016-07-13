import requests
from .api import res_to_url


class Res:
    """A tool for calling API

    Will keep a session and handle auth token automatic

    Usage::

        res = Res("http://127.0.0.1:5000")
        resp = res.user.post_login({..})
        print(resp.json())
        resp = res.user.get({..})
        print(resp.json)

    :param url_prefix: url prefix of API
    :param auth_header: auth header name of API
    :parma *args, **kwargs: params passed to requests.Session
    :return: requests.Response
    """

    def __init__(self, url_prefix="", auth_header="Authorization",
                 *args, **kwargs):
        self.url_prefix = url_prefix
        self.auth_header = auth_header
        self.session = requests.Session(*args, **kwargs)

    def request(self, resource, action, data=None, headers=None):
        url, httpmethod = res_to_url(resource, action)
        if self.url_prefix:
            url = self.url_prefix + url
        data_param = {}
        if data is None:
            data_param = {}
        else:
            if httpmethod in ["GET", "DELETE"]:
                data_param["params"] = data
            elif httpmethod in ["POST", "PUT"]:
                data_param["json"] = data
        resp = self.session.request(
            method=httpmethod, url=url, headers=headers, **data_param)
        if self.auth_header in resp.headers:
            self.session.headers[self.auth_header] = \
                resp.headers[self.auth_header]
        return resp

    def __getattr__(self, resource):
        return Resource(self, resource)


class Resource:

    def __init__(self, res, resource):
        self._res = res
        self._resource = resource

    def __getattr__(self, action):
        return Action(self, action)


class Action:

    def __init__(self, resource, action):
        self.res = resource._res
        self.resource = resource._resource
        self.action = action

    def __call__(self, data=None, headers=None):
        return self.res.request(self.resource, self.action, data, headers)
