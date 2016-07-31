.. _resjs:

res.js
======

res.js是对AJAX的封装，用res.js调用API非常简单，回调是Promise风格的。

用框架提供的命令行工具生成 res.js 和 res.min.js::

    resjs url -d dest

例如::

    resjs http://127.0.0.1:5000 -d static

会将生成的文件保存在 static 目录中。

HTTP请求使用的是 `axios <https://github.com/mzabriskie/axios>`_ 。

Promise使用的是 `es6-promise <https://github.com/stefanpenner/es6-promise>`_ 。

发出请求时会自动添加 auth token(Authorization) 请求头,
收到响应后会自动将响应头中的 auth token(Authorization) 储存在浏览器 localStorage 中。

使用res.js::

    // 模块加载方式(UMD)
    var res = require('./res');

    //或引用 res.js 文件
    <script type="text/javascript" src="/static/res.js"></script>

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


res.ajax
--------

res.ajax 就是 axios 模块，用法见 `axios-api <https://github.com/mzabriskie/axios#axios-api>`_


res.resource.action
----------------------

用法::

    res.resource.action(data).then(function(value){
        # success
    }).catch(function(error){
        # error
    })

示例::

    // Hello World
    res.hello.get({
        name: 'kk'
    }).then(function(value){
        console.log(value.message);
    }).catch(function(error){
        # error
    })

    // 登录
    res.user.post_login({
        username: 'admin',
        password: '123456'
    }).then(function(value){
        # success
    }).catch(function(error){
        # error
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

