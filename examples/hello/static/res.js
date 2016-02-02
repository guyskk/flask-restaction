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
window.res = {};

(function(root) {

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
        if (options.header) {
            for (var k in options.header) {
                req.setRequestHeader(k, options.header[k]);
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

    root._ajax = sendRequest;
})(res);

(function(root) {
    function Promise(promise_fn) {
        var self = {};
        self.value = null;
        self.error = null;
        self.finished = false;
        self.progress = 0;
        self.resolve_callbacks = []
        self.reject_callbacks = []
        self.finish_callbacks = []
        self.progress_callbacks = []
        promise_fn(resolve, reject, doing);

        function resolve(value) {
            if (!self.finished) {
                self.value = value;
                self.finished = true;
                while (self.resolve_callbacks.length > 0) {
                    var fn = self.resolve_callbacks.shift();
                    var ret = fn(value);
                    if (ret != null) {
                        self.value = ret;
                    }
                }
                _finished();
            }
        }

        function reject(error) {
            if (!self.finished) {
                self.error = error;
                self.finished = true;
                while (self.reject_callbacks.length > 0) {
                    var fn = self.reject_callbacks.shift();
                    fn(error);
                }
                _finished();
            }
        }

        function doing(progress) {
            if (!self.finished) {
                self.progress = progress;
                for (var i = 0; i < self.progress_callbacks.length; i++) {
                    var fn = self.progress_callbacks[i];
                    fn(progress);
                }
            }
        }

        function _finished() {
            while (self.finish_callbacks.length > 0) {
                var fn = self.finish_callbacks.shift();
                fn(self.value, self.error);
            }
            self.progress_callbacks = [];
        }
        self.then = function(onFulfilled, onRejected) {
            if (typeof onFulfilled === 'function') {
                if (!self.finished) {
                    self.resolve_callbacks.push(onFulfilled);
                } else {
                    onFulfilled(self.value);
                }
            }
            if (typeof onRejected === 'function') {
                if (!self.finished) {
                    self.reject_callbacks.push(onRejected);
                } else {
                    onRejected(self.error);
                }
            }
            return self;
        }
        self.catch = function(onRejected) {
            return self.then(undefined, onRejected);
        }
        self.done = function(onFinished) {
            if (!self.finished) {
                if (typeof onFinished === 'function') {
                    self.finish_callbacks.push(onFinished)
                }
            } else {
                if (typeof onFinished === 'function') {
                    onFinished(self.value, self.error);
                }
            }
            return self;
        }
        self.doing = function(onProgress) {
            if (!self.finished) {
                if (typeof onProgress === 'function') {
                    self.progress_callbacks.push(onFinished)
                }
            }
            return self;
        }
        return self;
    }

    root._Promise = Promise;
})(res);


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
    var info = {
    "url_prefix": "", 
    "docs": "", 
    "auth_header": "", 
    "resources": [
        {
            "docs": "hello world", 
            "name": "hello", 
            "actions": [
                {
                    "inputs": "{\n  \"name\": {\n    \"default\": \"world\", \n    \"desc\": \"your name\", \n    \"validater\": \"safestr\"\n  }\n}", 
                    "endpoint": "hello", 
                    "outputs": "{\n  \"hello\": {\n    \"required\": true, \n    \"validater\": \"unicode\"\n  }\n}", 
                    "url": "/hello", 
                    "docs": "welcome to flask-restaction", 
                    "action": "get", 
                    "method": "get"
                }
            ]
        }
    ]
}
    parse_api(info);
})(res)