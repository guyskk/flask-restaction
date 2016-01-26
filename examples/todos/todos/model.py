#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function

from . import db


class User(db.Model):
    userid = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.Unicode(240), index=True, unique=True, nullable=False)
    pwdhash = db.Column(db.Unicode(240), nullable=False)
    name = db.Column(db.Unicode(240), default='', nullable=False)
    photo = db.Column(db.Unicode(240), default='', nullable=False)
    date = db.Column(db.DateTime(), nullable=False)


class Todo(db.Model):
    todoid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Unicode(240), index=True, nullable=False)
    content = db.Column(db.UnicodeText, nullable=False)
    date = db.Column(db.DateTime(), index=True, nullable=False)
