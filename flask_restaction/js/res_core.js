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
    
    /*网址, 例如 http://www.example.com, 最后面不要斜杠*/
    res.website_url="";
    res.clear_token=function() {
        window.localStorage.removeItem("{{auth_token_name}}")
    }
    header_accept="application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8";

    /*以下为jinja2模板，用于生成js*/
    {% if blueprint != None and blueprint!="" %}
    res.{{blueprint}}={};
    ress=res.{{blueprint}};
    {% else %}
    ress=res;
    {% endif %}

    /*当不需要传递data时，参数顺序是fn,progress,null*/
    {% for name,doc,actions in reslist %}
    ress.{{name}}={};
        {% for url, meth, action, needtoken, inputs, outputs, docs in actions %}
        ress.{{name}}.{{action}}=function(data,fn,progress){
            if (progress===null && typeof(data)==="function"){
                progress = fn;
                fn = data;
                data = null;
            }
            header={accept:header_accept};
            {% if needtoken %}
            addToken(header,"{{auth_header}}");
            {% endif %}
            var _fn=function(err, data, header, xhr){
                saveToken(xhr,"{{auth_header}}");
                if(typeof(fn)==="function"){
                    fn(err, data, header, xhr);
                }
            }
            res.ajax(res.website_url+"{{url}}",{
                method:"{{meth}}",
                data:data,
                header: header,
                fn:_fn,
                progress:progress
            });
        };
        {% endfor %}
    {% endfor %}
    
    /*End jinja2模板*/

    function addToken(header, key){
        if (header!==null&&key!==null) {
            if(window.localStorage){
                _token = window.localStorage.{{auth_token_name}};
                if(_token){
                    header[key]=_token;
                }
            }
        }
    }

    function saveToken(xhr, key) {
        if (key!==null) {
            token=xhr.getResponseHeader(key)
            if (token!==null && window.localStorage) {
                window.localStorage.{{auth_token_name}} = token;
            }
        }
    }

})(res);
