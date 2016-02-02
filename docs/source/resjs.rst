.. _resjs:

res.js
======

此文件是根据后端 API 自动生成，发出请求时会自动向请求头中添加 auth token,
收到响应后会自动将响应头中的 auth token 储存在浏览器 localStorage 中。


res.ajax
--------

用法::

    res.ajax(url, method, data).then(function(value){
        # success
    }).catch(function(error){
        # error
    }).done(function(value, error){
        # finish
    }).doing(function(progress){
        # will be called on uploading
        # 0 <= progress <= 100
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
    }).doing(function(progress){
        # update progress bar
    })
   

res.resource.action
----------------------

用法::

    res.resource.action(data).then(function(value){
        # success
    }).catch(function(error){
        # error
    }).done(function(value, error){
        # finish
    }).doing(function(progress){
        # will be called on uploading
        # 0 <= progress <= 100
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
    }).doing(function(progress){
        # update progress bar
    })


res.clear_token
----------------------

清除浏览器 localStorage 中的 auth token

.. code-block:: javascript

    res.clear_token()

