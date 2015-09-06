# coding:utf-8
from flask import Flask
from flask_restaction import Api
from flask_restaction import Resource
from flask_restaction import abort
from datetime import datetime

app = Flask(__name__)
api = Api(app)
app.config["JSON_AS_ASCII"] = False
app.config["RESOURCE_JWT_SECRET"] = "RESOURCE_JWT_SECRET"
todos = {
    1: {
        "name": "todo1",
        "date": datetime.utcnow(),
        "finish": False
    },
}


class Todo(Resource):

    """docstring for Todo"""

    schema_id = ("id", {
        "desc": "todo's id",
        "required": True,
        "validate": "int",
    })
    schema_name = ("name", {
        "desc": u"名称",
        "required": True,
        "validate": "re_name",
    })
    schema_date_out = ("date", {
        "desc": u"时间",
        "required": True,
        "validate": lambda v: (True, v.isoformat()),
    })
    schema_date_in = ("date", {
        "desc": u"时间",
        "required": True,
        "validate": "datetime",
        "default": datetime.now
    })
    schema_finish = ("finish", {
        "desc": u"是否已完成",
        "required": True,
        "validate": "bool",
        "default": False
    })
    schema_inputs = {
        "get": dict([schema_id]),
        "post": dict([schema_name, schema_date_in, schema_finish]),
        "put": dict([schema_id, schema_name, schema_date_in, schema_finish]),
        "delete": dict([schema_id]),
    }
    schema_out = dict([schema_id, schema_name, schema_date_out, schema_finish])
    schema_outputs = {
        "get": schema_out,
        "get_list": [schema_out],
        "post": schema_out,
        "put": schema_out,
    }
    types = []

    def get(self, id):

        if id in todos:
            return dict(todos[id], id=id)
        else:
            abort(404, "Not Found")

    def get_list(self):
        return [dict(v, id=k) for k, v in todos.items()]

    def post(self, **todo):
        if not todos:
            newid = 1
        else:
            newid = sorted(todos.keys())[-1] + 1
        todos[newid] = todo
        return dict(todo, id=newid)

    def put(self, id, **todo):
        if id in todos:
            todos[id] = todo
            return dict(todo, id=id)
        else:
            abort(404, "Not Found")

    def delete(self, id):
        if id in todos:
            del todos[id]

api.add_resource(Todo)
api.gen_res_js()

if __name__ == '__main__':
    app.run(debug=True)
