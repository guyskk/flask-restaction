#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function
from flask import g, abort
from flask_restaction import Resource
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from . import db, model, auth


class User(Resource):
    """User"""
    email_password = {
        "email": "email&required",
        "password": "password&required"
    }
    info = {
        "userid": "+int&required",
        "email": "email&required",
        "name": "name",
        "photo": "url",
        "date": ("datetime", "last modified datetime")
    }
    schema_inputs = {
        "get": None,
        "post": email_password,
        "post_login": email_password,
        "put": {"name": "name", "photo": "url"},
        "delete": None
    }
    schema_outputs = {
        "get": info,
        "post": info,
        "post_login": info,
        "put": info,
        "delete": {"message": "safestr"}
    }
    output_types = [model.User]

    def get(self):
        """get user info"""
        return model.User.query.get_or_404(g.token["id"])

    def post(self, email, password):
        """regisiter account"""
        user = model.User.query.filter_by(email=email).first()
        if user:
            abort(400, "user email=%s already exists" % email)
        pwdhash = generate_password_hash(password)
        date = datetime.datetime.utcnow()
        user = model.User(email=email, pwdhash=pwdhash, date=date)
        db.session.add(user)
        db.session.flush()
        user.name = "user%s" % user.userid
        db.session.commit()
        return user

    def post_login(self, email, password):
        """user login"""
        user = model.User.query.filter_by(email=email).first()
        if not user:
            abort(403, "Incorrect email or password")
        if not check_password_hash(user.pwdhash, password):
            abort(403, "Incorrect email or password")
        header = auth.gen_auth_header({"id": user.userid})
        user.date = datetime.datetime.utcnow()
        db.session.commit()
        return user, header

    def put(self, name, photo):
        """update user info"""
        user = model.User.query.get_or_404(g.token["id"])
        user.name = name
        user.photo = photo
        user.date = datetime.datetime.utcnow()
        db.session.commit()
        return user

    def delete(self):
        """delete account"""
        user = model.User.query.get_or_404(g.token["id"])
        db.session.delete(user)
        return {"message": "OK"}
