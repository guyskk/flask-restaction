# coding:utf-8
from __future__ import unicode_literals
from flask_restaction import Res
from todos import db, api, create_app
import pytest


@pytest.yield_fixture(scope='function')
def app():
    app = create_app(test=True)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture(scope='function')
def guest(app):
    return Res(api)


@pytest.fixture(scope='function')
def user(guest):
    resp = guest.user.post({
        "email": "tester@todos.com",
        "password": "123456"
    })
    assert resp.status_code == 200
    return resp.json


@pytest.fixture(scope='function')
def res(guest, user):
    resp = guest.user.post_login({
        "email": "tester@todos.com",
        "password": "123456"
    })
    assert resp.status_code == 200
    auth_headers = {'Authorization': resp.headers['Authorization']}
    return Res(api, headers=auth_headers)
