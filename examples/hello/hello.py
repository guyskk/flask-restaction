from flask import Flask
from flask.ext.restaction import Resource, Api, schema

app = Flask(__name__)
api = Api(app)


class Hello(Resource):
    """docstrings Hello"""
    name = "safestr&required", "world", "you name"
    schema_inputs = {
        "get": schema("name")
    }

    def get(self, name):
        """docstrings get"""
        return {"hello": name}

api.add_resource(Hello)
api.gen_resjs()
api.gen_resdocs()

if __name__ == '__main__':
    app.run(debug=True)
