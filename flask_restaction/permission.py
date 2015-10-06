# coding:utf-8

from __future__ import unicode_literals
from os.path import isfile
import json
import re
import copy
from . import pattern_action
pattern_name = re.compile(ur"[A-Za-z]\w*", re.I)


def validate(obj):
    """验证 permission 数据格式是否正确

    :param obj: 从 json 文件读取进来的dict对象
    """
    assert isinstance(obj, dict), \
        "invalid obj, obj must be a dict: '%s'" % obj
    for role, perm in obj.items():
        assert role == "*" or pattern_name.match(role),\
            "invalid role: '%s'" % role
        assert isinstance(perm, dict), \
            "invalid permission, permission must be a dict: '%s'" % perm
        for res, actions in perm.items():
            if res == "*":
                assert len(perm) == 1, \
                    "invalid resource, '*' resource must be the only resource"
                assert actions == [], \
                    "invalid resource, '*' resource's actions must be []: "
            elif res[-1:] == "*":
                assert pattern_name.match(res[:-1]),\
                    "invalid resource: '%s'" % res
                assert actions == [], \
                    "invalid resource, actions must be []: '%s'" % res
            else:
                assert pattern_name.match(res), \
                    "invalid resource: '%s'" % res
                assert isinstance(
                    actions, list), \
                    "invalid actions, actions must be a list: '%s'" % actions
                for act in actions:
                    assert pattern_action.match(act), \
                        "invalid action: '%s'" % act


class Permission(object):

    """Permission 权限分配表

    :param filepath: permission 文件路径
    :param jsonstr: json 字符串
    """

    def __init__(self, filepath=None, jsonstr=None):
        if filepath is not None:
            if isfile(filepath):
                with open(filepath) as f:
                    jsonstr = f.read()
            else:
                raise ValueError("%s is not file" % filepath)

        if jsonstr is not None:
            self.permission = json.loads(jsonstr)
            validate(self.permission)
        else:
            self.permission = {}

    def permit(self, role, resource, action):
        """判断角色是否有对应的权限

        :param role: 角色
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

            permission.add("admin", "*")
            permission.add("poster", "photo*")
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
                validate(p)
                self.permission = p
            except Exception as ex:
                raise ValueError(ex.message)

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
