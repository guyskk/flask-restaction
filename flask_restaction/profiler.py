# coding:utf-8

from __future__ import unicode_literals
from __future__ import absolute_import

from flask_restaction import Resource


class Profiler(Resource):
    """Api Profiler

    profiler_data::

        {
            "resource": {
                "action": {
                    "count":"int"
                    "avg":"float"
                    "max":"float"
                    "min":"float"
                },
                ...
            },
            ...
        }
    """

    def __init__(self, profiler_data):
        self.profiler_data = profiler_data

    def get(self):
        """get profiler data"""
        return self.profiler_data
