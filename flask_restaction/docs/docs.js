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
marked('# Marked in browser\n\nRendered by **marked**.');
let app = new Vue({
    el: '#app',
    data: {
        meta: null,
        basic: null,
        roles: null,
        resources: null,
        showRaw: false,
        currentView: null,
        currentRole: null,
        currentRoleName: null,
        currentResource: null,
        currentResourceName: null
    },
    methods: {
        toggleRaw: function() {
            app.showRaw = !app.showRaw
        },
        showBasic: function() {
            app.currentView = 'basic'
        },
        showRole: function(role) {
            app.currentRoleName = role
            app.currentRole = app.roles[role]
            app.currentView = 'roles'
        },
        showResource: function(resource) {
            app.currentResourceName = resource
            app.currentResource = app.resources[resource]
            app.currentView = 'resources'
        }
    },
    created: function() {
        res.ajax('')
            .set('Accept', 'application/json')
            .then(function(response) {
                if (response.status >= 200 && response.status <= 299) {
                    app.meta = response.body
                    let meta = parseMeta(response.body)
                    app.basic = meta.basic
                    app.roles = meta.roles
                    app.resources = meta.resources
                    app.currentView = 'basic'
                } else {
                    app.message = JSON.stringify(response.body) || response.statusText
                }
            })
    },
    directives: {
        marked: {
            bind: function(el, binding) {
                if (binding.value && binding.value != binding.oldValue) {
                    el.innerHTML = marked(binding.value)
                }
            },
            update: function(el, binding) {
                if (binding.value && binding.value != binding.oldValue) {
                    el.innerHTML = marked(binding.value)
                }
            }
        }
    }
})

window.app = app
