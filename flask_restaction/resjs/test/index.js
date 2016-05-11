var ajax = require('../src/res-ajax');

var testHttpMethod = function(method, url, name) {
    if (!name) {
        name = 'world';
    }
    if (!url) {
        url = '/test';
    }
    it(method + ' ' + url, function(done) {
        ajax('http://127.0.0.1:5000' + url, {
            method: method,
            data: {
                "name": name
            },
            fn: function(err, data) {
                assert.isNull(err);
                assert.deepEqual(data, {
                    'hello': name
                });
                done();
            }
        });
    });
};

function testGetError(code) {
    it('Test ' + code, function(done) {
        ajax('http://127.0.0.1:5000/test/' + code, {
            method: 'GET',
            fn: function(err, data, xhr) {
                assert.isNotNull(err);
                assert.isNull(data);
                assert.equal(xhr.status, code);
                done();
            }
        });
    });
}
describe('resjs', function() {
    describe('ajax', function() {
        testHttpMethod('GET');
        testHttpMethod('POST');
        testHttpMethod('PUT');
        testHttpMethod('DELETE');
        var statusCodes = [400, 401, 403, 404, 500];
        for (var i in statusCodes) {
            testGetError(statusCodes[i]);
        }

        xit('Test ' + 302, function(done) {
            // 302 with CORS is not allowed
            ajax('http://127.0.0.1:5000/test/' + 302, {
                method: 'GET',
                fn: function(err, data, xhr) {
                    assert.isNull(err);
                    assert.isNotNull(data);
                    assert.equal(xhr.status, 200);
                    assert.deepEqual(data, {
                        'hello': 'world'
                    });
                    done();
                }
            });
        });
        it('POST without data to use default param', function(done) {
            ajax('http://127.0.0.1:5000/test/name', {
                method: 'POST',
                fn: function(err, data) {
                    assert.isNull(err);
                    assert.deepEqual(data, {
                        'hello': 'world'
                    });
                    done();
                }
            });
        });
        it('POST without data to dict-like param should 400', function(done) {
            ajax('http://127.0.0.1:5000/test', {
                method: 'POST',
                fn: function(err, data, xhr) {
                    assert.isNotNull(err);
                    assert.equal(xhr.status, 400);
                    done();
                }
            });
        });
        it('GET binary response', function(done) {
            ajax('http://127.0.0.1:5000/test/binary', {
                method: 'GET',
                fn: function(err, data, xhr) {
                    assert.isNull(err);
                    assert.isNotNull(data);
                    assert.equal(xhr.status, 200);
                    done();
                }
            });
        });
        it('Test Auth', function(done) {
            ajax('http://127.0.0.1:5000/test/login', {
                method: 'POST',
                data: {
                    "name": "guyskk"
                },
                fn: function(err, data, xhr) {
                    assert.isNull(err);
                    assert.isNotNull(data);
                    assert.equal(xhr.status, 200);
                    assert.equal(data.name, 'guyskk');
                    var token = xhr.getResponseHeader('Authorization');
                    ajax('http://127.0.0.1:5000/test/me', {
                        method: 'GET',
                        headers: {
                            'Authorization': token
                        },
                        fn: function(err, data, xhr) {
                            assert.isNull(err);
                            assert.isNotNull(data);
                            assert.equal(xhr.status, 200);
                            assert.equal(data.name, 'guyskk');
                            done();
                        }
                    });
                }
            });
        });
    });
});
