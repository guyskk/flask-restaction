# coding:utf-8
from flask import Flask
from flask_restaction import Api

app = Flask(__name__)
api = Api(app)
app.config["JSON_AS_ASCII"] = False

from users import User
from todos import Todo
api.add_resource(User)
api.add_resource(Todo)
api.gen_resjs()
