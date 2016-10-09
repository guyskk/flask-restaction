import flask
import requests
from json import dumps, loads


def resp_json(resp):
    """
    Get JSON from response if success, raise requests.HTTPError otherwise.

    :param resp: requests.Response or flask.Response
    :return: JSON value
    """
    if isinstance(resp, flask.Response):
        if 400 <= resp.status_code < 600:
            msg = resp.status
            try:
                result = loads(resp.data.decode("utf-8"))
                if isinstance(result, str):
                    msg = "%s, %s" % (resp.status, result)
                else:
                    msg = "%s %s, %s" % (
                        resp.status_code, result["error"], result["message"])
            except Exception:
                pass
            raise requests.HTTPError(msg, response=resp)
        else:
            return loads(resp.data.decode("utf-8"))
    else:
        try:
            resp.raise_for_status()
        except requests.HTTPError as ex:
            # the response may contains {"error": "", "message": ""}
            # append error and message to exception if possible
            try:
                result = resp.json()
                ex.args += (result["error"], result["message"])
            except (ValueError, KeyError):
                pass
            raise
        return resp.json()


def res_to_url(resource, action):
    """Convert resource.action to (url, HTTP_METHOD)"""
    i = action.find("_")
    if i < 0:
        url = "/" + resource
        httpmethod = action
    else:
        url = "/%s/%s" % (resource, action[i + 1:])
        httpmethod = action[:i]
    return url, httpmethod.upper()


class TestClientSession:
    """Wrapper Flask.test_client like requests.Session"""

    def __init__(self, test_client):
        self.test_client = test_client
        self.headers = {}

    def request(self, method, url, params=None, data=None,
                headers=None, json=None):
        if headers is None:
            headers = self.headers
        else:
            headers.update(self.headers)
        params = {
            "path": url,
            "method": method,
            "query_string": params,
            "headers": headers,
            "follow_redirects": True
        }
        if json is not None:
            params["data"] = dumps(json, ensure_ascii=False)
            params["content_type"] = "application/json"
        with self.test_client() as c:
            resp = c.open(**params)
        return resp


class Res:
    """A tool for calling API

    Will keep a session and handle auth token automatic

    Usage::

        >>> res = Res(test_client=app.test_client)  # used in testing
        >>> res = Res("http://127.0.0.1:5000")  # request remote api
        >>> res.ajax("/hello")
        {'message': 'Hello world, Welcome to flask-restaction!'}
        >>> res.hello.get()
        {'message': 'Hello world, Welcome to flask-restaction!'}
        >>> res.hello.get({"name":"kk"})
        {'message': 'Hello kk, Welcome to flask-restaction!'}
        >>> res.xxx.get()
        ...
        requests.exceptions.HTTPError: 404 Client Error: NOT FOUND
                                       for url: http://127.0.0.1:5000/xxx

    :param url_prefix: url prefix of API
    :param auth_header: auth header name of API
    :return: requests.Response
    """

    def __init__(self, url_prefix="", test_client=None,
                 auth_header="Authorization"):
        self.url_prefix = url_prefix
        self.auth_header = auth_header
        if test_client is None:
            self.session = requests.Session()
        else:
            self.session = TestClientSession(test_client)
        self.session.headers.update({'Accept': 'application/json'})

    def ajax(self, url, method="GET", data=None, headers=None):
        params = {
            "method": method,
            "url": self.url_prefix + url,
            "headers": headers
        }
        if data is not None:
            if method in ["GET", "DELETE"]:
                params["params"] = data
            elif method in ["POST", "PUT", "PATCH"]:
                params["json"] = data
        resp = self.session.request(**params)
        if self.auth_header in resp.headers:
            self.session.headers[
                self.auth_header] = resp.headers[self.auth_header]
        return resp_json(resp)

    def _request(self, resource, action, data=None, headers=None):
        """Send request

        :param resource: resource
        :param action: action
        :param data: string or object which can be json.dumps
        :param headers: http headers
        """
        url, httpmethod = res_to_url(resource, action)
        return self.ajax(url, httpmethod, data, headers)

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
        return self.res._request(self.resource, self.action, data, headers)
