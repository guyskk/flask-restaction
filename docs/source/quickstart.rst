.. _quickstart:

快速上手
========

一个最小的应用
-------------------

A minimal Flask-Restaction API:

.. code-block :: python

    from flask import Flask
    from flask_restaction import Resource, Api

    app = Flask(__name__)
    api = Api(app)


    class Hello(Resource):
        schema_inputs = {
            "get": {
                "name": {
                    "desc": "you name",
                    "required": True,
                    "validate": "safestr",
                    "default": "world"
                }
            }
        }

        def get(self, name):
            return {"hello": name}

    api.add_resource(Hello)
    api.gen_resjs()
    api.gen_resdocs()
    
    if __name__ == '__main__':
        app.run(debug=True)

save this as ``hello.py``, then run it: 

.. code ::

    $ python hello.py
     * Running on http://127.0.0.1:5000/
     * Restarting with reloader

then open browser, visit ``http://127.0.0.1:5000/hello``
you will see: 

.. code ::

    {
      "hello": "world"
    }

if you visit ``http://127.0.0.1:5000/hello?name=kk``
you will see: 

.. code ::

    {
      "hello": "kk"
    }


Use url_for
-----------
    
The endpoint is ``resource@action``::
    
    resource -> Resource class name, lowcase
    action   -> action's last part name, lowcase

For Example::
    
    Hello.get -> url_for("hello") -> /hello
    # suppose Hello.get_list exists
    Hello.get_list -> url_for("hello@list") -> /hello/list
    Hello.post_login -> url_for("hello@login") -> /hello/login
    
Use res.js
-----------

Let's write test.html and save it in static folder

.. code-block :: html

    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>test res.js</title>
        <script type="text/javascript" src="/static/res.js"></script>
        <script type="text/javascript">
        function send() {
            var name = document.getElementById("name").value;
            if (name && name != "") {
                var data = {
                    name: name
                };
            }
            res.hello.get(data, function(err, value) {
                msg = JSON.stringify(err || value)
                document.getElementById("message").innerText = msg;
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

then open browser, visit ``http://127.0.0.1:5000/static/test.html``

have a try, and notice schema_inputs's ``"validate": "safestr"``

if you input some unsafe strings, such as: 

``<script type="text/javascript">alert("haha")</script>``

then you inputs will be escape to avoid attack:

``{"hello":"&lt;script type=&#34;text/javascript&#34;&gt;alert(&#34;haha&#34;)&lt;/script&gt;"}``

**look at this:**

.. code-block :: javascript

    res.hello.get(data, function(err, value) {
        msg = JSON.stringify(err || value)
        document.getElementById("message").innerText = msg;
    });


You can use ``res.resource.action(data, function(err, value))`` to access resources provided by rest api.

- ``resource`` is resource's name(is not always resource's classname, depends on add_resource), such as ``hello``

- ``action`` is ... such as ``get`` , ``post`` ... 
  not only http method, ``get_list`` , ``post_upload`` is ok

- If you use blueprint, then You should use``res.blueprint.resource.action`` to access resources

Py2&py3
---------

Flask-restaction support py3 since v0.17.0, tested on py27 and py34.
and more tests is required to make it more stable.

Also, you should use the latest version of flask.

You'd better put statements below to the head of all modules if you use py2. It will reduce you work of transfer to py3.

.. code-block:: python

    # coding:utf-8

    from __future__ import unicode_literals
    from __future__ import absolute_import


Validater
---------

Resource class use ``schema_inputs``, ``schema_outputs``, ``output_types`` to validate inputs and outputs.

The ``output_types`` is a list of class that you want to return, then the return value will be proxy as a dict.

You can split schema dict into some tuples and combine them into ``schema_inputs`` and ``schema_outputs``.


For example:

.. code-block:: python

    class Hello(Resource):
        schema_name = ("name", {
            "desc": "name",
            "required": True,
            "validate": "name",
            "default": "world"
        })
        schema_date = ("date", {
            "desc": "date",
            "required": True,
            "validate": "datetime",
        })
        schema_hello = ("hello", {
            "desc": "hello",
            "required": True,
            "validate": "str",
        })
        schema_inputs = {
            "get": dict([schema_name]),
            "post_login": dict([schema_date]),
        }
        schema_outputs = {
            "get": dict([schema_hello]),
            "post_login": dict([schema_hello])
        }

        def get(self, name):
            return {"hello": "world"}

        def post_login(self, date):
            return {"hello": "world"}


For more information, see `validater <https://github.com/guyskk/validater>`_


Authorize
----------

flask_restaction use ``json web token`` for authorize.

see https://github.com/jpadilla/pyjwt

**You should add you own auth_secret to api**, default auth_secret is ``"SECRET"``, see :ref:`api` for detail


You can access auth info by `request.me`, it's struct is:

.. code ::

    {
        "id":user_id, 
        "role":user_role
    }

And you should add auth header(default ``Authorization``) to response after user login, it's value can be generate
by ``api.gen_token(me)`` or ``api.gen_auth_token(me)``.

**user_role function of Resource**

.. code-block:: python

    class User(Resource):

        @staticmethod
        def user_role(user_id):
            return "role of user" or "*" if user not exists


This function must be decorated by ``@staticmethod``, it will be called before request and it's return value will be
in ``request.me["role"]``, then permission system will use it.

The Usage of user_role

A user can be different role in different field, and only one role in one field. A field consist of some Resources or only one Resource, so this can avoid the effect of user/permission system when add new Resource or new module to you application.

**Note:**

res.js will auto add auth header(default ``Authorization``) to request if needed, and will auto save auth token to localstroge when recive auth header


Permission control
------------------------------

``permission.json`` permission table

By default, ``permission.json`` should be saved in root path of you flask application, you can change to other path, see :ref:`api` .

permission subdivide by role->resource->action

JSON struct

.. code ::

    {
        "role/*": {
            "*/resource*": ["get", "post"],
            "resource": ["action", ...]
        },
        ...
    }

- When role is ``*``, represent anonymous user.

- When resource is ``*``, represent the role can access all resources all actions, actions must be ``[]`` and can't has other resource.

- When resource is ``resource*``, represent the role can access this resource's all action, actions must be ``[]``.

- role and resource must be combine of a-z_0-9 and start with a-z.

Work with Blueprint
---------------------

.. code-block :: python

    from flask import Flask, Blueprint
    from flask_restaction import Api
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


- You should add ``static_folder='something'`` to Blueprint if you need gen_resjs or gen_resdocs, because res.js and resdocs is save in Blueprint's static_folder.

- You should do #1, #2, #3, #4 orderly, otherwise will cause error, because Resource urls was registered when register_blueprint and permission was inited after register_blueprint.


Process Flow
---------------------

.. image:: _static/flask-restaction.svg