/*
用法：
    res.resource.action(data,fn,progress)
说明：
    data：要向服务器提交的数据
    fn：function(err, data, header, xhr)
    progress: function(percent, msg)

    此文件是根据后端API自动生成，调用需要授权的接口时，会自动向data数据中添加'_token'。登录成功后'_token'自动储存在浏览器localStorage中，并从返回的data中移除。
*/

(function(res) {
    
    /*以下为jinja2模板，用于生成js*/
    
    {% for name, actions in reslist %}
    res.{{name}}={};
        {% for url, meth, action, needtoken in actions %}
        res.{{name}}.{{action}}=function(data,fn,progress){
            headers={};
            {% if needtoken %}
            addToken(headers);
            {% endif %}
            var _fn=function(err, data, header, xhr){
                saveToken(header);
                if(typeof(fn)==="function"){
                    fn(err, data, header, xhr);
                }
            }
            res.ajax("{{url}}",{
                method:"{{meth}}",
                data:data,
                headers: headers,
                fn:_fn,
                progress:progress
            });
        };
        {% endfor %}
    {% endfor %}
    
    /*End jinja2模板*/
   
    

    function addToken(header){
        if(window.localStorage){
            var _token=window.localStorage._token;
            if(_token){
                header["Authorization"]=_token;
            }
        }
    }

    function saveToken(header) {
        if (header) {
            header["Authorization"]
            if (header["Authorization"] && window.localStorage) {
                window.localStorage._token = header["Authorization"];
            }
        }
    }

})(res);
