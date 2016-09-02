import ajax from 'axios'

function toUrl(resource, action) {
    //Convert resource.action to {url, method}
    let i = action.indexOf("_")
    if (i < 0) {
        return {
            url: "/" + resource,
            method: action
        }
    } else {
        return {
            url: `/${resource}/${action.slice(i+1)}`,
            method: action.slice(0, i)
        }
    }
}

function Res(urlPrefix = '', authHeader = 'Authorization') {
    let base = {
        ajax: ajax,
        config: {
            urlPrefix: urlPrefix,
            authHeader: authHeader.toLowerCase()
        }
    }
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
    let q = function(url, method) {
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
    return new Proxy(base, {
        get: function(target1, resource) {
            if (resource in target1) {
                return target1[resource]
            }
            return new Proxy({}, {
                get: function(target2, action) {
                    if (action in target2) {
                        return target2[action]
                    }
                    let { url, method } = toUrl(resource, action)
                    return q(url, method)
                }
            })
        }
    })
}

module.exports = Res
