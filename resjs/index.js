import fs from 'fs'
import { join } from 'path'
import ajax from 'superagent'
import program from 'commander'
import Handlebars from 'handlebars'

function toUrl(resource, action) {
    //Convert resource.action to {url, method}
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
    return readMeta(url).then(meta => {
        let authHeader = meta.$auth ? meta.$auth.header : null
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

function parseTemplate() {
    let filename = join(__dirname, 'res.core.hbs')
    return new Promise((resolve, reject) => {
        fs.readFile(filename, { encoding: 'utf-8' }, (error, data) => {
            if (error) {
                reject(error)
            } else {
                try {
                    resolve(Handlebars.compile(data))
                } catch (ex) {
                    reject(ex)
                }
            }
        })
    })
}

function parseResjs(node = false) {
    let filename = 'res.web.js'
    if (node) {
        filename = 'res.node.js'
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

function resjs(url, dest = './res.js', urlPrefix = undefined, node = undefined) {
    return Promise.all([parseMeta(url), parseTemplate(), parseResjs(node)])
        .then(([meta, template, generate]) => {
            if (urlPrefix) {
                meta.urlPrefix = urlPrefix
            }
            let code = generate(template(meta))
            return new Promise((resolve, reject) => {
                fs.writeFile(dest, code, (error) => {
                    if (error) {
                        reject(error)
                    } else {
                        resolve('OK')
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

// cli
program
    .version('0.0.1')
    .description('generated res.js')
    .arguments('<url> [dest]')
    .option('-p, --prefix [prefix]', 'urlPrefix of generated res.js')
    .option('-n, --node [node]', 'generate for nodejs or not')
    .action(function(url, dest, options) {
        return resjs(url, dest, options.prefix, options.node)
    })
program.parse(process.argv);
