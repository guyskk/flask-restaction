# coding:utf-8
import os
import sys
sys.path.append(os.path.realpath("../../"))
from flask import Flask
from flask_restaction import Api

# app.config["RESOURCE_JWT_SECRET"] = "RESOURCE_JWT_SECRET"

app = Flask(__name__)
api = Api(app)
app.config["JSON_AS_ASCII"] = False

from users import User
from todos import Todo
api.add_resource(User)
api.add_resource(Todo)
api.gen_resjs()
