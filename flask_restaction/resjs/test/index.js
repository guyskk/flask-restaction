describe('resjs', function() {
    it("test.get", function() {
        return res.test.get({ name: "kk" }).then(function(data) {
            assert.deepEqual(data, {
                'hello': 'kk'
            })
        })
    })
    it("test.post", function() {
        return res.test.post({ name: "kk" }).then(function(data) {
            assert.deepEqual(data, {
                'hello': 'kk'
            })
        })
    })
    it("test.post_name", function() {
        return res.test.post_name({ name: "kk" }).then(function(data) {
            assert.deepEqual(data, {
                'hello': 'kk'
            })
        })
    })
    it("test.put", function() {
        return res.test.put({ name: "kk" }).then(function(data) {
            assert.deepEqual(data, {
                'hello': 'kk'
            })
        })
    })
    it("test.patch", function() {
        return res.test.patch({ name: "kk" }).then(function(data) {
            assert.deepEqual(data, {
                'hello': 'kk'
            })
        })
    })
    it("test.delete", function() {
        return res.test.delete({ name: "kk" }).then(function(data) {
            assert.deepEqual(data, {
                'hello': 'kk'
            })
        })
    })
    it("test.get_302", function() {
        return res.test.get_302().then(function(data) {
            assert.deepEqual(data, {
                'hello': 'world'
            })
        })
    })
    it("test.get_404", function(done) {
        res.test.get_404().catch(function(error) {
            assert.isNotNull(error)
            done()
        })
    })
    it("test.get_403", function(done) {
        res.test.get_403().catch(function(error) {
            assert.isNotNull(error)
            done()
        })
    })
    it("test.get_401", function(done) {
        res.test.get_401().catch(function(error) {
            assert.isNotNull(error)
            done()
        })
    })
    it("test.get_400", function(done) {
        res.test.get_400().catch(function(error) {
            assert.isNotNull(error)
            done()
        })
    })
    it("test.get_500", function(done) {
        res.test.get_500().catch(function(error) {
            assert.isNotNull(error)
            done()
        })
    })
    it("test.get_binary", function(done) {
        res.test.get_binary().then(function(data) {
            assert.isNotNull(data)
            done()
        })
    })

    it("test.post_upload", function(done) {
        res.test.post_upload().then(function(data) {
            assert.isNotNull(data)
            done()
        })
    })
    it("test.post_login", function(done) {
        res.clearToken()
        res.test.post_login({ name: "kk" }).then(function(data) {
            assert.deepEqual(data.name, "kk")
        }).then(function() {
            res.test.get_me().then(function(data) {
                assert.deepEqual(data.name, "kk")
                done()
            })
        })
    })

    it("test.get_me", function(done) {
        res.clearToken()
        res.test.get_me().catch(function(error) {
            assert.isNotNull(error)
            done()
        })
    })
})
