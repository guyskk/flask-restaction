#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function

from flask_restaction.permission import permit, load_config, parse_config


def test_permission():
    resource_json = "tests/testdata/resource.json"
    permission_json = "tests/testdata/permission.json"
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
