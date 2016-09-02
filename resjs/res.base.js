import ajax from 'axios'

let base = { ajax: ajax }

function init(urlPrefix, authHeader) {
    base.config = { urlPrefix, authHeader }
        // {
        //     urlPrefix: urlPrefix,
        //     authHeader: authHeader.toLowerCase()
        // }
    if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
        let token = null
        Object.assign(base, {
            clearToken() {
                token = null
            },
            setToken(token) {
                token = token
            },
            getToken() {
                return token
            }
        })
    } else {
        Object.assign(base, {
            clearToken() {
                window.localStorage.removeItem('resjs-auth-token')
            },
            setToken(token) {
                window.localStorage['resjs-auth-token'] = token
            },
            getToken() {
                return window.localStorage['resjs-auth-token']
            }
        })
    }
    return function(url, method) {
        return function(data) {
            var options = {
                url: base.config.urlPrefix + url,
                method: method,
                headers: { 'Accept': 'application/json' }
            }
            if (base.config.authHeader) {
                var token = base.getToken()
                if (token) {
                    options.headers[base.config.authHeader] = token
                }
            }
            if (method == 'PUT' || method == 'POST' || method == 'PATCH') {
                options.data = data
            } else {
                options.params = data
            }
            return base.ajax(options).then(function(response) {
                if (base.config.authHeader) {
                    var token = response.headers[base.config.authHeader]
                    if (token) {
                        base.setToken(token)
                    }
                }
                return response.data
            }).catch(function(error) {
                if (error.response) {
                    throw error.response.data
                } else {
                    throw error.message
                }
            })
        }
    }
}

let core = "#res.core.js#";
core(base, init);

module.exports = base;
