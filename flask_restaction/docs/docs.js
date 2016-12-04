function parseMeta(meta) {
    let basic = {}
    let roles = null
    let resources = {}
    for (let k in meta) {
        if (k.slice(0, 1) == '$') {
            if (k != "$roles") {
                basic[k] = meta[k]
            } else {
                roles = meta[k]
            }
        } else {
            resources[k] = meta[k]
        }
    }
    return { basic, roles, resources }
}

function isAllow(role, resource, action) {
    if (role[resource]) {
        if (role[resource].indexOf(action) >= 0) {
            return true
        }
    }
    return false
}

function strm(value) {
    // 去除字符串开头的 '#' 和 空白
    if (!value) {
        return value
    } else {
        return value.replace(/^[#\s]+/, '')
    }
}

function parseRole(role, resources) {
    let result = {}
    for (let resource in resources) {
        result[resource] = {}
        for (let action in resources[resource]) {
            if (isSpecial(action)) {
                continue
            }
            result[resource][action] = {
                desc: strm(resources[resource][action].$desc),
                allow: isAllow(role, resource, action)
            }
        }
    }
    return result
}

function isEmpty(value) {
    return !value || Object.keys(value).length === 0
}

function isSpecial(value) {
    return !value || value.slice(0, 1) == '$'
}

function route(app) {
    // 根据location.hash值显示对应的页面
    if (location.hash) {
        let state = location.hash.slice(1).split('.')
        if (state.length == 1) {
            if (state[0] == 'desc') {
                return app.showBasic()
            } else if (state[0] == 'meta') {
                return app.showMeta()
            }
        } else if (state.length == 2) {
            if (state[0] == 'roles') {
                if (state[1] in app.roles) {
                    return app.showRole(state[1])
                }
            } else if (state[0] == 'res') {
                if (state[1] in app.resources) {
                    return app.showResource(state[1])
                }
            }
        } else if (state.length == 3) {
            if (state[0] == 'res') {
                if (state[1] in app.resources) {
                    return app.showResource(state[1])
                }
            }
        }
    }
    app.showBasic()
}

let app = new Vue({
    el: '#app',
    data: {
        meta: null,
        metaText: null,
        basic: null,
        roles: null,
        resources: null,
        view: null,
        role: null,
        roleName: null,
        resource: null,
        resourceName: null,
        sidebar: true,
        isSpecial,
        isEmpty
    },
    methods: {
        showMeta() {
            this.view = 'meta'
        },
        showBasic() {
            this.view = 'basic'
        },
        showRole(name) {
            if (name in this.roles) {
                this.roleName = name
                this.role = parseRole(this.roles[name], this.resources)
                this.view = 'role'
            }
        },
        showResource(name) {
            if (name in this.resources) {
                this.resourceName = name
                this.resource = this.resources[name]
                this.view = 'resource'
            }
        },
        toggleSidebar() {
            if (this.sidebar === "none") {
                this.sidebar = "block"
            } else {
                this.sidebar = "none"
            }
        },
        hideSidebar() {
            if (window.innerWidth < 768) {
                this.sidebar = "none"
            }
        },
        toUrl(resource, action) {
            let prefix = this.meta.basic.$url_prefix || ''
            //Convert resource.action to "METHOD url", method is UpperCase
            let i = action.indexOf("_")
            if (i < 0) {
                return `${action.toUpperCase()} ${prefix}/${resource}`
            } else {
                return `${action.slice(0, i).toUpperCase()} ${prefix}/${action.slice(i+1)}`
            }
        }
    },
    created: function() {
        let metaText = document.getElementById('meta-text').value
        let meta = parseMeta(JSON.parse(metaText))
        this.metaText = metaText
        this.meta = meta
        this.basic = meta.basic
        this.roles = meta.roles
        this.resources = meta.resources
    },
    mounted: function() {
        route(this)
    },
    directives: {
        marked: function(el, binding) {
            if (binding.value !== undefined) {
                el.innerHTML = marked(binding.value)
            }
        },
        highlight: function(el, binding) {
            if (binding.value !== undefined) {
                let value = null
                if (typeof(binding.value) === "string") {
                    value = binding.value
                } else {
                    value = JSON.stringify(binding.value, null, 4)
                }
                el.innerHTML = hljs.highlight("json", value, true).value
            }
        }
    }
})

window.app = app
