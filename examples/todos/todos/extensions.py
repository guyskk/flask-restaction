# coding:utf-8
from __future__ import unicode_literals

from flask_restaction import Api, Auth
from flask_sqlalchemy import SQLAlchemy

api = Api()
auth = Auth()
db = SQLAlchemy()
