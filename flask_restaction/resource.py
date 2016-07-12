"""
    flask_restaction.resource
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. versionadded:: 0.18.0
       Support tuple_like schema, The ``schema,parse_schema,combine_schema``
       function was added.
"""


class Resource:
    """Resource代表一个资源

    - before_request::

        def before_request(self):
            return (rv, [code, headers]) or None

    - after_request
        Must return ``tuple(rv, code, headers)``::

            def after_request(self, rv, code, headers):
                return (rv, code, headers) or None

    - handle_error::

        def fn(self, ex):
            return (rv, [code, headers])
    """

    def dispatch_request(self, *args, **kwargs):
        """Preproccess request and dispatch request"""
        try:
            if hasattr(self, "before_request"):
                rv = self.before_request()
                if rv is not None:
                    return rv
            resource, action = parse_request()
            fn = getattr(self, action, None)
            if fn is None:
                abort(404, 'Unimplemented action %r' % action)
            data = get_request_data()
            rv = fn(data)
        except Exception as ex:
            if hasattr(self, "handle_error"):
                rv = self.handle_error(self, ex)
                if rv is None:
                    raise
        rv, code, headers = unpack(rv)
        if hasattr(self, "after_request"):
            rv, code, headers = self.after_request(self, rv, code, headers)
        return rv, code, headers
