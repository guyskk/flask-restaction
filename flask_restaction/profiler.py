# coding:utf-8

from __future__ import unicode_literals
from __future__ import absolute_import

from flask import g
from flask_restaction import Resource
import functools
import time


class Profiler(Resource):
    """
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

    def __init__(self):
        self.data = {}

    def add(self, resource, action, elapsed):
        self.data.setdefault(resource, {})
        self.data[resource].setdefault(
            action, {"max": elapsed, "min": elapsed, "avg": elapsed, "count": 0})
        act = self.data[resource][action]
        act["max"] = max(act["max"], elapsed)
        act["min"] = min(act["min"], elapsed)
        act["count"] += 1
        p = 1.0 / float(act["count"])
        act["avg"] = act["avg"] * (1 - p) + elapsed * p

    def measure(self, fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            time_begin = time.time()
            ret = fn(*args, **kwargs)
            time_end = time.time()
            self.add(g.resource, g.action, time_end - time_begin)
            return ret
        return wrapper

    def get(self):
        """profiler data"""
        return self.data
