/*
用法：
    var ajax = require('res-ajax');
    ajax(url, options);
参数 options：
    {
        method: "get/post/...",
        data: "object/string(id)/formdata",
        headers: {},
        fn: function(err, data, xhr) {

        },
        progress: function(percent, msg) {

        }
    }
当 data 是 formdata: 
    表示上传文件, method必须是POST。
当 data 是 string(id):
    表示input控件id, 会从其中获取要上传的文件, method必须是POST。
*/


function createQueryString(query) {
    var parts = [];
    for (var k in query) {
        if (query.hasOwnProperty(k)) {
            parts.push(encodeURIComponent(k) + "=" + encodeURIComponent(query[k]));
        }
    }
    return parts.join('&');
}


function isFormData(obj) {
    return Object.prototype.toString.call(obj) === "[object FormData]";
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

function getFormData(id) {
    var ele = window.document.getElementById(id);
    if (!ele) {
        throw "upload elementId '" + id + "' is invalid";
    }
    var data = new FormData();
    if (!ele.files || ele.files.length === 0) {
        throw "upload element'#" + id + "' has no file";
    }
    data.append(ele.name || '', ele.files[0]);
    return data;
}

function parseOptions(url, options) {
    if (!url) {
        url = "";
    }
    if (!options) {
        options = {};
    }
    var method = "GET";
    if (options.method) {
        method = options.method.toUpperCase();
    }
    var headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    };
    if (options.headers) {
        for (var k in options.headers) {
            headers[k] = options.headers[k];
        }
    }
    var data = options.data === undefined ? null : options.data;
    var hasData = options.data !== null;
    var isUpload = false;
    if (hasData) {
        if (method === "GET" || method === "DELETE") {
            var query = createQueryString(data);
            if (query) {
                url += '?' + query;
            }
        } else if (isFormData(data)) {
            if (method !== "POST") {
                throw "method must be POST when upload FormData";
            }
            isUpload = true;
        } else if (typeof data === "string") {
            if (method !== "POST") {
                throw "method must be POST when upload FormData";
            }
            data = getFormData(data);
            isUpload = true;
        } else {
            data = JSON.stringify(data);
        }
    }
    return {
        url: url,
        method: method,
        data: data,
        isUpload: isUpload,
        hasData: hasData,
        headers: headers,
        fn: options.fn,
        progress: options.progress,
    };
}

function sendRequest(url, options) {
    options = parseOptions(url, options);
    var req = createXMLHTTPObject();
    if (!req) {
        throw "AJAX is not supported";
    }
    req.open(options.method, options.url, true);
    if (options.isUpload) {
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
    }
    for (var k in options.headers) {
        req.setRequestHeader(k, options.headers[k]);
    }
    req.onreadystatechange = function() {
        if (req.readyState != 4) return;
        var content_type = req.getResponseHeader('Content-Type');
        var data = req.responseText;
        if (data && content_type === "application/json") {
            try {
                data = JSON.parse(req.responseText);
            } catch (ex) {}
        }
        var isSuccess = req.status >= 200 && req.status < 300 || status === 304;
        if (typeof options.fn === 'function') {
            if (isSuccess) {
                options.fn(null, data, req);
            } else {
                var msg = req.status + " " + req.statusText;
                options.fn(data || msg, null, req);
            }
        }
    };
    req.send(options.data);
}

module.exports = sendRequest;
