.. _quickstart:

快速上手
========

一个最小的应用
-------------------

.. code-block:: python
    
    from flask import Flask
    from flask_restaction import Api

    app = Flask(__name__)
    api = Api(app)

    class Hello:
        """Hello world"""

        def get(self, name):
            """Get welcome message

            $input:
                name?str&escape&default="world": Your name
            $output:
                message?str&maxlen=60: Welcome message
            """
            return {
                "message": "Hello %s, Welcome to flask-restaction!" % name
            }

    api.add_resource(Hello)

    if __name__ == '__main__':
        app.run(debug=True)

保存为 ``hello.py``, 然后运行：

.. code::

    $ python hello.py
     * Running on http://127.0.0.1:5000/
     * Restarting with reloader

打开浏览器，访问 http://127.0.0.1:5000/hello

.. code::

    {
      "hello": "world"
    }

再访问 http://127.0.0.1:5000/hello?name=kk

你将会看到 

.. code::

    {
      "hello": "kk"
    }

访问 http://127.0.0.1:5000 可以查看自动生成的文档(JSON格式)，
此文档为API全部接口信息，建议用 Chrome 安装 `WEB前端助手 <https://www.baidufe.com/fehelper>`_ 查看。

那么，这些代码是什么意思呢？

1. 创建一个 Api 对象，把 app 作为参数
2. 创建一个 Hello 类，定义 get 方法
3. 在 get 方法文档字符串中描述输入参数和输出的格式
4. 调用 api.add_resource(Hello)

.. glossary:: 两个概念
    *resource*
        资源，比如这里的 Hello 类
    
    *action* 
        操作，例如 get, post, delete, get_list, post_login。
        只要是 HTTP 方法或 HTTP 方法加下划线 _ 开头就行


校验输入输出
-------------------

在Resource的文档字符串中用 *$shared* 描述共享的Schema。
在Action的文档字符串中用 *$input*, *$output* 描述输入输出Schema, 用 *$error* 描述可能返回的错误。

*$input*
    YAML格式(`YAML 简介 <http://www.mutouxiaogui.cn/blog/?p=357>`_)的字符串，
    Schema语法见 `Validater <https://github.com/guyskk/validater>`_ 。
    实际数据来源取决于HTTP方法，GET和DELETE请求，取自url参数，
    POST和PUT请求，取自请求体，Content-Type为 ``application/json``。

*$output*
    输出格式，同$input。

*$error*
    可能返回的错误，例如::

        $error:
            InvalidData: 输入参数错误
            PermissionDeny: 权限不足

关于 Validater, 请移步 `Validater <https://github.com/guyskk/validater>`_

**自定义 validater**

在 Validater 的文档中讲述了自定义 validater 的用法。所有自定义的 validater 通过
Api(validaters=validaters) 进行注册。


使用 res.js
-----------

用框架提供的命令行工具生成 res.js 和 res.min.js::

    resjs url dest

例如::

    resjs http://127.0.0.1:5000 static

会将生成的文件保存在 static 目录中。

用res.js调用API非常简单，回调是Promise风格的。

res.js用法::

    res.resource.action({
        ...some data
    }).then(function(value) {
        ...
    }).catch(function(error) {
        ...
    })

例如调用Hello的API::

    res.hello.get({name:"kk"})


详细用法见 :ref:`resjs`


使用 res.py
---------------------------

res.py 的用法类似于 res.js，网络请求用的是requests库。

.. code-block:: python

    from flask_restaction import Res
    res = Res("http://127.0.0.1:5000")
    data = {'username':'admin', 'password':'123456'}
    resp = res.user.post_login(data)
    # resp是requests.Response对象
    assert resp.status_code == 200
    user = resp.json()


构建 URL
---------------------------

可以使用 flask 中的 url_for() 函数构建指定 action 的 URL。

endpoint (url_for 的参数) 是 ``resource@action_name``
    
*resource*
    Resource类名称的小写

*action_name*
    Action的后半部分(下划线分隔)

格式::

    url_for("resource@lastpart") -> /resource/lastpart

示例::
    
    url_for("hello") -> /hello
    url_for("hello@login") -> /hello/login


身份验证&权限控制
-------------------

flask_restaction 使用 *json web token* 作为身份验证工具。

see `https://github.com/jpadilla/pyjwt <https://github.com/jpadilla/pyjwt>`_

metafile是一个描述API信息的文件，通常放在应用的根目录下，文件名 meta.json。
在Api初始化的时候通过 Api(metafile="meta.json") 加载。

