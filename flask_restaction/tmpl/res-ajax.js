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
