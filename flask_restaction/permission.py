#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function

"""
permission.json struct::

    {
        "user_role": {
            "resource": "res_role"
        },
        "user_role": {
            "resource": "owner"
        },
        "user_role": {
            "resource": "other"
        }
    }

resource.json struct::

    {
        "resource": {
            "other": ["actions"],
            "res_role": ["action"]
        }
    }

- resource is lowercase and resource.json is for programer
- permission.json is for website manager, and can be changed via UI
- owner, other are special res_role,
  other means guest/anonymous, owner means allow all actions
- root is special user_role, means allow all resources
- every one can access 'other' actions,
  needn't add that actions to every res_role
"""

import json
import codecs
import copy
from flask import abort
from flask_restaction import pattern_action, Resource


def load_config(resource_json, permission_json):
    """load resource.json and permission.json

    :param resource_json: path of resource.json
    :param permission_json: path of permission.json
    """
    try:
        with codecs.open(resource_json, encoding="utf-8") as f_resource, \
                codecs.open(permission_json, encoding="utf-8") as f_permission:
            resource = json.load(f_resource)
            permission = json.load(f_permission)
    except IOError as e:
        e.strerror = 'Unable to load configuration file (%s)' % e.strerror
        raise
    return resource, permission


def parse_config(resource, permission):
    """parse resource and permission, make it easy to use

    :param resource: dict from resource.json
    :param permission: dict from permission.json
    :return:
    permission_config::

        {
            (user_role, resource): (res_role, [actions])
        }
    """
    result = {}
    assert "root" not in permission, "user_role: root can't be modified"
    for user_role in permission:
        for resource_name, res_role in permission[user_role].items():
            assert resource_name.islower(), \
                "resource should in lowercase: %s" % resource_name
            assert resource_name in resource, \
                "resource %s not exists" % resource_name
            res = resource[resource_name]
            if res_role != "owner" and res_role != "other":
                assert res_role in res, \
                    "res_role %s.%s not exists" % (resource_name, res_role)
            actions = list(set(res.get(res_role, []) + res.get("other", [])))
            for action in actions:
                assert pattern_action.match(action), \
                    "invalid action: %s.%s" % (resource_name, action)
            result[(user_role, resource_name)] = (res_role, actions)
    # user_role is None, for anonymous user
    for resource_name in resource:
        result[(None, resource_name)] = \
            ("other", resource[resource_name].get("other", []))
    return result


def permit(config, user_role, resource, action):
    """check permission

    :return: (permit, res_role)
    """
    if user_role == "root":
        return (True, "owner")
    result = config.get((user_role, resource))
    if result is None:
        # get res_role of anonymous user
        result = config.get((None, resource))
    if result is None:
        return (False, None)
    res_role, actions = result
    if res_role == "owner":
        return (True, res_role)
    else:
        return (action in actions, res_role)


class Permission(Resource):

    """Permission

    json struct of get::

        {
            "permission": {
                "user_role": {
                    "resource": "res_role",
                    ...
                },
                ...
            }
            "resources": {
                "resource": ["res_role", ...],
                ...
            }
        }

    json struct of post::

        {
            "user_role": "user_role"
            "resources": {
                "resource": "res_role",
                ...
            }
        }
    """
    schema_inputs = {
        "get_permit": {
            "user_role": "unicode&required",
            "resource": "unicode&required",
            "action": "unicode&required"
        },
        "post": {
            "user_role": "unicode&required",
            "resources": "any&required"
        },
        "delete": {"user_role": "unicode&required"},
    }
    schema_outputs = {
        "get_permit": {"permit": "bool&required"},
        "post": {"message": "unicode&required"},
        "delete": {"message": "unicode&required"}
    }

    def __init__(self, api):
        self.api = api

    def get_permit(self, user_role, resource, action):
        """check if the role can access the resource and action
        """
        p, res_role = permit(self.api.permission_config,
                             user_role, resource, action)
        return {"permit": p}

    def get(self):
        """get permission info
        """
        resources = {
            resource: list(set(res_roles) | set(["owner", "other"]))
            for resource, res_roles in self.api.permission_resource.items()
        }
        return {
            "resources": resources,
            "permission": self.api.permission_permission
        }

    def post(self, user_role, resources):
        """add or update user_role"""
        permission = copy.deepcopy(self.api.permission_permission)
        permission.setdefault(user_role, {})
        try:
            permission[user_role].update(resources)
        except Exception as ex:
            abort(400, ex.message)
        self._save_permission(permission)
        return {"message": "OK"}

    def delete(self, user_role):
        """delete user_role"""
        if user_role in self.api.permission_permission:
            permission = copy.deepcopy(self.api.permission_permission)
            del permission[user_role]
            self._save_permission(permission)
        return {"message": "OK"}

    def _save_permission(self, permission):
        try:
            config = parse_config(self.api.permission_resource, permission)
            with codecs.open(self.api.permission_json, "w", encoding="utf-8") as f:
                json.dump(permission, f, indent=4,
                          ensure_ascii=False, sort_keys=True)
            self.api.permission_permission = permission
            self.api.permission_config = config
        except IOError as ex:
            abort(400, "can't save permission to file: %s" % ex)
        except AssertionError as ex:
            abort(400, ex.message)
