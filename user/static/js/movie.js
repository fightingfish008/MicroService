let laytpl = layui.laytpl;
let element = layui.element;
let form = layui.form;
let rate = layui.rate;
let flow = layui.flow;
let layer = layui.layer;
$ = layui.jquery;

$.ajaxSetup({
    beforeSend: function (xhr) {
        let token = layui.data('micro').token;
        if (token)
            xhr.setRequestHeader('token', layui.data('micro').token);
    },
    error: function () {
        layer.msg('无法连接到服务器，请稍后重试！')
    }
});
if (location.pathname === '/') {
    if (location.hash === '#upcoming') {
        Router.replace('/home.html#upcoming');
    } else {
        Router.replace('/home.html#playing');
    }
}
if (layui.device().os === 'android' || layui.device().os === 'ios') {
    let input = document.getElementsByTagName('input');
    if (input.scrollIntoView && input.scrollIntoViewIfNeeded) {
        input.scrollIntoView(true);
        input.scrollIntoViewIfNeeded();
    }
}

$(document).on('click', 'a[href]', function (e) {
    e.preventDefault();
    let href = $(this).attr('href');
    if (!(/.+\.html/.test(href))) {
        return
    }
    if (layui.data('micro').token !== undefined && href === '/login.html') {
        return
    }
    Router.navigate(href);
    Router.check();
});
let loadHtml = function (url) {
    let prefix = '/html';
    $("#main").load(prefix + url);
};
//进入页面时检查登录是否过期
(function () {
    let _token = layui.data('micro').token;
    if (_token) {
        $.ajax({
            url: '/api/login',
            method: 'GET',
            headers: {'token': layui.data('micro').token},
            dataType: 'json',
            success: function (resp) {
                if (resp.code !== 0) {
                    layui.data('micro', null);
                    layer.msg(resp.msg);
                }
            }
        });
    }
})();
let Handler = {
    home: function () {
        loadHtml('/home.html');
    },
    search: function () {
        loadHtml('/search.html');
    },
    user: {
        user: function () {
            loadHtml('/user.html');
        },
        order: function () {
            loadHtml('/user/order.html');
        },
        comment: function () {
            loadHtml('/user/comment.html');
        },
        seen: function () {
            loadHtml('/user/seen.html');
        },
        want: function () {
            loadHtml('/user/want.html');
        }
    },
    login: function () {
        loadHtml('/login.html');
    },
    register: function () {
        loadHtml('/register.html');
    },
    forget: function () {
        loadHtml('/forget.html');
    },
    movie: function () {
        loadHtml('/movie.html');
    },
    comment: function () {
        loadHtml('/comment.html');
    },
    schedule: function () {
        loadHtml('/schedule.html');
    },
    seat: function () {
        loadHtml('/seat.html');
    },
    order: function () {
        loadHtml('/order.html');
    }
};
Router.add(/home\.html/, Handler.home)
    .add(/search\.html/, Handler.search)
    .add(/user\.html/, Handler.user.user)
    .add(/user\/order\.html/, Handler.user.order)
    .add(/user\/comment\.html/, Handler.user.comment)
    .add(/user\/seen\.html/, Handler.user.seen)
    .add(/user\/want\.html/, Handler.user.want)
    .add(/login\.html/, Handler.login)
    .add(/register\.html/, Handler.register)
    .add(/forget\.html/, Handler.forget)
    .add(/movie\.html\?movie=(.+)/, Handler.movie)
    .add(/comment\.html\?movie=(.+)/, Handler.comment)
    .add(/schedule\.html\?movie=(.+)/, Handler.schedule)
    .add(/seats\.html\?schedule=(.+)/, Handler.seat)
    .add(/order\.html\?order=(.+)/, Handler.order);

Router.check();


let user_info = function () {
    let _token = layui.data('micro').token;
    if (!_token)
        return null;
    let info = _token.split('.')[1];
    let b = new Base64();
    b = b.decode(info);
    info = JSON.parse(b);
    return info;
};