.. _quickstart:

快速上手
========

一个最小的应用
-------------------

.. code-block:: python
    
    from flask import Flask
    from flask_restaction import Resource, Api, Gen

    app = Flask(__name__)
    api = Api(app)

    class Hello(Resource):
        """hello world"""
        schema_inputs = {
            "get": {
                "name": ("safestr&default='world'", "your name")
            }
        }
        schema_outputs = {
            "get": {"hello": "unicode&required"}
        }

        def get(self, name):
            """welcome to flask-restaction"""
            return {"hello": name}

    api.add_resource(Hello)

    gen = Gen(api)
    gen.resjs('static/res.js')
    gen.resdocs('static/resdocs.html', resjs='/static/res.js',
                bootstrap='/static/bootstrap.min.css')

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

访问 http://127.0.0.1:5000/static/resdocs.html 可以查看自动生成的文档

那么，这些代码是什么意思呢？

1. 首先导入 Resource 和 Api 类
2. 创建一个 Api 对象，把 app 作为参数
3. 创建一个 Hello 类，继承自 Resource 类并定义 get 方法
4. 定义 schema_inputs，它指定了输入参数及格式
5. 调用 api.add_resource(Hello) ，把 Hello 添加到 api 资源中
6. 生成 res.js 和 resdocs.html(需要将bootstrap.min.css放到static目录里面)


.. glossary:: 两个概念
    *resource*
        资源，比如这里的 Hello 类
    
    *action* 
        操作，例如 get, post, delete, get_list, post_login。
        只要是 HTTP 方法或 HTTP 方法加下划线 _ 开头就行


校验输入输出
-------------------

Resource 类使用 *schema_inputs*, *schema_outputs*, *output_types* 来指定如何验证输入输出。

*schema_inputs*
    输入格式，action 作为 key, schema 作为 value

*schema_outputs*
    输出格式，同 schema_inputs

*output_types* ，
    输出类型，是一个 list，里面的元素是你要返回的自定义类型对象的类型，
    这样返回的对象会被包装成一个 dict

关于 validater, 请移步 `validater <https://github.com/guyskk/validater>`_


使用 res.js
-----------

使用 res.js 可以方便的调用 api ，使用其他的 js 方式调用也是完全可以的。

示例:

.. code-block:: javascript
    
    #引用 res.js 文件
    <script type="text/javascript" src="/static/res.js"></script>

    #调用 api
    var name = document.getElementById("name").value;
    res.hello.get({
        name: name
    }).then(function(value) {
        document.getElementById("message").innerText = 'Hello ' + value.hello;
    }).catch(function(err) {
        console.log(err);
    });


详细用法见 :ref:`resjs`


构建 URL
---------------------------

可以使用 flask 中的 url_for() 函数构建指定 action 的 URL。

endpoint (url_for 的参数) 是 ``resource@action_lastpart``
    
*resource*
    resource name or resource's class name, lowcase

*action_lastpart*
    action's last part name, lowcase

格式::

    url_for("resource@lastpart") -> /resource/lastpart

示例::
    
    url_for("hello") -> /hello
    url_for("hello@list") -> /hello/list
    url_for("hello@login") -> /hello/login


身份验证&权限控制
-------------------

flask_restaction 使用 *json web token* 作为身份验证工具。

see `https://github.com/jpadilla/pyjwt <https://github.com/jpadilla/pyjwt>`_


.. glossary:: 两个概念
    *user_role*
        用户角色，这是随时可以变动，可以通过UI界面编辑设定的，对应的配置文件为 permission.json

    *res_role*
        资源角色，这是与程序逻辑密切相关，由程序设计者确定的，对应的配置文件为 resource.json


默认情况下，permission.json 和 resource.json 放在应用的根目录下。
框架会在程序初始化的时候解析 permission.json 和 resource.json，
请求到来时，根据请求的 resource, action 和 user_role，可以快速确定 res_role 以及是否许可此次请求。
如果不许可此次请求，返回 403 状态码。


**fn_user_role 函数**

框架不知道用户是什么角色, 所以需要你提供一个能返回用户角色的函数

.. code-block:: python
    
    from flask_restaction import Auth

    def fn_user_role(token):
        if token and 'id' in token:
            user_id = token[id]
            # query user from database
            return user_role
        else:
            return None

    auth = Auth(api, fn_user_role=fn_user_role)

**auth.gen_header(token)**

为了能够确认用户的身份，你需要在用户登录成功后生成一个令牌(auth token)，
将令牌通过响应头(``Authorization``)返回给用户。令牌一般会储存用户ID和过期时间，
用户在发送请求时需要将令牌通过请求头发送给服务器。

