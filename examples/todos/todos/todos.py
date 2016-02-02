#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function
from flask_restaction import Resource
import datetime
from . import db, model
from flask import g


class Todos(Resource):
    """docstring for Todos"""
    paging = {
        "pagenum": "+int&default=1",
        "pagesize": "int(5,50)&default=10"
    }
    info = {
        "todoid": "+int&required",
        "name": "safestr&required",
        "content": "safestr&required",
        "date": ("datetime", "last modified datetime")
    }
    schema_inputs = {
        "get": {"todoid": "+int&required"},
        "get_list": paging,
        "post": {
            "name": "safestr&required",
            "content": "safestr&required"
        },
        "put": {
            "todoid": "+int&required",
            "name": "safestr&required",
            "content": "safestr&required"
        },
        "delete": {"todoid": "+int&required"}
    }
    schema_outputs = {
        "get": info,
        "get_list": [info],
        "post": info,
        "put": info,
        "delete": {"message": "safestr"}
    }
    output_types = [model.Todo]

    def get(self, todoid):
        return model.Todo.query.get_or_404(todoid)

    def get_list(self, pagenum, pagesize):
        return model.Todo.query.filter_by(userid=g.token["id"])\
            .paginate(pagenum, pagesize).items

    def post(self, name, content):
        date = datetime.datetime.utcnow()
        todo = model.Todo(userid=g.token["id"],
                          name=name, content=content, date=date)
        db.session.add(todo)
        db.session.commit()
        return todo

    def put(self, todoid, name, content):
        todo = model.Todo.query.get_or_404(todoid)
        todo.name = name
        todo.content = content
        todo.date = datetime.datetime.utcnow()
        db.session.commit()
        return todo

    def delete(self, todoid):
        todo = model.Todo.query.get_or_404(todoid)
        db.session.delete(todo)
        db.session.commit()
        return {"message": "OK"}
