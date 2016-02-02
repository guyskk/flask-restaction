(function(root) {
    function Promise(promise_fn) {
        var self = {};
        self.value = null;
        self.error = null;
        self.finished = false;
        self.progress = 0;
        self.resolve_callbacks = []
        self.reject_callbacks = []
        self.finish_callbacks = []
        self.progress_callbacks = []
        promise_fn(resolve, reject, doing);

        function resolve(value) {
            if (!self.finished) {
                self.value = value;
                self.finished = true;
                while (self.resolve_callbacks.length > 0) {
                    var fn = self.resolve_callbacks.shift();
                    var ret = fn(value);
                    if (ret != null) {
                        self.value = ret;
                    }
                }
                _finished();
            }
        }

        function reject(error) {
            if (!self.finished) {
                self.error = error;
                self.finished = true;
                while (self.reject_callbacks.length > 0) {
                    var fn = self.reject_callbacks.shift();
                    fn(error);
                }
                _finished();
            }
        }

        function doing(progress) {
            if (!self.finished) {
                self.progress = progress;
                for (var i = 0; i < self.progress_callbacks.length; i++) {
                    var fn = self.progress_callbacks[i];
                    fn(progress);
                }
            }
        }

        function _finished() {
            while (self.finish_callbacks.length > 0) {
                var fn = self.finish_callbacks.shift();
                fn(self.value, self.error);
            }
            self.progress_callbacks = [];
        }
        self.then = function(onFulfilled, onRejected) {
            if (typeof onFulfilled === 'function') {
                if (!self.finished) {
                    self.resolve_callbacks.push(onFulfilled);
                } else {
                    onFulfilled(self.value);
                }
            }
            if (typeof onRejected === 'function') {
                if (!self.finished) {
                    self.reject_callbacks.push(onRejected);
                } else {
                    onRejected(self.error);
                }
            }
            return self;
        }
        self.catch = function(onRejected) {
            return self.then(undefined, onRejected);
        }
        self.done = function(onFinished) {
            if (!self.finished) {
                if (typeof onFinished === 'function') {
                    self.finish_callbacks.push(onFinished)
                }
            } else {
                if (typeof onFinished === 'function') {
                    onFinished(self.value, self.error);
                }
            }
            return self;
        }
        self.doing = function(onProgress) {
            if (!self.finished) {
                if (typeof onProgress === 'function') {
                    self.progress_callbacks.push(onFinished)
                }
            }
            return self;
        }
        return self;
    }

    root._Promise = Promise;
})(res);