在 metafile 中设定角色和权限：
    
    {
        "$roles": {
            "Role": {
                "Resource": ["Action", ...]
            }
        }
    }

**get_role 函数**

框架不知道用户是什么角色, 所以需要你提供一个能返回用户角色的函数

.. code-block:: python
    
    @api.get_role
    def get_role(token):
        if token and 'id' in token:
            user_id = token[id]
            # query user from database
            return user_role
        else:
            return "Guest"

请求到来时，根据 Role, Resource, Action 可以快速确定是否许可此次请求
(通过判断Action是否在meta["$roles"][Resource]中)。 如果不许可此次请求，返回 403 状态码。

**api.gen_header(token)**

为了能够确认用户的身份，你需要在用户登录成功后生成一个令牌(auth token)，
将令牌通过响应头(``Authorization``)返回给用户。令牌一般会储存用户ID和过期时间，
用户在发送请求时需要将令牌通过请求头发送给服务器。

.. code-block:: python

    def post_login(self, username, password):
        """登录"""
        # query user from database
        headers = api.gen_header({"id": user.id})
        return user, headers

.. Note:: 

    令牌会用密钥进行签名，无法篡改。
    你需要设置一个密钥，可以通过 Auth 的参数 auth_secret 或者 flask 配置 API_AUTH_SECRET。
    令牌是未加密的，不要把敏感信息保存在里面。

res.js 会自动将令牌添加到请求头中，并且当收到响应时，会自动将响应头中的令牌保存到浏览器 localstroge 中。


使用蓝图
-----------------------------

Api可以放在蓝图中，这样所有的 Resource 都会路由到蓝图中。

.. code-block:: python

    from flask import Flask, Blueprint
    from flask_restaction import Api

    app = Flask(__name__)
    bp = Blueprint('api', __name__)
    api = Api(bp)


配置
-----------------------------

框架会使用 Flask.secret_key 对 token 进行加密。


对比其它框架
--------------------

**flask-restful**
~~~~~~~~~~~~~~~~~~~~

flask-restaction 相对于 flask-restful 有什么优势，或是什么特性?

- restaction 更灵活。

    restful 的方法只能是 http method，就是 get, post, put, delete 那几个，而
    restaction 的方法除了 http method，还可以是任何以 http method 加下划线开头的方法。

- 输入输出校验

    restaction 是声明式的，简单明确::
        
        from flask_restaction import reqparse

        name = "safestr&required&default='world'", "your name"
        schema_inputs = {
            "get": {"name": name}
        }

    在 reslful 中叫做 Request Parsing::

        from flask_restful import reqparse

        parser = reqparse.RequestParser()
        parser.add_argument('rate', type=int, help='Rate cannot be converted')
        parser.add_argument('name')
        args = parser.parse_args()

    Request Parsing 很繁琐，并且不能很好的重用代码。

    restaction 的输出校验和输入校验差不多，不同的是可以校验自定义的 python 对象。
    https://github.com/guyskk/validater#proxydict-validate-custome-type

    而 reslful 校验输出更加繁琐！

- 身份验证及权限控制
    
    restaction 提供一个灵活的权限系统，身份验证基于 jwt(json web token)，
    权限验证是通过json配置文件，而不是散布在代码中的装饰器(decorator)，
    并且角色本身也是 resource，客户端可以通过 API 进行操作。

- 自动生成文档，res.js和权限管理页面

    用 res.js 可以方便的调用 api，还可以直接上传文件。


历程
-----------------------------

**2015年9月4日 - 2015年12月**

项目开始

将validater作为一个独立项目

自动生成文档和res.js

添加身份验证和权限控制

重写身份验证和权限控制，之前的用起来太繁琐


**2016年1月20日 - 2月24日**

重写 validater，增强灵活性，去除一些混乱的语法

重构 Api
    - 将权限从 Api 里面分离
    - 将自动生成工具从 Api 里面分离，优化 res.js
    - 去除测试工具，因为 flask 1.0 内置测试工具可以取代这个
    - 将 testing.py 改造成 res.py，用于调用 API，功能类似于 res.js

**2016年3月 - 5月**

内部项目使用 flask-restaction 框架，项目已内测。
期间修复一些bug，做了小的改进和优化，Api基本未变。

**2016年5月 - 5月12日**

完善 res.js，对代码进行了重构和测试，支持模块化和标准 Promise。