.. code-block:: python

    def post_login(self, username, password):
        """登录"""
        # query user from database
        header = auth.gen_header({"id": user.id})
        return user, header

.. Note:: 注意

    令牌会用密钥进行签名，无法篡改。
    你需要设置一个密钥，可以通过 Auth 的参数 auth_secret 或者 flask 配置 API_AUTH_SECRET。
    令牌是未加密的，不要把敏感信息保存在里面。

res.js 会自动将令牌添加到请求头中，并且当收到响应时，会自动将响应头中的令牌保存到浏览器 localstroge 中。


**permission.json 结构**

.. code::

    {
        "user_role": {
            "resource": "res_role",
            ...
        },
        ...
    }


**resource.json 结构**
    
.. code::

    {
        "resource": {
            "res_role": ["action", ...],
            ...
        },
        ...
    }


**为何这样设计？**

在 RESTful 架构中，应用（网站）由一系列的资源（resource）组成，每个资源包含一系列操作（action）。
每个资源都是一个独立的组件，这些资源和它们包含的操作一起组成 API 供客户端调用，用户界面以及交互逻辑完全由客户端完成。资源之间需要保持独立，避免修改或添加新资源时产生相互影响，因此把角色分为用户角色（user_role） 和 资源角色（res_role）。用户角色是整个 API 范围的，资源角色只在 resource 内起作用，同时用户角色本身也是 resource，客户端可以通过 API 对它操作，但资源角色是固定的。


将用户角色本身做为 resource 

.. code::
    
    from flask_restaction import Permission
    api.add_resource(Permission, auth=auth)


全局数据
----------------------------

*flask.g.resource*
    请求的资源

*flask.g.action*
    请求的操作

*flask.g.request_data*
    请求数据

*flask.g.user_role*
    用户角色

*flask.g.res_role*
    资源角色
    
*flask.g.token*
    请求令牌

ApiInfo与自动生成工具
-----------------------------

万物皆资源

API本身也是资源，其威力可比编程语言中的反射/自省。

.. code-block:: python

    from flask_restaction import ApiInfo

    api.add_resource(ApiInfo, api=api)


将API本身暴露给前端，可以用来生成文档，res.js，甚至是res.java，
换句话说，这是用代码生成代码的武器。

目前能自动生成文档，res.js和权限管理页面，用法见 :class:`~flask_restaction.Gen`


使用蓝图
-----------------------------

通过 Api 的 blueprint 参数设置 blueprint，这样所有的 Resource 都会路由到 blueprint 中。

.. code-block:: python

    from flask import Flask, Blueprint
    from flask_restaction import Api

    app = Flask(__name__)
    bp_api = Blueprint('api', __name__, static_folder='static')
    api = Api(app, blueprint=bp_api)


配置
-----------------------------


配置项:

.. list-table:: 
  :widths: 20 20 30
  :header-rows: 1

  * - 名称
    - 默认值
    - 说明
  * - API_RESOURCE_JSON
    - resource.json
    - resource.json文件的路径
  * - API_PERMISSION_JSON
    - permission.json
    - permission.json文件的路径
  * - API_AUTH_HEADER
    - Authorization
    - 身份验证请求头
  * - API_AUTH_SECRET
    - SECRET
    - 用于加密身份验证token的密钥
  * - API_AUTH_ALG
    - HS256
    - 用于加密身份验证token的算法
  * - API_AUTH_EXP
    - 3600
    - 身份验证token的过期时间，单位是秒
  * - API_DOCS
    - 
    - docs of api

你也可以在 api 初始化的时候传递参数，这些参数也会被当作配置，并且会覆盖 app.config 中的配置。
see :class:`~flask_restaction.Api`


对比其它框架
--------------------

**flask-restful**
~~~~~~~~~~~~~~~~~~~~

flask-restaction 相对于 flask-restful 有什么优势，或是什么特性?

- restaction 更灵活。

    restful 的方法只能是 http method，就是 get, post, put, delete 那几个，而 restaction 的方法除了 http method，还可以是任何以 http method 加下划线开头的方法。

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


**2016年1月20日 - 今**

重写 validater，增强灵活性，去除一些混乱的语法

重构 Api
    - 将权限从 Api 里面分离
    - 将自动生成工具从 Api 里面分离，优化 res.js
    - 去除测试工具，因为 flask 1.0 内置测试工具可以取代这个
    - 将 testing.py 改造成 res.py，用于调用 API，功能类似于 res.js