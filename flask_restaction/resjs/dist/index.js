'use strict';

var _slicedToArray2 = require('babel-runtime/helpers/slicedToArray');

var _slicedToArray3 = _interopRequireDefault(_slicedToArray2);

var _promise = require('babel-runtime/core-js/promise');

var _promise2 = _interopRequireDefault(_promise);

var _fs = require('fs');

var _fs2 = _interopRequireDefault(_fs);

var _path = require('path');

var _superagent = require('superagent');

var _superagent2 = _interopRequireDefault(_superagent);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function toUrl(resource, action) {
    //Convert resource.action to {url, method}, method is UpperCase
    var i = action.indexOf("_");
    if (i < 0) {
        return {
            url: "/" + resource,
            method: action.toUpperCase()
        };
    } else {
        return {
            url: '/' + resource + '/' + action.slice(i + 1),
            method: action.slice(0, i).toUpperCase()
        };
    }
}

function readMeta(url) {
    return new _promise2.default(function (resolve, reject) {
        (0, _superagent2.default)('GET', url).set('Accept', 'application/json').end(function (error, response) {
            if (error) {
                reject(error);
            } else {
                resolve(response.body);
            }
        });
    });
}

function parseMeta(url) {
    // authHeader is LowerCase
    return readMeta(url).then(function (meta) {
        var authHeader = meta.$auth ? meta.$auth.header.toLowerCase() : null;
        var urlPrefix = meta.$url_prefix ? meta.$url_prefix : '';
        var resources = {};
        for (var k in meta) {
            if (k.slice(0, 1) != '$') {
                resources[k] = {};
                for (var action in meta[k]) {
                    if (action.slice(0, 1) != '$') {
                        resources[k][action] = toUrl(k, action);
                    }
                }
            }
        }
        return { authHeader: authHeader, urlPrefix: urlPrefix, resources: resources };
    });
}

function renderCore(meta) {
    /*Generate res.code.js*/
    var code = '';
    code += 'function(root, init) {\n';
    code += '  var q = init(\'' + meta.authHeader + '\', \'' + meta.urlPrefix + '\');\n';
    code += '  var r = null;\n';
    for (var key in meta.resources) {
        code += '  r = root.' + key + ' = {};\n';
        for (var action in meta.resources[key]) {
            var item = meta.resources[key][action];
            code += '    r.' + action + ' = q(\'' + item.url + '\', \'' + item.method + '\');\n';
        }
    }
    code += '}';
    return code;
}

function parseResjs() {
    var node = arguments.length <= 0 || arguments[0] === undefined ? false : arguments[0];
    var min = arguments.length <= 1 || arguments[1] === undefined ? false : arguments[1];

    var filename = min ? 'res.web.min.js' : 'res.web.js';
    if (node) {
        filename = 'res.node.js';
    }
    filename = (0, _path.join)(__dirname, filename);
    return new _promise2.default(function (resolve, reject) {
        _fs2.default.readFile(filename, { encoding: 'utf-8' }, function (error, data) {
            if (error) {
                reject(error);
            } else {
                resolve(function (core) {
                    return data.replace('"#res.core.js#"', core);
                });
            }
        });
    });
}

function resjs(url) {
    var dest = arguments.length <= 1 || arguments[1] === undefined ? './res.js' : arguments[1];
    var urlPrefix = arguments.length <= 2 || arguments[2] === undefined ? undefined : arguments[2];
    var node = arguments.length <= 3 || arguments[3] === undefined ? undefined : arguments[3];
    var min = arguments.length <= 4 || arguments[4] === undefined ? undefined : arguments[4];

    return _promise2.default.all([parseMeta(url), parseResjs(node, min)]).then(function (_ref) {
        var _ref2 = (0, _slicedToArray3.default)(_ref, 2);

        var meta = _ref2[0];
        var generate = _ref2[1];

        if (urlPrefix) {
            meta.urlPrefix = urlPrefix;
        }
        var code = generate(renderCore(meta));
        return new _promise2.default(function (resolve, reject) {
            _fs2.default.writeFile(dest, code, function (error) {
                if (error) {
                    reject(error);
                } else {
                    resolve('OK, saved in: ' + dest);
                }
            });
        });
    }).then(function (message) {
        console.log(message);
    }).catch(function (error) {
        console.log(error);
    });
}

module.exports = resjs;