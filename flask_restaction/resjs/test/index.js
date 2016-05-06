var ajax = require('../src/res-ajax');

var q = function(method, url, name) {
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

describe('resjs', function() {
    describe('ajax', function() {
        q('GET');
        q('POST');
        q('PUT');
        q('DELETE');
    });
});
