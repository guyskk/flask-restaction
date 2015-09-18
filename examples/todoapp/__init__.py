# coding:utf-8
# import imp
# import os
# fp, pathname, description = imp.find_module("flask_restaction", [os.path.abspath("../../")])
# imp.load_module("flask_restaction", fp, pathname, description)

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
api.gen_resdocs()
