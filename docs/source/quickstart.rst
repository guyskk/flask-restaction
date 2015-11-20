.. _quickstart:

快速上手
========

一个最小的应用
-------------------

.. code-block:: python

    from flask import Flask
    from flask.ext.restaction import Resource, Api, schema

    app = Flask(__name__)
    api = Api(app)



    class Hello(Resource):
        """docstrings Hello"""
        name = "safestr&required", "world", "you name"
        schema_inputs = {
            "get": schema("name")
        }

        def get(self, name):
            """docstrings get"""
            return {"hello": name}

    api.add_resource(Hello)
    api.gen_resjs()
    api.gen_resdocs()
    
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

那么，这些代码是什么意思呢？

1. 首先导入了 :class:`~flask_restaction.Resource` 和 :class:`~flask_restaction.Api` 类
2. 创建了一个 Api 类的实例，把 Flask 类的一个实例作为参数
3. 创建了一个 Hello 类，继承自 Resource 类
4. 定义 schema_inputs，它指定了输入参数及格式
5. 调用 api.add_resource(Hello) ，把 Hello 添加到 api 资源中
6. 生成 res.js 和 resdocs.html 文件, Visit http://127.0.0.1:5000/static/resdocs.html


校验输入输出
-------------------

从 v0.18.0 开始，flask_restaction 使用 tuple_like schema，它可以少写2/3的 schema 代码。

tuple_like schema::

    name = "safestr&required", "world", "you name"

等价于::

    {
        "desc": "you name",
        "required": True,
        "validate": "safestr",
        "default": "world"
    }


*desc*
    描述
*required*
    是否是必需的，输入的空字符串和None视作缺少

*validate*
    指定校验器，比如：int,str,url,email

*default*
     指定默认值，也可以是一个函数，比如：datetime.now

Resource 类使用 *schema_inputs*, *schema_outputs*, *output_types* 来指定如何验证输入输出。
*output_types* 是一个 list，里面的元素是你要返回的自定义类型对象的类型，
这样返回的对象会被包装成一个 dict。

你可以把 schema 分成几个小零件 ，然后用 schema 函数将它们组合。

.. code-block:: python
    
    from flask.ext.restaction import schema

    class Hello(Resource):

        name = "name&required", "world", "name"
        date = "datetime&required"
        hello = "str&required", None, "hello"

        schema_inputs = {
            "get": schema("name"),
            "post_login": schema("name", "date"),
        }
        schema_outputs = {
            "get": schema("hello"),
            "post_login": schema("hello", "date")
        }

        # if you return a custom type object
        # output_types = [custom_type]

        def get(self, name):
            return {"hello": name}

        def post_login(self, name, date):
            return {
                "hello": name,
                "date":date,
            }


schema 函数用于将 schema 组合，生成一个新的 schema。运行一下下面的代码你就明白了。

.. code-block:: python

    from flask.ext.restaction import schema
    import json

    leaf1 = "+int&required", 1, "leaf1 desc"
    leaf2 = "unicode&required"
    leaf3 = "unicode", None, "article table of content"

    branch1 = schema("leaf1", "leaf2")
    branch2 = schema("branch1", "leaf3")

    flower = schema(["branch1"])
    tree = schema(["branch2"])

    forest1 = schema(["tree"])
    forest2 = schema([["branch2"]])
    park = schema("tree", "flower")

    scope = locals()

    def pp(obj):
        print json.dumps(obj, ensure_ascii=False, indent=4)

    pp(branch1(scope))
    pp(branch2(scope))

    pp(flower(scope))
    pp(tree(scope))

    pp(forest1(scope))
    pp(forest2(scope))
    pp(park(scope))


建议你看一下内置的 validater 
`built-in validater <https://github.com/guyskk/validater#schema-format>`_

想要了解更多，请移步 `validater <https://github.com/guyskk/validater>`_


使用 res.js
-----------

使用 res.js 可以方便的调用 api ，使用其他的 js 方式调用也是完全可以的。

使用方式:

.. code-block:: javascript
    
    #引用 res.js 文件
    <script type="text/javascript" src="/static/res.js"></script>

    #调用 api
    res.hello.get(data, function(err, value) {
        if (!err){
            document.getElementById("message").innerText = value.hello;
        }else{
            alert(err)
        }
    });


调用 api 的语法为::

    res.resource.action(data, function(err, value), function(progress))

*resource*
    资源的名称，例如 ``hello``。

*action* 
    执行的操作，例如 get, post, delete, get_list, post_upload。只要是 httpmethod 或 httpmethod 加下划线 _ 开头就行。

*function(err, value)*
    请求完成回调函数。

*function(progress)*
    上传文件进度的回调函数。

