import fs from 'fs'
import { join } from 'path'
import ajax from 'axios'
import program from 'commander'
import Handlebars from 'handlebars'

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

function readMeta(url) {
    return ajax(url, { 'Accept': 'application/json' }).then(response => {
        return response.data
    }).catch(error => {
        if (error.response) {
            throw `$(error.response.status) $(error.response.statusText)`
        } else {
            throw error.message
        }
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
    console.log(__dirname)
    console.log(__filename)
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

function parseResjs() {
    let filename = join(__dirname, 'res.base.js')
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

function resjs(url, dest = './res.js', urlPrefix = undefined) {
    return Promise.all([parseMeta(url), parseTemplate(), parseResjs()])
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
    .action(function(url, dest, options) {
        console.log('%s %s %s', url, dest, options.prefix);
        return resjs(url, dest, options.prefix)
    })
program.parse(process.argv);
