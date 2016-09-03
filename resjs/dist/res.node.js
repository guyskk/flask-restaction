'use strict';

var _promise = require('babel-runtime/core-js/promise');

var _promise2 = _interopRequireDefault(_promise);

var _superagent = require('superagent');

var _superagent2 = _interopRequireDefault(_superagent);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var base = { ajax: _superagent2.default };

function init(authHeader, urlPrefix) {
    base.config = { authHeader: authHeader, urlPrefix: urlPrefix };
    if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
        (function () {
            var token = null;
            base.clearToken = function () {
                token = null;
            };
            base.setToken = function (token) {
                token = token;
            };
            base.getToken = function () {
                return token;
            };
        })();
    } else {
        base.clearToken = function () {
            window.localStorage.removeItem('resjs-auth-token');
        };
        base.setToken = function (token) {
            window.localStorage['resjs-auth-token'] = token;
        };
        base.getToken = function () {
            return window.localStorage['resjs-auth-token'];
        };
    }
    return function (url, method) {
        return function (data) {
            var request = (0, _superagent2.default)(method, base.config.urlPrefix + url);
            request = request.set('accept', 'application/json');
            if (base.config.authHeader) {
                var _token = base.getToken();
                if (_token) {
                    request = request.set(base.config.authHeader, _token);
                }
            }
            if (method == 'PUT' || method == 'POST' || method == 'PATCH') {
                request = request.send(data);
            } else {
                request = request.query(data);
            }
            return new _promise2.default(function (resolve, reject) {
                request.end(function (error, response) {
                    if (error) {
                        if (error.response) {
                            // 4xx or 5xx response
                            if (error.response.body) {
                                reject(error.response.body);
                            } else {
                                reject(error.response);
                            }
                        } else {
                            // Network failures, timeouts, and other errors
                            reject(error);
                        }
                    } else {
                        if (base.config.authHeader) {
                            var _token2 = response.header[base.config.authHeader];
                            if (_token2) {
                                base.setToken(_token2);
                            }
                        }
                        if (response.body) {
                            // JSON response
                            resolve(response.body);
                        } else {
                            // unparsed response
                            resolve(response);
                        }
                    }
                });
            });
        };
    };
}

var core = "#res.core.js#";
core(base, init);

module.exports = base;