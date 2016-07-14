.. _resjs:

res.js
======

res.js是用框架提供的命令行工具自动生成的。

发出请求时会自动添加 auth token(Authorization) 请求头,
收到响应后会自动将响应头中的 auth token(Authorization) 储存在浏览器 localStorage 中。

用法::

    // 模块加载方式(UMD)
    var res = require('./res');

    //或引用 res.js 文件
    <script type="text/javascript" src="/static/res.js"></script>


res.ajax
--------

用法::

    res.ajax(url, method, data).then(function(value){
        # success
    }).catch(function(error){
        # error
    })

*当 data 是 formdata*
    表示上传文件, method必须是POST。
*当 data 是 string*
    表示 input 控件id, 会从其中获取要上传的文件, method必须是POST。
*其余情况下*
    data 是普通 js 对象

示例::
    
    # 登录
    res.ajax('/user/login', 'POST', {
        username: 'admin',
        password: '123456'
    }).then(function(value){
        # success
    }).catch(function(error){
        # error
    })

    # 上传
    res.ajax('/upload', 'POST', 'id_of_input').then(function(value){
        # success
    }).catch(function(error){
        # error
    })   

res.resource.action
----------------------

用法::

    res.resource.action(data).then(function(value){
        # success
    }).catch(function(error){
        # error
    })

示例::

    # 登录
    res.user.post_login({
        username: 'admin',
        password: '123456'
    }).then(function(value){
        # success
    }).catch(function(error){
        # error
    })

    # 上传
    res.upload.post('id_of_input').then(function(value){
        # success
    }).catch(function(error){
        # error
    })


.. Note:: 

    如果一个 API 是 POST/PUT 方法的, 并且全部参数是可选的:
    ``res.resource.post()`` 会报 400 invalid json content,
    因为空字符串不是有效的 json 格式, 需改成 ``res.resource.post({})``

    
res.clearToken
----------------------

清除浏览器 localStorage 中的 auth token

.. code-block:: javascript

    res.clear_token()


res.config.urlPrefix
----------------------

设置请求 url 前缀，可以用来指定请求的服务器

.. code-block:: javascript

    res.config.urlPrefix = 'http://127.0.0.1:5000'

