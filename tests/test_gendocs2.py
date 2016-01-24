#!/usr/bin/env python
# coding: utf-8

from flask import Flask
from flask_restaction import Api, Resource


def test_gendocs_str():
    class Hello(Resource):
        """中文docstring for Hello哈哈"""

        def get(self):
            """你好啊"""
            return "hello"

    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Hello)
    api.gen_resdocs()
    api.gen_resjs()


def test_gendocs_unicode():
    class Hello(Resource):
        """中文docstring for Hello哈哈"""

        def get(self):
            """你好啊"""
            return "hello"

    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Hello)
    api.gen_resdocs()
    api.gen_resjs()
