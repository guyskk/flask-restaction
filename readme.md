# Flask-Restaction

### you can do this Easily

- Create restful api 
- Validate inputs and Convert outputs
- Authorize and Permission control
- Auto generate res.js


### Install
    
    pip install flask-restaction


### Build Document

    cd docs
    make html

### Readthedocs

http://flask-restaction.readthedocs.org/zh/latest/

**The document's api part has some problems on readthedocs, please clone the source code(`git clone git@github.com:guyskk/flask-restaction.git`) and build document manually. π_π!!**

If you know how to fix this problem, don't hesitate to give me a favor.


```
Running Sphinx v1.3.1
making output directory...
loading translations [zh]... done
loading intersphinx inventory from https://docs.python.org/objects.inv...
building [mo]: targets for 0 po files that are out of date
building [readthedocs]: targets for 7 source files that are out of date
updating environment: 7 added, 0 changed, 0 removed
reading sources... [ 14%] api
reading sources... [ 28%] index
reading sources... [ 42%] permission
reading sources... [ 57%] quickstart
reading sources... [ 71%] res.js
reading sources... [ 85%] resource
reading sources... [100%] validater

/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/checkouts/latest/docs/source/api.rst:14: WARNING: autodoc: failed to import class u'Api' from module u'flask_restaction'; the following exception was raised:
Traceback (most recent call last):
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/sphinx/ext/autodoc.py", line 385, in import_object
    __import__(self.modname)
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/flask_restaction/__init__.py", line 92, in <module>
    from resource import Resource
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/flask_restaction/resource.py", line 6, in <module>
    from validater import validate
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/validater/__init__.py", line 5, in <module>
    from .validaters import validaters, add_validater
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/validater/validaters.py", line 3, in <module>
    from bson.objectid import ObjectId
ImportError: No module named objectid
/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/checkouts/latest/docs/source/api.rst:22: WARNING: autodoc: failed to import class u'Resource' from module u'flask_restaction'; the following exception was raised:
Traceback (most recent call last):
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/sphinx/ext/autodoc.py", line 385, in import_object
    __import__(self.modname)
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/flask_restaction/__init__.py", line 92, in <module>
    from resource import Resource
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/flask_restaction/resource.py", line 6, in <module>
    from validater import validate
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/validater/__init__.py", line 5, in <module>
    from .validaters import validaters, add_validater
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/validater/validaters.py", line 3, in <module>
    from bson.objectid import ObjectId
ImportError: No module named objectid
/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/checkouts/latest/docs/source/api.rst:30: WARNING: autodoc: failed to import class u'Permission' from module u'flask_restaction'; the following exception was raised:
Traceback (most recent call last):
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/sphinx/ext/autodoc.py", line 385, in import_object
    __import__(self.modname)
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/flask_restaction/__init__.py", line 92, in <module>
    from resource import Resource
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/flask_restaction/resource.py", line 6, in <module>
    from validater import validate
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/validater/__init__.py", line 5, in <module>
    from .validaters import validaters, add_validater
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/validater/validaters.py", line 3, in <module>
    from bson.objectid import ObjectId
ImportError: No module named objectid
/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/checkouts/latest/docs/source/api.rst:75: WARNING: autodoc: failed to import module u'validater.validate'; the following exception was raised:
Traceback (most recent call last):
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/sphinx/ext/autodoc.py", line 385, in import_object
    __import__(self.modname)
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/validater/__init__.py", line 5, in <module>
    from .validaters import validaters, add_validater
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/validater/validaters.py", line 3, in <module>
    from bson.objectid import ObjectId
ImportError: No module named objectid
/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/checkouts/latest/docs/source/api.rst:81: WARNING: autodoc: failed to import module u'validater.validaters'; the following exception was raised:
Traceback (most recent call last):
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/sphinx/ext/autodoc.py", line 385, in import_object
    __import__(self.modname)
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/validater/__init__.py", line 5, in <module>
    from .validaters import validaters, add_validater
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/validater/validaters.py", line 3, in <module>
    from bson.objectid import ObjectId
ImportError: No module named objectid
/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/checkouts/latest/docs/source/api.rst:87: WARNING: autodoc: failed to import class u'ProxyDict' from module u'validater'; the following exception was raised:
Traceback (most recent call last):
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/sphinx/ext/autodoc.py", line 385, in import_object
    __import__(self.modname)
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/validater/__init__.py", line 5, in <module>
    from .validaters import validaters, add_validater
  File "/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/envs/latest/local/lib/python2.7/site-packages/validater/validaters.py", line 3, in <module>
    from bson.objectid import ObjectId
ImportError: No module named objectid
looking for now-outdated files... none found
pickling environment... done
checking consistency... done
preparing documents... done
writing output... [ 14%] api
writing output... [ 28%] index
writing output... [ 42%] permission
writing output... [ 57%] quickstart
writing output... [ 71%] res.js
writing output... [ 85%] resource
writing output... [100%] validater

generating indices... genindex py-modindex
writing additional pages... search
copying static files... WARNING: html_static_path entry u'/home/docs/checkouts/readthedocs.org/user_builds/flask-restaction/checkouts/latest/docs/source/_static' does not exist
done
copying extra files... done
dumping search index in English (code: en) ... done
dumping object inventory... done
build succeeded, 7 warnings.
Copying readthedocs-dynamic-include.js_t... done
Copying readthedocs-data.js_t... done
```

