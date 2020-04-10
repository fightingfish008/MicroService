var Router = {
    routes: [],
    root: '/',
    config: function (options) {
        this.root = options && options.root ? '/' + this.clearSlashes(options.root) + '/' : '/';
        return this;
    },
    getFragment: function () {
        var fragment = this.clearSlashes(decodeURI(location.pathname + location.search));
        // fragment = fragment.replace(/\?(.*)$/, '');
        fragment = this.root !== '/' ? fragment.replace(this.root, '') : fragment;
        return this.clearSlashes(fragment);
    },
    clearSlashes: function (path) {
        return path.toString().replace(/\/$/, '').replace(/^\//, '');
    },
    add: function (re, handler) {
        if (typeof re === 'function') {
            handler = re;
            re = '';
        }
        this.routes.push({re: re, handler: handler});
        return this;
    },
    remove: function (param) {
        for (var i = 0, r; i < this.routes.length, r = this.routes[i]; i++) {
            if (r.handler === param || r.re.toString() === param.toString()) {
                this.routes.splice(i, 1);
                return this;
            }
        }
        return this;
    },
    flush: function () {
        this.routes = [];
        this.root = '/';
        return this;
    },
    check: function (f) {
        var fragment = f || this.getFragment();
        for (var i = 0; i < this.routes.length; i++) {
            var match = fragment.match(this.routes[i].re);
            if (match) {
                match.shift();
                this.routes[i].handler.apply({}, match);
                return this;
            }
        }
        return this;
    },
    navigate: function (path) {
        path = path ? path : '';
        var current = this.getFragment();
        if (current === this.clearSlashes(path))
            history.replaceState(null, null, this.root + this.clearSlashes(path));
        else {
            history.pushState(null, null, this.root + this.clearSlashes(path));
        }
        return this;
    },
    replace: function (path) {
        path = path ? path : '';
        history.replaceState(null, null, this.root + this.clearSlashes(path));
        return this;
    }
};
window.addEventListener('popstate', function (e) {
    var current = Router.getFragment();
    if (current === '/')
        current = '/home.html#playing';
    Router.check(Router.clearSlashes(current));

});

Router.config();