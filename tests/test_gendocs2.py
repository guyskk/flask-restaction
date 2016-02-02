#!/usr/bin/env python
# coding: utf-8
"""中文test_gendocs"""
from flask import Flask
from flask_restaction import Api, Resource, Gen


def test_gendocs():
    class Hello(Resource):
        """中文docstring for Hello哈哈"""

        def get(self):
            """你好啊"""
            return "hello"

    app = Flask(__name__)
    api = Api(app, docs=__doc__)
    api.add_resource(Hello)
    gen = Gen(api)
    gen.resjs('static/res.js')
    gen.resdocs('static/resdocs.html', resjs='static/res.js',
                bootstrap="bootstrap.css")
