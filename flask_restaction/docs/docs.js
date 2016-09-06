function parseMeta(meta) {
    let basic = {}
    let roles = null;
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

window.isEmpty = function(value) {
    return !value || Object.keys(value).length === 0
}

window.isSpecial = function(value) {
    return !value || value.slice(0, 1) == '$'
}

let app = new Vue({
    el: '#app',
    data: {
        meta: null,
        basic: null,
        roles: null,
        resources: null,
        view: null,
        role: null,
        roleName: null,
        resource: null,
        resourceName: null
    },
    methods: {
        showMeta: function() {
            this.view = 'meta'
        },
        showTerminal: function() {
            this.view = 'terminal'
        },
        showBasic: function() {
            this.view = 'basic'
        },
        showRole: function(name) {
            this.roleName = name
            this.role = this.roles[name]
            this.view = 'role'
        },
        showResource: function(name) {
            this.resourceName = name
            this.resource = this.resources[name]
            this.view = 'resource'
        }
    },
    created: function() {
        let metaText = document.getElementById('meta').value
        let meta = parseMeta(JSON.parse(metaText))
        this.meta = meta
        this.basic = meta.basic
        this.roles = meta.roles
        this.resources = meta.resources
    },
    mounted: function() {
        this.showBasic()
    },
    directives: {
        marked: {
            bind: function(el, binding) {
                if (binding.value && binding.value != binding.oldValue) {
                    el.innerHTML = marked(binding.value)
                }
            }
        }
    }
})

window.app = app
