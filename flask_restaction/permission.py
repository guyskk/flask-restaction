#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function
from flask import abort
from flask_restaction import Resource


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
            "resource": {
                "res": ["res_role", ...],
                ...
            }
        }

    json struct of post::

        {
            "user_role": "user_role"
            "resource": {
                "res": "res_role",
                ...
            }
        }

    :param auth: Auth
    """
    schema_inputs = {
        "get_permit": {
            "user_role": "unicode&required",
            "resource": "unicode&required",
            "action": "unicode&required"
        },
        "post": {
            "user_role": "unicode&required",
            "resource": "any&required"
        },
        "delete": {"user_role": "unicode&required"},
    }
    schema_outputs = {
        "get_permit": {"permit": "bool&required"},
        "post": {"message": "unicode&required"},
        "delete": {"message": "unicode&required"}
    }

    def __init__(self, auth):
        self.auth = auth
        self.resource = {k: list(set(v) | set(['owner', 'other']))
                         for k, v in self.auth.resource.items()}

    def get(self):
        """get permission info
        """
        return {
            "resource": self.resource,
            "permission": self.auth.permission
        }

    def get_permit(self, user_role, resource, action):
        """check if the role can access the resource and action
        """
        p, res_role = self.auth.permit(user_role, resource, action)
        return {"permit": p}

    def post(self, user_role, resource):
        """add or update user_role"""
        try:
            self.auth.update_permission(user_role, resource)
            return {"message": "OK"}
        except Exception as ex:
            abort(400, ex.message)

    def delete(self, user_role):
        """delete user_role"""
        try:
            self.auth.delete_permission(user_role)
            return {"message": "OK"}
        except Exception as ex:
            abort(400, ex.message)
