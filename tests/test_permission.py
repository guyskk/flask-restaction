# coding:utf-8

from __future__ import unicode_literals
from __future__ import absolute_import
from flask_restaction import Permission


def test_permission():
    p = Permission(filepath="tests/test_permission.json")
    assert p.permit("user.admin", "photo", "get")
    assert p.permit("user.userA", "photo", "get")
    assert not p.permit("user.userA", "message", "Post")
    assert not p.permit("user.userA", "message", "delete")
    assert p.permit("user.userB", "photo", "get_list")
    assert not p.permit("user.userB", "photo", "get")
    assert p.permit("user.userB", "message", "post")
    assert not p.permit("user.userB", "message", "delete")
    assert p.permit("user.userXX", "photo", "get")
    assert not p.permit("user.userXX", "photo", "delete")


def test_permission2():
    p = Permission(jsonstr="{}")
    p.add("user.admin", "*", "get")
    p.add("user.admin", "photo", "post")
    p.add("user.userA", "photo*", "get")
    p.add("user.userA", "photo", "get_list")
    p.add("user.userB", "photo", "get_list")
    p.add("user.userB", "photo", "post")
    assert p.permit("user.admin", "message", "get")
    assert p.permit("user.admin", "photo", "get")
    assert p.permit("user.userA", "photo", "get")
    assert p.permit("user.userA", "photo", "Post")
    assert not p.permit("user.userA", "message", "delete")
    assert p.permit("user.userB", "photo", "get_list")
    assert p.permit("user.userB", "photo", "post")
    assert not p.permit("user.userXX", "photo", "get")
    assert not p.permit("user.userXX", "photo", "delete")
    p.remove("user.userB", "photo", "post")
    p.remove("user.userB", "photo", "delete")
    assert not p.permit("user.userB", "message", "post")
    assert not p.permit("user.userB", "message", "delete")


def test_resource_user():
    p = Permission(filepath="tests/test_permission.json")
    p.resource_user["photo"] == "user"
    p.resource_user["message"] == "user"


def test_userroles():
    p = Permission(filepath="tests/test_permission.json")
    assert set(p.userroles["user"]) == set(["admin", "userA", "userB"])