## Quickstart

#### A minimal Flask-Restaction API looks like this:

```python
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
api.gen_res_js()

if __name__ == '__main__':
    app.run(debug=True)

```
save this as `hello.py`, then run it: 

    $ python hello.py
     * Running on http://127.0.0.1:5000/
     * Restarting with reloader

then open browser, visit `http://127.0.0.1:5000/hello`
you will see: 

    {
      "hello": "world"
    }

if you visit `http://127.0.0.1:5000/hello?name=kk`
you will see: 

    {
      "hello": "kk"
    }

if you visit `http://127.0.0.1:5000/hello?name=kk`
you will see: 

    {
      "hello": "kk"
    }

### Use res.js

Les's write test.html and save it in static folder

```html
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
```
then open browser, visit `http://127.0.0.1:5000/static/test.html`

have a try, notice schema_inputs's `"validate": "safestr"`

if you input some unsafe strings, such as: 

`<script type="text/javascript">alert("haha")</script>`

then you inputs will be escape to avoid attack:

`{"hello":"&lt;script type=&#34;text/javascript&#34;&gt;alert(&#34;haha&#34;)&lt;/script&gt;"}`

#### res.js

look at this:

```javascript
res.hello.get(data, function(err, value) {
    msg = JSON.stringify(err || value)
    document.getElementById("message").innerText = msg;
});
```

now we can use `res.resource.action(data, function(err, value))` to access resources provided by rest api.

`resource` is resource's name, such as 'hello',

`action` is ... such as `get`,`post` ... not only http method, `getlist`,`upload` is ok.

### More about validate

see <https://github.com/guyskk/validater>

### Authorize and Permission control

#### authorize

flask_restaction use 'json web token' for authorize.
see <https://github.com/jpadilla/pyjwt>

you should config `RESOURCE_JWT_SECRET` in `app.config`,

defalut value is `"DEFAULT_RESOURCE_JWT_SECRET"`

you can config `RESOURCE_JWT_ALG` in `app.config`,

defalut value is 'HS256'

token store in `request.headers.["Authorization"]`

you can access auth info by `request.me`, it's struct is:

    {
        "id":user_id, 
        "role":user_role
    }

and you should add `Authorization` header to response after user login, 

it's value can be generate by `api.gen_token(self, me)`

Note:

res.js will auto add `Authorization` header to request if needed, and will auto save `Authorization` token to localstroge when recive `Authorization` header


#### Permission 权限分配表

`permission.json` should be saved in root path of you flask application

权限按role->resource->action划分

JSON 文件格式
```json
{
    "role/*": {
        "*/resource*": ["get", "post"],
        "resource": ["action", ...]
    },
    ...
}
```
- role为`*`时，表示匿名用户的权限。
- resource为`*`时，表示拥有所有resource的所有action权限，此时actions必须为`[]`且不能有其他resource。
- resource为`resource*`时，表示拥有此resource的所有action权限，此时actions必须为`[]`。
- role和resource（除去`*`号）只能是字母数字下划线组合，且不能以数字开头。


### Next Todo

- tests 
- support blueprint
- document
- ...
