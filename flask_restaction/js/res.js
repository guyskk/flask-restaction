/*
用法：
    res.ajax(url, options)
参数 options：
    {
        method: "get/post/...",
        data: "object/string(id)/formdata",
        headers: {},
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

window.res = (function(window) {
    var res = {};

    function createQueryString(query) {
        var parts = [];
        for (var k in query) {
            if (query.hasOwnProperty(k)) {
                parts.push(encodeURIComponent(k) + "=" + encodeURIComponent(query[k]));
            }
        }
        return parts.join('&');
    }

    function isEmptyObject(obj) {
        for (var n in obj) {
            return false;
        }
        return true;
    }

    function isFormData(obj) {
        return Object.prototype.toString.call(obj) === "[object FormData]"
    }

    function sendRequest(url, options) {
        if (!url) {
            url = "";
        }
        if (!options) {
            options = {};
        }
        if (!options.method) {
            options.method = "GET";
        }
        var data = null;
        var isupload = false
        if (options.data) {
            if (options.method.toUpperCase() === "GET" || options.method.toUpperCase() === "DELETE") {
                var query = createQueryString(options.data);
                if (query) {
                    url += '?' + query;
                }
            } else if (isFormData(options.data)) {
                if (options.method.toUpperCase() !== "POST") {
                    throw "method must be POST when upload FormData";
                }
                isupload = true;
                data = options.data;
            } else if (typeof options.data === "string") {
                if (options.method.toUpperCase() !== "POST") {
                    throw "method must be POST when upload FormData";
                }
                var id = options.data;
                var ele = document.getElementById(id);
                if (!ele) {
                    throw "upload elementId'" + id + "' is invalid";
                }
                data = new FormData();
                if (ele.files.length === 0) {
                    throw "upload element'#" + id + "' has no file";
                }
                isupload = true;
                data.append(ele.name || 'upload', ele.files[0]);
            } else {
                data = JSON.stringify(options.data);
            }
        }

        var req = createXMLHTTPObject();
        if (!req) throw "AJAX is not supported";
        req.open(options.method, url, true);
        if (isupload) {
            //不要加请求头，浏览器会自动加上
            //req.setRequestHeader('Content-Type', 'multipart/form-data');
            req.upload.onprogress = function(event) {
                if (typeof options.progress === 'function') {
                    if (event.lengthComputable) {　　　　　　
                        var percent = event.loaded / event.total;　　　　
                        options.progress(percent, 'uploading');
                    }
                }
            };

            var onerror = function(event, msg) {
                var percent = 0;
                if (event.lengthComputable) {　　　　　　
                    percent = event.loaded / event.total;　　　　
                }　
                msg = '[' + req.status + ' ' + req.textStatus + ']' + (msg || '');
                if (typeof options.progress === 'function') {
                    options.progress(percent, msg);
                }
            };

            req.upload.onload = function(event) {
                if (typeof options.progress === 'function') {
                    options.progress(100, "success");
                }
            };
            req.upload.onabort = function(event) {
                onerror(event, "abort");
            };

            req.upload.ontimeout = function(event) {
                onerror(event, "timeout");
            };

            req.upload.onerror = function(event) {
                onerror(event, "error");
            };
        } else {
            req.setRequestHeader('Content-Type', 'application/json');
        }
        req.setRequestHeader('Accept', 'application/json');
        if (options.headers) {
            for (var k in options.headers) {
                req.setRequestHeader(k, options.headers[k]);
            }
        }
        req.onreadystatechange = function() {
            if (req.readyState != 4) return;
            var header = req.getAllResponseHeaders();
            var content_type = req.getResponseHeader('Content-Type');
            var data = req.responseText;
            if (data && content_type === "application/json") {
                try {
                    data = JSON.parse(req.responseText);
                } catch (ex) {}
            }
            var status_ok = [200, 201, 202, 204, 206, 304];
            if (typeof options.fn === 'function') {
                if (contains(status_ok, req.status)) {
                    options.fn(null, data, header, req);
                } else {
                    var msg = "[" + req.status + " " + req.statusText + "]";
                    options.fn(data || msg, null, header, req);
                }
            }
        };
        req.send(data);
    }

    function contains(arr, obj) {
        var i = arr.length;
        while (i--) {
            if (arr[i] === obj) {
                return true;
            }
        }
        return false;
    }

    var XMLHttpFactories = [
        function() {
            return new XMLHttpRequest();
        },
        function() {
            return new ActiveXObject("Msxml2.XMLHTTP");
        },
        function() {
            return new ActiveXObject("Msxml3.XMLHTTP");
        },
        function() {
            return new ActiveXObject("Microsoft.XMLHTTP");
        },
        function() {
            return new XDomainRequest();
        }
    ];

    function createXMLHTTPObject() {
        var xmlhttp = false;
        for (var i = 0; i < XMLHttpFactories.length; i++) {
            try {
                xmlhttp = XMLHttpFactories[i]();
            } catch (e) {
                continue;
            }
            break;
        }
        return xmlhttp;
    }

    res.ajax = sendRequest;
    return res;

})(window);


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
