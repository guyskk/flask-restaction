# coding:utf-8

"""
permission
~~~~~~~~~~~~~~~~

permission.json struct:

    {
        "*": {
            "user": ["get"]
        }
        "user.admin": {
            "*": []
        },
        "user.super": {
            "bloguser*": [],
            "userinfo*": []
        },
        "user.normal": {
            "comment": ["post", "post_by3", "put"],
            "user": ["get_me", "delete", "put_password"],
            "userinfo": ["get_me", "put"]
        },
        "monkey.king": {
            "monkey*": [],
            "fruit*": []
        }
    }

- the key's format is: ``user.role``.
- resource must be in lowercase.
- a resource can't belong to more than one user
"""
from __future__ import unicode_literals
from __future__ import absolute_import

import json
import re
import copy
from flask_restaction import pattern_action
pattern_role = re.compile(r"^([A-Za-z_][A-Za-z_0-9]+)\.([A-Za-z][A-Za-z_0-9]+)$")
pattern_res = re.compile(r"^([a-z_][a-z_0-9]+)$")


def validate(obj):
    """验证 permission 数据格式是否正确

    :param obj: 从 json 文件读取进来的dict对象
    """
    assert isinstance(obj, dict), \
        "invalid obj, obj must be a dict: '%s'" % obj
    for role, perm in obj.items():
        assert role == "*" or pattern_role.match(role),\
            "invalid role: '%s'" % role
        assert isinstance(perm, dict), \
            "invalid permission, permission must be a dict: '%s'" % perm
        for res, actions in perm.items():
            if res == "*":
                assert len(perm) == 1, \
                    "invalid resource, '*' resource must be the only resource"
                assert actions == [], \
                    "invalid resource, '*' resource's actions must be []"
            elif res[-1:] == "*":
                assert pattern_res.match(res[:-1]),\
                    "invalid resource: '%s'" % res
                assert actions == [], \
                    "invalid resource, actions must be []: '%s'" % res
            else:
                assert pattern_res.match(res), \
                    "invalid resource: '%s'" % res
                assert isinstance(
                    actions, list), \
                    "invalid actions, actions must be a list: '%s'" % actions
                for act in actions:
                    assert pattern_action.match(act), \
                        "invalid action: '%s'" % act


def parse_userroles(permission):
    """parse {user: [roles]} from permission

    For example:

        {
            "bloguser.admin": {
                "*": []
            },
            "bloguser.normal": {
                "githooks": ["post", "post_update"]
            }
        }

    will return:

        {
            "bloguser": ["admin", "normal"]
        }

    :return:

        {
            "user": ["role1","role2"...],
            ...
        }
    """
    d = {}
    for k in permission:
        if k == "*":
            continue
        user, role = pattern_role.findall(k)[0]
        d.setdefault(user, set())
        d[user].add(role)
    return d


def parse_resource_user(permission):
    """parse {resource: user} from permission"""
    d = {}
    for k in permission:
        if k == "*":
            continue
        user, role = pattern_role.findall(k)[0]
        ress = set(permission[k])
        for r in ress:
            if r != "*" and r[-1] == "*":
                r = r[:-1]
            if r not in d:
                d[r] = user
            elif d[r] != user:
                err = "a resource can't belong to more than one user"\
                    ": %s -> %s,%s" % (r, d[r], user)
                raise ValueError(err)
    return d


def make_all_role_validaters(userroles):
    """get all role_validater"""
    def make_role_validater(roles):
        def validater(v):
            if v in roles:
                return (True, v)
            else:
                return (False, "")

        return validater

    validaters = {}
    for user, roles in userroles.items():
        roles = ["%s.%s" % (user, r) for r in roles]
        validaters["role_%s" % user] = make_role_validater(roles)
    return validaters


