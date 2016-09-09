// 用ES6的Proxy实现res.js，实验性功能
import { toUrl } from './index.js'
import root, { init } from './res.base.js'

function Res(authHeader = 'Authorization', urlPrefix = '') {
    function core(root, init) {
        let q = init(authHeader.toLowerCase(), urlPrefix)
        return new Proxy(root, {
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
    return core(root, init)
}

module.exports = Res
