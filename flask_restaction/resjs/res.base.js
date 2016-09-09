import ajax from 'superagent'

let base = { ajax }

function init(authHeader, urlPrefix) {
    base.config = { authHeader, urlPrefix }
    if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
        let token = null
        base.clearToken = () => {
            token = null
        }
        base.setToken = (token) => {
            token = token
        }
        base.getToken = () => {
            return token
        }
    } else {
        base.clearToken = () => {
            window.localStorage.removeItem('resjs-auth-token')
        }
        base.setToken = (token) => {
            window.localStorage['resjs-auth-token'] = token
        }
        base.getToken = () => {
            return window.localStorage['resjs-auth-token']
        }
    }
    return function(url, method) {
        return function(data) {
            let request = ajax(method, base.config.urlPrefix + url)
            request = request.set('accept', 'application/json')
            if (base.config.authHeader) {
                let token = base.getToken()
                if (token) {
                    request = request.set(base.config.authHeader, token)
                }
            }
            if (method == 'PUT' || method == 'POST' || method == 'PATCH') {
                request = request.send(data)
            } else {
                request = request.query(data)
            }
            return new Promise((resolve, reject) => {
                request.end((error, response) => {
                    if (error) {
                        if (error.response) {
                            // 4xx or 5xx response
                            if (error.response.body) {
                                reject(error.response.body)
                            } else {
                                reject(error.response)
                            }
                        } else {
                            // Network failures, timeouts, and other errors
                            reject(error)
                        }
                    } else {
                        if (base.config.authHeader) {
                            let token = response.header[base.config.authHeader]
                            if (token) {
                                base.setToken(token)
                            }
                        }
                        if (response.body) {
                            // JSON response
                            resolve(response.body)
                        } else {
                            // unparsed response
                            resolve(response)
                        }
                    }
                })
            })
        }
    }
}

let core = "#res.core.js#"
core(base, init)

module.exports = base
