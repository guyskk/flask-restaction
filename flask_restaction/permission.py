# coding:utf-8

import os
from os.path import isfile
import json
import re
import copy
from . import pattern_action
pattern_name = re.compile(ur"[A-Za-z]\w*", re.I)


def validate(obj):
    """验证permission数据格式是否正确"""
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

        权限按role->resource->actions划分
        JSON 文件格式
        {
            "role/*": {
                "*/resource*": ["get", "post"],
                "resource": ["action", ...]
            },
            ...
        }
        role为'*'时，表示匿名用户的权限。
        resource为'*'时，表示拥有所有resource的所有action权限，
            此时actions必须为'[]'且不能有其他resource。
        resource为'resource*'时，表示拥有此resource的所有action权限，此时actions必须为'[]'。
        role和resource（除去'*'号）只能是字母数字下划线组合，且不能以数字开头。
    """

    def __init__(self, filepath=None, jsonstr=None):
        """
        filepath 文件（json格式）路径
        jsonstr json字符串
        """
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
        """
        判断角色是否有对应的权限
        """
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
        """
        将权限分配表导出为json格式字符串
        """
        return json.dumps(self.permission, indent=4)

    def dump(self, filepath):
        """
        将权限分配表用json格式保存到文件
        """
        with open(filepath, "w") as f:
            f.write(self.dumps())

    def add(self, role, resource, action):
        """
        给角色添加权限，可以使用'*'符号
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
        """
        移除权限
        role!=None, resource==None, 删除role
        role!=None, resource!=None,action==None, 删除resource
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
