# coding:utf-8
from __future__ import unicode_literals
from flask import g, abort
from flask.ext.restaction import Resource, schema
import time
from collections import OrderedDict


class Todos(Resource):
    """docstring for Todos"""
    pagenum = "+int", 1
    pagesize = "+int", 10
    todo_id = "int&required"
    content = "safestr&required"
    message = "unicode"
    todo = schema("todo_id", "content")
    schema_inputs = {
        "get": schema("todo_id"),
        "get_list": schema("pagenum", "pagesize"),
        "post": schema("content"),
        "put": todo,
        "delete": schema("todo_id")
    }
    schema_outputs = {
        "get": schema("content"),
        "get_list": schema(["todo"]),
        "post": todo,
        "put": schema("message"),
        "delete": schema("message"),
    }

    def __init__(self):
        todos_key = g.me["id"] + ".todos"
        g.db.setdefault(todos_key, OrderedDict())
        self.todos = g.db[todos_key]
        self.todos_key = todos_key

    def get(self, todo_id):
        if todo_id not in self.todos:
            abort(404)
        return self.todos[todo_id]

    def get_list(self, pagenum, pagesize):
        todos = self.todos.items()[(pagenum - 1) * pagesize:pagenum * pagesize]
        return [{"todo_id": todo_id, "content": content} for todo_id, content in todos]

    def post(self, content):
        todo_id = int(time.time() * 1000)
        self.todos[todo_id] = content
        g.db[self.todos_key] = self.todos
        g.db.commit()
        return {
            "todo_id": todo_id,
            "content": content
        }

    def put(self, todo_id, content):
        if todo_id not in self.todos:
            abort(404)
        self.todos[todo_id] = content
        g.db[self.todos_key] = self.todos
        g.db.commit()
        return {"message": "OK"}

    def delete(self, todo_id):
        if todo_id not in self.todos:
            abort(404)
        del self.todos[todo_id]
        g.db[self.todos_key] = self.todos
        g.db.commit()
        return {"message": "OK"}