class Permission(object):

    """Permission

    :param filepath: path of permission.json
    :param jsonstr: json string
    :param pdict: python dict
    """

    def __init__(self, filepath=None, jsonstr=None, pdict=None):

        if filepath is not None:
            try:
                with open(filepath) as f:
                    jsonstr = f.read()
            except IOError as e:
                e.strerror = 'Unable to load configuration file (%s)' % e.strerror
                raise
        if jsonstr is not None:
            pdict = json.loads(jsonstr)
        if pdict is not None:
            self._parse_permission(pdict)
        else:
            self.permission = {}

    def _parse_permission(self, p):
        """validate permission and parse permission"""
        validate(p)
        userroles = parse_userroles(p)
        role_validaters = make_all_role_validaters(userroles)
        resource_user = parse_resource_user(p)
        self.userroles = userroles
        self.role_validaters = role_validaters
        self.resource_user = resource_user
        self.permission = p

    def permit(self, role, resource, action):
        """判断角色是否有对应的权限

        :param role: 角色, '*' 或 None 表示 anonymous user
        :param resource: 资源
        :param action: 操作
        """
        if role is None:
            role = "*"
        if role in self.permission:
            perm = self.permission[role]
            for r, a in perm.items():
                if r == "*" or resource == r[:-1]:
                    return True
                elif resource == r:
                    return action in a
            return False
        elif "*" in self.permission:
            return self.permit("*", resource, action)
        else:
            return False

    def which_user(self, resource):
        """return resource belong to which user"""
        if resource not in self.resource_user:
            return self.resource_user.get("*")
        return self.resource_user.get(resource)

    def dumps(self):
        """将权限分配表导出为 json 格式字符串
        """
        return json.dumps(self.permission, indent=4)

    def dump(self, filepath):
        """将权限分配表用 json 格式保存到文件

        :param filepath: 文件路径
        """
        with open(filepath, "w") as f:
            f.write(self.dumps())

    def add(self, role, resource, action=None):
        """给角色添加权限，可以使用 ``'*'`` 符号。

        当 role, resource, action 不存在时会自动创建。

        :param role: 角色
        :param resource: 资源
        :param action: 操作

        例如::

            permission.add("user.admin", "*")
            permission.add("user.poster", "photo*")
            permission.add("*", "photo", "get")
        """
        p = copy.deepcopy(self.permission)
        if role not in p:
            p[role] = {}
        r = p[role]
        if resource == "*":
            r.clear()
            r[resource] = []
        elif resource[-1:] == "*":
            if resource[:-1] in r:
                del r[resource[:-1]]
            r[resource] = []
        elif "*" not in r and (resource + "*") not in r:
            if resource not in r:
                r[resource] = []
            if action not in r[resource]:
                r[resource].append(action)

        if p != self.permission:
            try:
                self._parse_permission(p)
            except Exception as ex:
                ex.message = "%s" % ex.message
                raise

    def remove(self, role, resource=None, action=None):
        """移除权限

        :param role: 角色
        :param resource: 资源
        :param action: 操作

        - 当 ``role!=None, resource==None`` , 删除 role
        - 当 ``role!=None, resource!=None,action==None`` , 删除 resource
        - 当 ``role, resource, action`` 不存在时不进行操作也不抛 Exception
        """
        if role in self.permission:
            r = self.permission[role]
            if resource is None:
                del self.permission[role]
            elif resource in r:
                if action is None:
                    del r[resource]
                elif action in r[resource]:
                    r[resource].remove(action)

    def __repr__(self):
        return repr(self.permission)

    def __str__(self):
        return str(self.permission)

if __name__ == '__main__':
    pdict = {
        "user.admin": {
            "*": []
        },
        "user.super": {
            "bloguser*": [],
            "userinfo*": [],
        },
        "user.normal": {
            "comment": ["post", "post_by3", "put"],
            "user": ["get_me", "delete", "put_password"],
            "userinfo": ["get_me", "put"],
        },
        "monkey.king": {
            "monkey*": [],
            "fruit*": [],
        }
    }
    p = Permission(pdict=pdict)
    from pprint import pprint as pp
    pp(p.resource_user)
