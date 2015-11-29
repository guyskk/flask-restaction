# coding:utf-8

from __future__ import unicode_literals
from __future__ import absolute_import
from flask_restaction.permission import permit, load_config, parse_config


def test_permission():
    resource_json = "tests/test_resource.json"
    permission_json = "tests/test_permission.json"
    resource, permission = load_config(resource_json, permission_json)
    config = parse_config(resource, permission)

    assert permit(config, "roleA", "photo", "get")[0]
    assert permit(config, "roleB", "photo", "get")[0]
    assert permit(config, "roleC", "photo", "get")[0]

    assert not permit(config, "roleA", "photo", "post")[0]
    assert not permit(config, "roleB", "photo", "post")[0]
    assert permit(config, "roleC", "photo", "post")[0]

    assert permit(config, "roleA", "article", "get")[0]
    assert permit(config, "roleB", "article", "get")[0]
    assert permit(config, "roleC", "article", "get")[0]

    assert permit(config, "roleA", "article", "post")[0]
    assert permit(config, "roleB", "article", "post")[0]
    assert not permit(config, "roleC", "article", "post")[0]

    assert not permit(config, "roleA", "article", "delete")[0]
    assert permit(config, "roleB", "article", "delete")[0]
    assert not permit(config, "roleC", "article", "delete")[0]


# def test_permission2():
#     p = Permission(jsonstr="{}")
#     p.add("user.admin", "*", "get")
#     p.add("user.admin", "photo", "post")
#     p.add("user.userA", "photo*", "get")
#     p.add("user.userA", "photo", "get_list")
#     p.add("user.userB", "photo", "get_list")
#     p.add("user.userB", "photo", "post")
#     assert p.permit("user.admin", "message", "get")
#     assert p.permit("user.admin", "photo", "get")
#     assert p.permit("user.userA", "photo", "get")
#     assert p.permit("user.userA", "photo", "Post")
#     assert not p.permit("user.userA", "message", "delete")
#     assert p.permit("user.userB", "photo", "get_list")
#     assert p.permit("user.userB", "photo", "post")
#     assert not p.permit("user.userXX", "photo", "get")
#     assert not p.permit("user.userXX", "photo", "delete")
#     p.remove("user.userB", "photo", "post")
#     p.remove("user.userB", "photo", "delete")
#     assert not p.permit("user.userB", "message", "post")
#     assert not p.permit("user.userB", "message", "delete")


# def test_resource_user():
#     p = Permission(filepath="tests/test_permission.json")
#     p.resource_user["photo"] == "user"
#     p.resource_user["message"] == "user"


# def test_userroles():
#     p = Permission(filepath="tests/test_permission.json")
#     assert set(p.userroles["user"]) == set(["admin", "userA", "userB"])
