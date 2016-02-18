#!/usr/bin/env python
# coding: utf-8
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
            "res_role": ["actions"]
        }
    }

- resource is lowercase and resource.json is for programer
- permission.json is for website manager, and can be changed via UI
- owner, other are special res_role,
  other means guest/anonymous, owner means allow all actions
- root is special user_role, means allow all resources
"""
from __future__ import unicode_literals, absolute_import, print_function
from flask import g, abort, request
from flask import json
import codecs
import jwt
import copy
import os
from datetime import datetime, timedelta
from . import pattern_action, logger
from .api import load_options


def load_config(resource_json, permission_json):
    """load resource.json and permission.json

    :param resource_json: path of resource.json
    :param permission_json: path of permission.json
    """
    try:
        with codecs.open(resource_json, encoding="utf-8") as f_resource, \
                codecs.open(permission_json, encoding="utf-8") as f_permission:
            return json.load(f_resource), json.load(f_permission)
    except IOError as e:
        e.strerror = "can't load auth config file: %s" % e.strerror
        raise


def parse_config(resource, permission):
    """parse resource and permission, make it easy to use

    :param resource: dict from resource.json
    :param permission: dict from permission.json
    :return:
        ::

            {
                (user_role, resource): (res_role, [actions])
            }

    """
    result = {}
    assert "root" not in permission, "user_role: root can't be modified"
    # user_role is None, for anonymous user
    # and set default owner,other
    for resource_name in resource:
        res = resource[resource_name]
        res.setdefault("owner", [])
        res.setdefault("other", [])
        actions = list(set(res["other"]))
        for action in actions:
            assert pattern_action.match(action), \
                "invalid action: %s.%s" % (resource_name, action)
        result[(None, resource_name)] = ("other", actions)
    for user_role in permission:
        for resource_name, res_role in permission[user_role].items():
            assert resource_name.islower(), \
                "resource should in lowercase: %s" % resource_name
            assert resource_name in resource, \
                "resource %s not exists" % resource_name
            res = resource[resource_name]
            assert res_role in res, \
                "res_role %s.%s not exists" % (resource_name, res_role)
            actions = list(set(res.get(res_role, []) + res["other"]))
            for action in actions:
                assert pattern_action.match(action), \
                    "invalid action: %s.%s" % (resource_name, action)
            result[(user_role, resource_name)] = (res_role, actions)
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

DEFAULT_OPTIONS = {
    "fn_user_role": None,
    "resource_json": "resource.json",
    "permission_json": "permission.json",
    "auth_header": "Authorization",
    "auth_secret": "SECRET",
    "auth_alg": "HS256",
    "auth_exp": 3600,
}


class Auth(object):
    """Auth

    usage::

        def fn_user_role(token):
            if token and 'id' in token:
                user_id = token[id]
                # query user from database
                return user_role
            else:
                return None

        Auth(api, fn_user_role=fn_user_role)

    :param fn_user_role: a function that return user_role
    :param resource_json: path of resource.json, default ``resource.json``
    :param permission_json: path of permission.json,
                            default ``permission.json``
    :param auth_header: request header of auth, default ``Authorization``
    :param auth_secret: secret of generate auth token, default ``SECRET``
    :param auth_alg: algorithm of generate auth token, default ``HS256``,
                     see json-web-token or pyjwt for more infomations
    :param auth_exp: expiration time of auth token, default ``3600`` seconds
    """

    def __init__(self, api=None, **kwargs):
        self._options = kwargs
        if api is not None:
            self.init_api(api, **kwargs)

    def init_api(self, api, **kwargs):
        """just like flask's ext init_app()"""
        options = load_options(DEFAULT_OPTIONS, api.app, self._options, kwargs)
        assert options["fn_user_role"] is not None, "fn_user_role is required"
        self.__dict__.update(options)

        if not os.path.isabs(self.resource_json):
            self.resource_json = os.path.join(
                api.app.root_path, self.resource_json)
        if not os.path.isabs(self.permission_json):
            self.permission_json = os.path.join(
                api.app.root_path, self.permission_json)
        self.resource, self.permission = load_config(
            self.resource_json, self.permission_json)
        self.config = parse_config(self.resource, self.permission)
        api.auth = self
        api.before_request(self._before_request)

    def permit(self, user_role, resource, action):
        """check permit"""
        return permit(self.config, user_role, resource, action)

    def update_permission(self, user_role, resource):
        """add or update user_role"""
        permission = copy.deepcopy(self.permission)
        permission.setdefault(user_role, {})
        permission[user_role].update(resource)
        self._save_permission(permission)

    def delete_permission(self, user_role):
        """delete user_role"""
        if user_role in self.permission:
            permission = copy.deepcopy(self.permission)
            del permission[user_role]
            self._save_permission(permission)

    def _save_permission(self, permission):
        """save permission to file"""
        try:
            config = parse_config(self.resource, permission)
            with codecs.open(self.permission_json, "w", encoding="utf-8") as f:
                json.dump(permission, f, indent=4,
                          ensure_ascii=False, sort_keys=True)
            self.permission = permission
            self.config = config
        except IOError as ex:
            ex.strerror = "can't save permission to file: %s" % ex.strerror
            raise
        except AssertionError as ex:
            raise ValueError(ex.message)

    def gen_token(self, token, auth_exp=None):
        """generate auth token

        :param token: a dict like ``{"id": user_id, ...}``
        :param auth_exp: seconds of jwt token expiration time
                         , default is ``self.auth_exp``
        :return: string
        """
        if auth_exp is None:
            auth_exp = self.auth_exp
        token["exp"] = datetime.utcnow() + timedelta(seconds=auth_exp)
        return jwt.encode(token, self.auth_secret, algorithm=self.auth_alg)

    def gen_header(self, token, auth_exp=None):
        """generate auth header

        :return: ``{self.auth_header: self.gen_token(token)}``
        """
        auth = {self.auth_header: self.gen_token(token)}
        return auth

    def _before_request(self):
        """check permission"""
        token = self.parse_auth_header()
        g.token = token
        user_role = self._fn_user_role(token)
        g.user_role = user_role
        perm, res_role = permit(self.config, user_role, g.resource, g.action)
        g.res_role = res_role
        if not perm:
            if token is None:
                abort(403, "permission deny: your token is invalid")
            else:
                abort(403, "You don't have permission: user_role=%s" % user_role)

    def parse_auth_header(self):
        """parse http header auth token

        :return: me
        """
        token = request.headers.get(self.auth_header)
        options = {
            'require_exp': True,
        }
        try:
            return jwt.decode(token, self.auth_secret,
                              algorithms=[self.auth_alg], options=options)
        except jwt.InvalidTokenError:
            pass
        except AttributeError:
            # jwt's bug when token is None or int
            # https://github.com/jpadilla/pyjwt/issues/183
            pass
        logger.debug("InvalidToken: %s" % token)
        return None

    def _fn_user_role(self, me):
        """exec fn_user_role"""
        if self.fn_user_role:
            try:
                return self.fn_user_role(me)
            except Exception as ex:
                logger.exception(
                    "Error raised when get user_role: %s" % str(ex))
        return None
