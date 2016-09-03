let app = new Vue({
    el: '#app',
    data: {
        meta: null,
        showRaw: false,
        message: 'Hello Vue!'
    },
    methods: {
        toggleRaw: function() {
            app.showRaw = !app.showRaw
        }
    },
    computed: {
        basic: function() {
            if (!app.meta) {
                return null;
            }
            let info = {}
            for (let k of app.meta) {
                if (k.slice(0, 1) == '$' && k != "$roles" && k != "$resources") {
                    info[k.slice(1)] = app.meta[k]
                }
            }
        },
        roles: function() {
            if (!app.meta) {
                return null;
            }
            return app.meta.$roles
        },
        resources: function() {
            if (!app.meta) {
                return null;
            }
            return app.meta.$resources
        },

    },
    created: function() {
        res.ajax('')
            .set('Accept', 'application/json')
            .then(function(response) {
                if (response.status >= 200 && response.status <= 299) {
                    app.meta = response.body
                } else {
                    app.message = JSON.stringify(response.body) || response.statusText
                }
            })
    }
})
module.exports = app
