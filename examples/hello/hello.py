"""
# Hello API

Support markdown in docs:

![markdown](https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Markdown-mark.svg/500px-Markdown-mark.svg.png)

为RESTful API而生的Web框架：

- 创建RESTful API
- 校验用户输入以及将输出转化成合适的响应格式
- 身份验证和权限控制
- 自动生成Javascript SDK和API文档
"""
from flask import Flask, g
from flask_restaction import Api

app = Flask(__name__)
api = Api(app, docs=__doc__, metafile="meta.json")
app.secret_key = b'secret_key'


@api.get_role
def get_role(token):
    g.token = token
    if token is None:
        return "guest"
    else:
        return "normal"


class Welcome:

    def __init__(self, name):
        self.name = name
        self.message = "Hello %s, Welcome to flask-restaction!" % name


class Hello:
    """
    Hello world

    $shared:
        name:
            name?str&default="world": Your name
        message:
            message?str: Welcome message
    """

    def __init__(self, api):
        self.api = api

    def get(self, name):
        """
        Welcome to flask-restaction

        $input: "@name"
        $output: "@message"
        """
        return Welcome(name)

    def get_me(self):
        """
        Get welcome for me

        $output: "@message"
        """
        return Welcome(g.token["name"])

    def post(self, name):
        """Create auth headers

        $input: "@name"
        """
        headers = self.api.gen_auth_headers({"name": name})
        return "OK", headers

api.add_resource(Hello, api)
api.add_resource(type('Docs', (), {'get': api.meta_view}))

if __name__ == '__main__':
    app.run(debug=True)
