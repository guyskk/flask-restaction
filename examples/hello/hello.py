"""
# Hello API

Support markdown in docs:

![markdown](https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Markdown-mark.svg/500px-Markdown-mark.svg.png)

执行以下命令，将会在static目录下生成res.js文件:
```
resjs http://127.0.0.1:5000/docs -d static/res.js
```
之后打开chrome控制台就可以用res.js调用API了。
"""
from flask import Flask, g
from flask_restaction import Api, TokenAuth

app = Flask(__name__)
api = Api(app, docs=__doc__, metafile="meta.json")
app.secret_key = b'secret_key'
auth = TokenAuth(api)


@auth.get_role
def get_role(token):
    if token:
        return token.get('role', 'guest')
    return 'guest'


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
        g.token = {"name": name, "role": "normal"}
        return "OK"


api.add_resource(Hello, api)
api.add_resource(type('Docs', (), {'get': api.meta_view}))

if __name__ == '__main__':
    app.run(debug=True)
