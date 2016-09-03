'use strict';

var _promise = require('babel-runtime/core-js/promise');

var _promise2 = _interopRequireDefault(_promise);

var _assign = require('babel-runtime/core-js/object/assign');

var _assign2 = _interopRequireDefault(_assign);

var _superagent = require('superagent');

var _superagent2 = _interopRequireDefault(_superagent);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

require('es6-promise').polyfill();


var base = {};

function init(authHeader, urlPrefix) {
    base.config = { authHeader: authHeader, urlPrefix: urlPrefix };
    if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
        (function () {
            var token = null;
            (0, _assign2.default)(base, {
                clearToken: function clearToken() {
                    token = null;
                },
                setToken: function setToken(token) {
                    token = token;
                },
                getToken: function getToken() {
                    return token;
                }
            });
        })();
    } else {
        (0, _assign2.default)(base, {
            clearToken: function clearToken() {
                window.localStorage.removeItem('resjs-auth-token');
            },
            setToken: function setToken(token) {
                window.localStorage['resjs-auth-token'] = token;
            },
            getToken: function getToken() {
                return window.localStorage['resjs-auth-token'];
            }
        });
    }
    return function (url, method) {
        return function (data) {
            var request = (0, _superagent2.default)(method, base.config.urlPrefix + url);
            request = request.set('Accept', 'application/json');
            if (base.config.authHeader) {
                var token = base.getToken();
                if (token) {
                    request = request.set(base.config.authHeader, token);
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
                            var _token = response.header[base.config.authHeader];
                            if (_token) {
                                base.setToken(_token);
                            }
                        }
                        resolve(response.body);
                    }
                });
            });
        };
    };
}

var core = "#res.core.js#";
core(base, init);

module.exports = base;