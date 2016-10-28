import {
    AsyncStorage
} from 'react-native'

const base = {
    async clearToken () {
        await AsyncStorage.removeItem('resjs-auth-token')
    },
    async setToken (token) {
        await AsyncStorage.setItem('resjs-auth-token', token)
    },
    async getToken () {
        return await AsyncStorage.getItem('resjs-auth-token')
    }
}

function init (authHeader, urlPrefix) {
    let token = null
    base.config = { authHeader, urlPrefix }
    return function (url, method) {
        return async (data) => {
            let uri = base.config.urlPrefix + url
            const options = {
                method,
                headers: {
                    Accept: 'application/json',
                    'Content-Type': 'application/json',
                    // @TODO To be or not to be, this is a question.
                    From: 'ReactNative'
                }
            }
            if (base.config.authHeader) {
                let token = await base.getToken()
                if (token) {
                    options.headers[base.config.authHeader] = token
                }
            }
            if (method == 'PUT' || method == 'POST' || method == 'PATCH') {
                options.body = JSON.stringify(data)
            } else {
                uri += '?' + getQueryString(data)
            }
            return new Promise(async (resolve, reject) => {
                const response = await fetch(uri, options)
                const json = await response.json()
                if (response.status !== 200) {
                    reject(json)
                } else {
                    const token = response.headers.get(base.config.authHeader)
                    if (token) {
                        base.setToken(token)
                    }
                    resolve(json)
                }
            })
        }
    }
}

function getQueryString (data = {}) {
    const qs = Object.keys(data)
        .map(k => encodeURIComponent(k) + '=' + encodeURIComponent(data[k]))
        .join('&')
    return qs
}

let core = "#res.core.js#"
core(base, init)

module.exports = base