*data*
    请求数据

    - 当 data 是 formdata: 表示上传文件, method 必须是 POST。

    - 当 data 是 string: 表示 input 控件 id, 会从其中获取要上传的文件, method 必须是 POST。

    - 其余情况下 data 是普通 js 对象


现在来写一个 hello.html 并保存到 static 目录

.. code-block:: html

    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>hello res.js</title>
        <script type="text/javascript" src="/static/res.js"></script>
        <script type="text/javascript">
        function send() {
            var name = document.getElementById("name").value;
            res.hello.get({name: name}, function(err, value) {
                if (!err){
                    document.getElementById("message").innerText = value.hello;
                }else{
                    alert(err)
                }
            });
        }
        </script>
    </head>
    <body>
        <input id="name" type="text" placeholder="you name">
        <p id="message"></p>
        <button onclick="send()">GetHello</button>
    </body>
    </html>

打开浏览器，访问 http://127.0.0.1:5000/static/hello.html

尝试一下，注意 schema_inputs 中的 ``"validate": "safestr"``

你如果输入一些不安全的字符（黑客攻击），例如::

    <script type="text/javascript">alert("haha")</script>

你输入的字符串会被转义成如下内容::

    &lt;script type=&#34;text/javascript&#34;&gt;alert(&#34;haha&#34;)&lt;/script&gt;


构建 URL
---------------------------

可以使用 flask 中的 url_for() 函数构建指定 action 的 URL。

endpoint 名称是resource@action_lastpart::
    
    resource -> resource name or resource's class name, lowcase
    action   -> action's last part name, lowcase

格式::

    Resource.action_lastpart -> url_for("resource@lastpart") -> /resource/lastpart

For example::
    
    Hello.get -> url_for("hello") -> /hello
    # 假设 Hello.get_list 存在
    Hello.get_list -> url_for("hello@list") -> /hello/list
    Hello.post_login -> url_for("hello@login") -> /hello/login


Py2&py3
---------

Flask-restaction 从 v0.17.0 开始支持 py3，在 py27 和 py34 上测试通过。
但是还需要更多测试来使它更稳定。同时，你要使用最新版的 flask 。

如果你使用 py2 ，最好将下面几句加到每个模块的开头。这样在你以后迁移到 py3 的时候会容易的多。

.. code-block:: python

    # coding:utf-8

    from __future__ import unicode_literals
    from __future__ import absolute_import




身份验证
-------------------

flask_restaction 使用 *json web token* 作为身份验证工具。

see `https://github.com/jpadilla/pyjwt <https://github.com/jpadilla/pyjwt>`_

**你需要把自己的 auth_secret 添加到 api 中**，默认值是 ``"SECRET"``。

你可以通过 ``flask.g.me`` 获取用户的身份信息，它的结构如下:

.. code::

    {
        "id":user_id, 
        "role":user_role
    }

此外，你需要在用户登录成功后返回 auth 响应头(default ``Authorization``) 到响应中，它的值可以通过 ``api.gen_token(me)`` or ``api.gen_auth_token(me)`` 生成。

**fn_user_role 函数**

Flask-Restaction 不知道用户是什么角色, 所有需要你提供一个能返回用户角色的函数

.. code-block:: python

    def user_role(uid, user):
        # user is the user in permission.json
        # you may need query user from database
        return "user.admin"

    api = Api(app, fn_user_role=user_role)

如果 ``g.me["id"] is None``，那么不会调用 fn_user_role。

fn_user_role 的返回值会保存在 ``g.me["role"]`` 中，权限系统需要用到它。

**为何这样设计？**

一个应用（网站）通常会划分成几个领域。一个用户在不同的领域会担任不同的角色，但是在一个领域只应当承担一个角色。一个领域由一些 Resource(用户本身也是 Resource)组成，这样划分可以可以避免在添加新领域，新功能的时候影响原有的用户和权限系统。

在 permission.json 中，用 user.role 表示领域以及领域中的角色。

.. code::

    - user
        - resource1
        - resource2
        - ...
        - module1_user
            - module1_resource
            - ...
        - module2_user
            - module2_resource
            - ...


res.js 会自动添加 auth 请求头 (``Authorization``) 到请求中。
并且当收到 auth 响应头时，会自动将 auth token 保存到浏览器 localstroge 中。


权限控制
------------------------------

默认情况下，permission.json 应当文件放在应用的根目录下，你也可以改成放到其他位置。

权限按 用户.角色 -> 资源 -> 操作 划分


JSON struct

.. code::

    {
        "user.role/*": {
            "*/resource*": ["get", "post"],
            "resource": ["action", ...]
        },
        ...
    }

当 role 为 ``*`` 时
    表示匿名用户的权限。

