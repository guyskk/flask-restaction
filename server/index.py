"""Test Server"""
from flask import Flask, Response, request, abort, redirect, url_for, g
from flask_restaction import Api, TokenAuth
from flask_cors import CORS
from os.path import abspath, dirname, join

app = Flask(__name__)
app.secret_key = "secret_key"
CORS(app, expose_headers=['Authorization'])
metafile = abspath(join(dirname(__file__), "meta.json"))
api = Api(app, metafile=metafile)

auth = TokenAuth(api)


@auth.get_role
def get_role(token):
    if token:
        return token["role"]
    return "guest"


class Test:
    """
    $shared:
        name: str&default="world"
    """

    def __init__(self, api):
        self.api = api

    def get(self, name):
        """
        $input:
            name@name: Your name
        """
        return {'hello': name}

    def post(self, name):
        """
        $input:
            name@name: Your name
        """
        return {'hello': name}

    def post_name(self, name):
        """
        $input:
            name@name: Your name
        """
        return {'hello': name}

    def put(self, name):
        """
        $input:
            name@name: Your name
        """
        return {'hello': name}

    def patch(self, name):
        """
        $input:
            name@name: Your name
        """
        return {'hello': name}

    def delete(self, name):
        """
        $input:
            name@name: Your name
        """
        return {'hello': name}

    def get_404(self):
        abort(404)

    def get_403(self):
        abort(403)

    def get_401(self):
        abort(401)

    def get_400(self):
        abort(400)

    def get_302(self):
        return redirect(url_for('test'))

    def get_500(self):
        abort(500)

    def get_binary(self):
        def generate():
            rows = '0123456789'
            for i in range(1, 10):
                yield ','.join(rows[:i]) + '\n'
        return Response(generate(), mimetype='text/csv')

    def post_upload(self):
        files = request.files.getlist('upload')
        return {'recv': len(files)}

    def post_login(self, name):
        """
        $input:
            name@name: Your name
        """
        g.token = token = {'role': 'admin', 'name': name}
        return token

    def get_me(self):
        return g.token


api.add_resource(Test, api)
app.route('/')(api.meta_view)

if __name__ == '__main__':
    app.run(debug=True)
