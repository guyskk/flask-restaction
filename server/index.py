from flask import Flask, Response, request, abort, redirect, url_for, g
from flask_restaction import Api, Resource, Auth
from flask_cors import CORS

app = Flask(__name__)
CORS(app, expose_headers=['Authorization'])


def fn_user_role(token):
    if token and 'name' in token:
        return token['name']

api = Api(app)
auth = Auth(api, fn_user_role=fn_user_role)


class Test(Resource):

    name = {
        'name': 'unicode&default="world"'
    }
    schema_inputs = {
        'get': name,
        'post': name,
        'put': name,
        'delete': name,
        'get_404': None,
        'get_403': None,
        'get_401': None,
        'get_400': None,
        'get_302': None,
        'get_500': None,
        'post_name': 'unicode&default="world"',
        'get_binary': None,
        'post_upload': None,
        'post_login': name,
        'get_me': None,
    }

    def get(self, name):
        return {'hello': name}

    def post(self, name):
        return {'hello': name}

    def post_name(self, name):
        return {'hello': name}

    def put(self, name):
        return {'hello': name}

    def delete(self, name):
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
        token = {'name': name}
        headers = auth.gen_header(token)
        return token, headers

    def get_me(self):
        return g.token


api.add_resource(Test)

if __name__ == '__main__':
    app.run(debug=True)
