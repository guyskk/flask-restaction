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
    会自动向请求头中添加 'res_auth_token'。
    登录成功后将请求头中的 'res_auth_token' 自动储存在浏览器 localStorage 中。
*/
(function(root) {

    var ajax = root._ajax;
    var Promise = root._Promise;
    var auth_token = "res_auth_token";
    var auth_header = null;

    function addToken(header) {
        if (auth_header && header && window.localStorage) {
            token = window.localStorage[auth_token];
            if (token) {
                header[auth_header] = token;
            }
        }
    }

    function saveToken(xhr) {
        if (auth_header && window.localStorage) {
            token = xhr.getResponseHeader(auth_header)
            if (token) {
                window.localStorage[auth_token] = token;
            }
        }
    }

    function clear_token() {
        if (window.localStorage) {
            window.localStorage.removeItem(auth_token)
        }
    }

    function request(url, method, data) {
        header = {
            accept: "application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        };
        addToken(header);
        return Promise(function(resolve, reject, doing) {
            ajax(url, {
                method: method,
                data: data,
                header: header,
                fn: function(err, data, header, xhr) {
                    saveToken(xhr);
                    if (err) {
                        reject(err);
                    } else {
                        resolve(data);
                    }
                },
                progress: doing
            });
        });
    }

    function parse_api(info) {
        auth_header = info.auth_header;
        for (var i = 0; i < info.resources.length; i++) {
            var resource = info.resources[i];
            root[resource.name] = {};
            for (var j = 0; j < resource.actions.length; j++) {
                var action = resource.actions[j];
                root[resource.name][action.action] = (function(action) {
                    return function(data) {
                        return request(info.url_prefix + action.url, action.method, data);
                    };
                })(action);
            }
        }
    }
    root.clear_token = clear_token;
    root.ajax = request;
    var info = {{apiinfo}}
    parse_api(info);
})(res)
