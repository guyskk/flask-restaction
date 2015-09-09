import sys
import os
sys.path.insert(0, os.path.abspath("../"))
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
api.gen_resjs()

if __name__ == '__main__':
    app.run(debug=True)
