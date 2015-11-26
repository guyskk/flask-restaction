# coding:utf-8

from __future__ import unicode_literals
from __future__ import absolute_import

from flask_restaction import Resource


class Profiler(Resource):
    """Api Profiler"""

    def __init__(self, profiler_data):
        self.profiler_data = profiler_data

    def get(self):
        return self.profiler_data
