from flask import Flask
from flask_restaction import Resource, Api, Gen

app = Flask(__name__)
api = Api(app)


class Hello(Resource):
    """hello world"""
    schema_inputs = {
        "get": {
            "name": ("safestr&default='world'", "your name")
        }
    }
    schema_outputs = {
        "get": {"hello": "unicode&required"}
    }

    def get(self, name):
        """welcome to flask-restaction"""
        return {"hello": name}

api.add_resource(Hello)

gen = Gen(api)
gen.resjs('static/res.js')
gen.resdocs('static/resdocs.html', resjs='/static/res.js',
            bootstrap='/static/bootstrap.min.css')

if __name__ == '__main__':
    app.run(debug=True)