当 resource 为 ``*`` 时
    表示该角色可以操作所有 resource 的所有 action ， 此时 actions 必须是 ``[]`` 并且不能有其他 resource。

当 resource 为 ``resource*`` 时
    表示该角色可以操作该 resource 的所有 action ， 此时 actions 必须是 ``[]``。

user.role
    必须是 user.role 这种格式，中间是一个点号， 并且只能由字母数字和下划线组成，并且以字母开头。

resource
    只能由小写字母数字和下划线组成，并且以小写字母开头。


使用蓝图
-----------------------------

.. code-block:: python

    from flask import Flask, Blueprint
    from flask.ext.restaction import Api
    from .article import Article

    app = Flask(__name__)

    #1
    bp_api = Blueprint('api', __name__, static_folder='static')
    api = Api(bp_api)

    #2
    api.add_resource(Article)

    #3
    app.register_blueprint(bp_api, url_prefix='/api')

    #4
    api.gen_resjs()
    api.gen_resdocs()


如果你需要 gen_resjs 或 gen_resdocs ，你应当添加 ``static_folder='something'`` 到 Blueprint 中，因为生成的 res.js 和 resdocs.html 都要保存到 Blueprint 的 static 目录中。

你必须按 #1, #2, #3, #4 的顺序组织代码，否则会造成错误。因为 Resource urls 在 register_blueprint 时绑定，permission 在 register_blueprint 之后初始化。


配置
-----------------------------

你可以把配置加载到 app.config （从配置文件中或其他方式），当 api 初始化接收参数是 app 而不是 blueprint 的时候它会从 app.config 从加载配置。

如果 api 接收参数是 blueprint ，你可以使用 :meth:`~flask_restaction.Api.config` 并传递 ``app.config`` 给它。

配置项:

.. list-table:: 
  :widths: 20 20 30
  :header-rows: 1

  * - 名称
    - 默认值
    - 说明
  * - API_PERMISSION_PATH
    - permission.json
    - 权限配置文件的路径
  * - API_PERMISSION_PATH
    - permission.json
    - 权限配置文件的路径
  * - API_AUTH_HEADER
    - Authorization
    - 身份验证请求头
  * - API_AUTH_TOKEN_NAME
    - res_token
    - 身份验证token保存在localstorage中的名称
  * - API_AUTH_SECRET
    - SECRET
    - 用于加密身份验证token的密钥
  * - API_AUTH_ALG
    - HS256
    - 用于加密身份验证token的算法
  * - API_AUTH_EXP
    - 1200
    - 身份验证token的过期时间，单位是秒
  * - API_RESJS_NAME
    - res.js
    - res.js文件名
  * - API_RESDOCS_NAME
    - resdocs.html
    - resdocs.html文件名
  * - API_BOOTSTRAP
    - ``http://apps.bdimg.com/libs/
      bootstrap/3.3.4/css/bootstrap.css``
    - 用于resdocs.html中
  * - API_DOCS
    - 
    - docs of api

你也可以在 api 初始化的时候传递参数，这些参数也会被当作配置，并且会覆盖 app.config 中的配置。
see :class:`~flask_restaction.Api`


测试
------------------------

For example:

.. code-block:: python

    with api.test_client() as c:
        rv,code,header = c.resource.action(data)
        assert code == 200
        assert rv == {"hello":"world"}
        assert c.resource.action_need_login(data).code == 403

    with api.test_client(user_id) as c:
        assert c.resource.action_need_login(data).code == 200
        assert c.resource.action_need_login(data).rv == {"hello":"guyskk"}

**Note**

测试中可以访问 flask.g 但是不能访问 flask.request ,因为只有应用环境而没有请求环境。
c.resource.action(data) 的返回值是 namedtuple("ResponseTuple", "rv code header"),
其中 rv 是一个 dict。

如果 flask 的完整请求的流程是::

    1. 创建请求环境 应用环境
    2. 解析请求 获取请求数据 
    3. 校验请求数据 调用相应的action 校验返回值
    4. 将返回值转化成响应

那么 1 是 flask 处理的， 2,4 是由 api 处理的，3 是 resource 中处理的。
第 2 步会将解析结果保存到 g.resource g.action g.me 中，这样在 resource 中就能使用解析结果。

测试的时候先创建应用环境，伪造 2，执行 3，直接返回 3 的结果而不执行4。


请求处理流程
-----------------------------

.. image:: _static/flask-restaction.svg


kkblog 介绍
-----------------------------

KkBloG 是一套基于 Python 的多人博客系统，你可以用 markdown 格式写文章，保存到 github ，然后就可以在上面展示自己的博客，别人还可以评论你的文章。

这个项目是对flask-restaction框架的一次尝试。

see `https://github.com/guyskk/kkblog <https://github.com/guyskk/kkblog>`_
