import requests


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


def raise_for_status(resp):
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


class Res:
    """A tool for calling API

    Will keep a session and handle auth token automatic

    Usage::

        >>> res = Res("http://127.0.0.1:5000")
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
    :parma *args, **kwargs: params passed to requests.Session
    :return: requests.Response
    """

    def __init__(self, url_prefix="", auth_header="Authorization",
                 *args, **kwargs):
        self.url_prefix = url_prefix
        self.auth_header = auth_header
        self.session = requests.Session(*args, **kwargs)

    def request(self, resource, action, data=None, headers=None):
        """Send request

        :param resource: resource
        :param action: action
        :param data: string or object which can be json.dumps
        :param headers: http headers
        """
        url, httpmethod = res_to_url(resource, action)
        if self.url_prefix:
            url = self.url_prefix + url
        data_param = {}
        if data is None:
            data_param = {}
        else:
            if httpmethod in ["GET", "DELETE"]:
                data_param["params"] = data
            elif httpmethod in ["POST", "PUT", "PATCH"]:
                data_param["json"] = data
        resp = self.session.request(
            method=httpmethod, url=url, headers=headers, **data_param)
        if self.auth_header in resp.headers:
            self.session.headers[
                self.auth_header] = resp.headers[self.auth_header]
        raise_for_status(resp)
        return resp.json()

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
