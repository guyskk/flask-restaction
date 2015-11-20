.. _resjs:

res.js
======

res.ajax
--------

.. code-block:: javascript

    /*
    用法：
        res.ajax(url, options)
    参数 options：
        {
            method: "get/post/...",
            data: "object/string(id)/formdata",
            header: {},
            fn: function(err, data, header, xhr) {

            },
            progress: function(percent, msg) {

            }
        }
    当 data 是 formdata: 
        表示上传文件, method必须是POST。
    当 data 是 string(id):
        表示input控件id, 会从其中获取要上传的文件, method必须是POST。
    */
   

res.resource.action
----------------------

.. code-block:: javascript

    /*
    用法：
        res.resource.action(data,fn,progress)
    当不需要传递data时使用:
        res.resource.action(fn,progress)
        或
        res.resource.action(null,fn,progress)
    说明：
        data：要向服务器提交的数据
        fn：function(err, data, header, xhr)
        progress: function(percent, msg)

        此文件是根据后端 API 自动生成，调用需要授权的接口时，
        会自动向请求头中添加 'res_token'。
        登录成功后将请求头中的 'res_token' 自动储存在浏览器 localStorage 中。

    可以设置 res.website_url，这样可以将 ajax 请求的 url 变成绝对 url。

    */

    (function(res) {

        function addToken(header){
            if (header!==null) {
                if(window.localStorage){
                    _token = window.localStorage.{{apiinfo.auth_token_name}};
                    if(_token){
                        header["{{apiinfo.auth_token_name}}"]=_token;
                    }
                }
            }
        }

        function saveToken(xhr) {
            token=xhr.getResponseHeader("{{apiinfo.auth_token_name}}")
            if (token!==null && window.localStorage) {
                window.localStorage.{{apiinfo.auth_token_name}} = token;
            }
        }

        header_accept="application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8";
        
        /*网址, 例如 http://www.example.com, 最后面不要斜杠*/
        res.website_url="";
        res.clear_token=function() {
            window.localStorage.removeItem("{{apiinfo.auth_token_name}}")
        }
        
        /*当不需要传递数据时，回调函数参数顺序是: fn,progress,null*/
        function request(url,method,data,fn,progress) {
            if (progress===null && typeof(data)==="function"){
                progress = fn;
                fn = data;
                data = null;
            }
            header={accept:header_accept};
            addToken(header);
            var _fn=function(err, data, header, xhr){
                saveToken(xhr);
                if(typeof(fn)==="function"){
                    fn(err, data, header, xhr);
                }
            }
            res.ajax(res.website_url+url,{
                method:method,
                data:data,
                header: header,
                fn:_fn,
                progress:progress
            });
        }

        {%- for name,res in resources.items() %}
        res.{{name}}={};
            {%- for action in res["actions"] %}
            res.{{name}}.{{action.action}}=function(data,fn,progress){request("{{apiinfo.url_prefix+action.url}}","{{action.httpmethod}}",data,fn,progress) };
            {%- endfor %}
        {%- endfor -%}
        
    })(res);
