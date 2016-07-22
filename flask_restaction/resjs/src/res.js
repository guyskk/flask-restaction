require('es6-promise').polyfill();
var ajax = require('axios');
var res = {
    ajax: ajax,
    clearToken: function() {
        window.localStorage.removeItem('resjs-auth-token');
    },
    setToken: function(token) {
        window.localStorage['resjs-auth-token'] = token;
    },
    getToken: function() {
        return window.localStorage['resjs-auth-token'];
    },
};

function init(authHeader, urlPrefix) {
    res.config = {
        urlPrefix: urlPrefix,
        authHeader: authHeader.toLowerCase()
    };
    return function(url, method) {
        return function(data) {
            var options = {
                url: res.config.urlPrefix + url,
                method: method,
                headers: {}
            };
            if (res.config.authHeader) {
                var token = res.getToken();
                if (token) {
                    options.headers[res.config.authHeader] = token;
                }
            }
            if (method == 'PUT' || method == 'POST' || method == 'PATCH') {
                options.data = data;
            } else {
                options.params = data;
            }
            return ajax(options).then(function(response) {
                if (res.config.authHeader) {
                    var token = response.headers[res.config.authHeader];
                    if (token) {
                        res.setToken(token);
                    }
                }
                return response.data;
            }).catch(function(error) {
                if (error.response) {
                    throw error.response.data;
                } else {
                    throw error.message;
                }
            });
        };
    };
}

var res_core = "#res-core.js#";
res_core(res, init);

module.exports = res;
