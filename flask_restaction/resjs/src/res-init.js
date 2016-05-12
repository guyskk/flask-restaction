var ajax = require('./res-ajax');
var es6_promise = require('es6-promise');
var Promise = typeof Promise === 'function' ? Promise : es6_promise.Promise;

function init(res, authHeader, urlPrefix) {

    // get token from storage and add it to request headers
    function addToken(authHeader, headers) {
        if (authHeader && headers && window.localStorage) {
            var token = window.localStorage['resjs-auth-token'];
            if (token) {
                headers[authHeader] = token;
            }
        }
    }

    // get token from response headers and save it to storage
    function saveToken(authHeader, xhr) {
        if (authHeader && window.localStorage) {
            var token = xhr.getResponseHeader(authHeader);
            if (token) {
                window.localStorage['resjs-auth-token'] = token;
            }
        }
    }

    // delete token from storage
    function clearToken() {
        if (window.localStorage) {
            window.localStorage.removeItem('resjs-auth-token');
        }
    }

    function request(url, method, data) {
        var headers = {};
        addToken(authHeader, headers);
        return new Promise(function(resolve, reject) {
            ajax(url, {
                method: method,
                data: data,
                headers: headers,
                fn: function(err, data, xhr) {
                    if (err) {
                        reject(err);
                    } else {
                        saveToken(authHeader, xhr);
                        resolve(data);
                    }
                }
            });
        });
    }

    function q(url, method) {
        return function(data) {
            return request(res.config.urlPrefix + url, method, data);
        };
    }
    res.clearToken = clearToken;
    res.ajax = request;
    res.config = {
        urlPrefix: urlPrefix
    };
    return q;
}

module.exports = init;
