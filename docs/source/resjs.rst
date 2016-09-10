.. _resjs:

res.js
======

res.js是对AJAX的封装，用res.js调用API非常简单，回调是Promise风格的。

生成res.js
----------

可以用flask-restaction提供的命令行工具或者 https://www.npmjs.com/package/resjs
生成res.js，两个用法一样，生成的代码也是完全一样的。

用法::

    usage: resjs [-h] [-d DEST] [-p PREFIX] [-n] [-m] url

    generate res.js for browser or nodejs

    positional arguments:
      url                   url of api meta

    optional arguments:
      -h, --help                  show this help message and exit
      -d DEST, --dest DEST        dest path to save res.js
      -p PREFIX, --prefix PREFIX  url prefix of generated res.js
      -n, --node                  generate res.js for nodejs, default for browser
      -m, --min                   minimize generated res.js, default not minimize

例如::

    resjs http://127.0.0.1:5000 -d static/res.js


res.js的用法
------------

HTTP请求使用的是 SuperAgent_，Promise使用的是
`babel-plugin-transform-runtime <https://babeljs.io/docs/plugins/transform-runtime/>`_ 。

发出请求时会自动添加 auth token(Authorization) 请求头,
收到响应后会自动将响应头中的 auth token(Authorization) 储存在浏览器 localStorage 中。

使用res.js::

    // 模块加载方式(UMD)
    var res = require('./res.js');

    //或引用 res.js 文件
    <script type="text/javascript" src="/static/res.js"></script>


res.ajax
--------

res.ajax 就是SuperAgent模块，用法见 SuperAgent_。


res.resource.action
----------------------

用法::

    res.resource.action({
        // some data
    }).then(function(value){
        // success
    }).catch(function(error){
        // error
    })

例如调用Hello的API::

    // Hello World
    res.hello.get({
        name: 'kk'
    }).then(function(value){
        console.log(value.message);
    }).catch(function(error){
        // error
    })


res.xxxToken
----------------------

.. code-block:: javascript

    // 清除浏览器 localStorage 中的 auth token
    res.clearToken()
    // 获取浏览器 localStorage 中的 auth token
    var token = res.getToken()
    // 设置浏览器 localStorage 中的 auth token
    res.setToken(token)


res.config
----------------------

.. code-block:: javascript

    //设置请求 url 前缀，可以用来指定请求的服务器
    res.config.urlPrefix = 'http://127.0.0.1:5000'
    //设置 auth 请求头，注意要是小写字母
    res.config.authHeader = 'authorization'


.. _SuperAgent: http://visionmedia.github.io/superagent/
