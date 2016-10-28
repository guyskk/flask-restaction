import fs from 'fs'
import { join } from 'path'
import ajax from 'superagent'

function toUrl(resource, action) {
    //Convert resource.action to {url, method}, method is UpperCase
    let i = action.indexOf("_")
    if (i < 0) {
        return {
            url: "/" + resource,
            method: action.toUpperCase()
        }
    } else {
        return {
            url: `/${resource}/${action.slice(i+1)}`,
            method: action.slice(0, i).toUpperCase()
        }
    }
}

function readMeta(url) {
    return new Promise((resolve, reject) => {
        ajax('GET', url)
            .set('Accept', 'application/json')
            .end((error, response) => {
                if (error) {
                    reject(error)
                } else {
                    resolve(response.body)
                }
            })
    })
}

function parseMeta(url) {
    // authHeader is LowerCase
    return readMeta(url).then(meta => {
        let authHeader = meta.$auth ? meta.$auth.header.toLowerCase() : null
        let urlPrefix = meta.$url_prefix ? meta.$url_prefix : ''
        let resources = {}
        for (let k in meta) {
            if (k.slice(0, 1) != '$') {
                resources[k] = {}
                for (let action in meta[k]) {
                    if (action.slice(0, 1) != '$') {
                        resources[k][action] = toUrl(k, action)
                    }
                }
            }
        }
        return { authHeader, urlPrefix, resources }
    })
}

function renderCore(meta) {
    /*Generate res.code.js*/
    let code = ''
    code += `function(root, init) {\n`
    code += `  var q = init('${meta.authHeader}', '${meta.urlPrefix}');\n`
    code += `  var r = null;\n`
    for (let key in meta.resources) {
        code += `  r = root.${key} = {};\n`
        for (let action in meta.resources[key]) {
            let item = meta.resources[key][action]
            code += `    r.${action} = q('${item.url}', '${item.method}');\n`
        }
    }
    code += `}`
    return code
}

function parseResjs(node = false, rn = false, min = false) {
    let filename = min ? 'res.web.min.js' : 'res.web.js'
    if (node) {
        filename = 'res.node.js'
    }
    if (rn) {
        filename = 'res.rn.js'
    }
    filename = join(__dirname, filename)
    return new Promise((resolve, reject) => {
        fs.readFile(filename, { encoding: 'utf-8' }, (error, data) => {
            if (error) {
                reject(error)
            } else {
                resolve(core => {
                    return data.replace('"#res.core.js#"', core)
                })
            }
        })
    })
}

function resjs(url, dest = './res.js', urlPrefix = undefined, node = undefined, rn = undefined, min = undefined) {
    return Promise.all([parseMeta(url), parseResjs(node, rn, min)])
        .then(([meta, generate]) => {
            if (urlPrefix) {
                meta.urlPrefix = urlPrefix
            }
            let code = generate(renderCore(meta))
            return new Promise((resolve, reject) => {
                fs.writeFile(dest, code, (error) => {
                    if (error) {
                        reject(error)
                    } else {
                        resolve(`OK, saved in: ${dest}`)
                    }
                })
            })
        }).then(message => {
            console.log(message)
        }).catch(error => {
            console.log(error)
        })
}

module.exports = resjs
