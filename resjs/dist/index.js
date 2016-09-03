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

var _commander = require('commander');

var _commander2 = _interopRequireDefault(_commander);

var _handlebars = require('handlebars');

var _handlebars2 = _interopRequireDefault(_handlebars);

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

function parseTemplate() {
    var filename = (0, _path.join)(__dirname, 'res.core.hbs');
    return new _promise2.default(function (resolve, reject) {
        _fs2.default.readFile(filename, { encoding: 'utf-8' }, function (error, data) {
            if (error) {
                reject(error);
            } else {
                try {
                    resolve(_handlebars2.default.compile(data));
                } catch (ex) {
                    reject(ex);
                }
            }
        });
    });
}

function parseResjs() {
    var node = arguments.length <= 0 || arguments[0] === undefined ? false : arguments[0];

    var filename = 'res.web.js';
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

    return _promise2.default.all([parseMeta(url), parseTemplate(), parseResjs(node)]).then(function (_ref) {
        var _ref2 = (0, _slicedToArray3.default)(_ref, 3);

        var meta = _ref2[0];
        var template = _ref2[1];
        var generate = _ref2[2];

        if (urlPrefix) {
            meta.urlPrefix = urlPrefix;
        }
        var code = generate(template(meta));
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

// cli
_commander2.default.version('0.0.1').description('generated res.js').arguments('<url> [dest]').option('-p, --prefix [prefix]', 'urlPrefix of generated res.js').option('-n, --node [node]', 'generate for nodejs or not').action(function (url, dest, options) {
    return resjs(url, dest, options.prefix, options.node);
});
_commander2.default.parse(process.argv);