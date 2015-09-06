from flask import Flask
from flask_restaction import Resource, Api

app = Flask(__name__)
api = Api(app)


class Hello(Resource):
    schema_inputs = {
        "get": {
            "name": {
                "desc": "you name",
                "required": True,
                "validate": "safestr",
                "default": "world"
            }
        }
    }

    def get(self, name):
        return {"hello": name}

api.add_resource(Hello)
api.gen_res_js()

if __name__ == '__main__':
    app.run(debug=True)
