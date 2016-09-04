/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};

/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {

/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId])
/******/ 			return installedModules[moduleId].exports;

/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			exports: {},
/******/ 			id: moduleId,
/******/ 			loaded: false
/******/ 		};

/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);

/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;

/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}


/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;

/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;

/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";

/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(0);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	'use strict';

	var _stringify = __webpack_require__(1);

	var _stringify2 = _interopRequireDefault(_stringify);

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

	function parseMeta(meta) {
	    var basic = {};
	    var roles = null;
	    var resources = {};
	    for (var k in meta) {
	        if (k.slice(0, 1) == '$') {
	            if (k != "$roles") {
	                basic[k] = meta[k];
	            } else {
	                roles = meta[k];
	            }
	        } else {
	            resources[k] = meta[k];
	        }
	    }
	    return { basic: basic, roles: roles, resources: resources };
	}
	marked('# Marked in browser\n\nRendered by **marked**.');
	var app = new Vue({
	    el: '#app',
	    data: {
	        meta: null,
	        basic: null,
	        roles: null,
	        resources: null,
	        showRaw: false,
	        currentView: null,
	        currentRole: null,
	        currentRoleName: null,
	        currentResource: null,
	        currentResourceName: null
	    },
	    methods: {
	        toggleRaw: function toggleRaw() {
	            app.showRaw = !app.showRaw;
	        },
	        showBasic: function showBasic() {
	            app.currentView = 'basic';
	        },
	        showRole: function showRole(role) {
	            app.currentRoleName = role;
	            app.currentRole = app.roles[role];
	            app.currentView = 'roles';
	        },
	        showResource: function showResource(resource) {
	            app.currentResourceName = resource;
	            app.currentResource = app.resources[resource];
	            app.currentView = 'resources';
	        }
	    },
	    created: function created() {
	        res.ajax('').set('Accept', 'application/json').then(function (response) {
	            if (response.status >= 200 && response.status <= 299) {
	                app.meta = response.body;
	                var meta = parseMeta(response.body);
	                app.basic = meta.basic;
	                app.roles = meta.roles;
	                app.resources = meta.resources;
	                app.currentView = 'basic';
	            } else {
	                app.message = (0, _stringify2.default)(response.body) || response.statusText;
	            }
	        });
	    },
	    directives: {
	        marked: {
	            bind: function bind(el, binding) {
	                if (binding.value && binding.value != binding.oldValue) {
	                    el.innerHTML = marked(binding.value);
	                }
	            },
	            update: function update(el, binding) {
	                if (binding.value && binding.value != binding.oldValue) {
	                    el.innerHTML = marked(binding.value);
	                }
	            }
	        }
	    }
	});

	window.app = app;

/***/ },
/* 1 */
/***/ function(module, exports, __webpack_require__) {

	module.exports = { "default": __webpack_require__(2), __esModule: true };

/***/ },
/* 2 */
/***/ function(module, exports, __webpack_require__) {

	var core  = __webpack_require__(3)
	  , $JSON = core.JSON || (core.JSON = {stringify: JSON.stringify});
	module.exports = function stringify(it){ // eslint-disable-line no-unused-vars
	  return $JSON.stringify.apply($JSON, arguments);
	};

/***/ },
/* 3 */
/***/ function(module, exports) {

	var core = module.exports = {version: '2.4.0'};
	if(typeof __e == 'number')__e = core; // eslint-disable-line no-undef

/***/ }
/******/ ]);