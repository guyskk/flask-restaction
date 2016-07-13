"""Hello API"""
from flask import Flask
from flask_restaction import Api

app = Flask(__name__)
api = Api(app, docs=__doc__, metafile="meta.json")
app.secret_key = b'\x7fk\x98\x06xl\xdfU\xae?\x92^\t~:b\x83\xe3uX\xaf\x9a\x01G'


@api.get_role
def get_role(token):
    if token is None:
        return "guest"
    else:
        return "admin"


class Hello:
    """Hello world"""

    def get(self, name):
        """Welcome to flask-restaction

        $input:
            name?str&escape&default="world": Your name
        $output:
            message?str&maxlen=60: Welcome message
        """
        return {
            "message": "Hello %s, Welcome to flask-restaction!" % name
        }

    def get_token(self, name):
        """Create auth headers

        $input:
            name?str: 角色
        $output:
            message?str: 提示信息
        """
        headers = api.gen_auth_header({"name": name})
        return {"message": "OK"}, headers

api.add_resource(Hello)


if __name__ == '__main__':
    app.run(debug=True)
