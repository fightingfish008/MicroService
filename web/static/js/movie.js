layui.use(['carousel', 'element', 'flow', 'rate', 'laytpl', 'form', 'layer', 'mobile'], function () {
    var carousel = layui.carousel;
    var laytpl = layui.laytpl;
    var element = layui.element;
    var form = layui.form;
    var rate = layui.rate;
    var flow = layui.flow;
    var layer = layui.mobile.layer;
    $ = layui.jquery;


    if (location.pathname === '/') {
        if (location.hash === '#upcoming') {
            Router.replace('/home.html#upcoming');
        } else {
            Router.replace('/home.html#playing');
        }
    }
    if (layui.device().os === 'android' || layui.device().os === 'ios') {
        input = document.getElementsByTagName('input');
        if (input.scrollIntoViewIfNeeded && input.scrollIntoView) {
            input.scrollIntoView(true);
            input.scrollIntoViewIfNeeded();
        }
    }
    carousel.render({
        elem: '#poster',
        arrow: 'always',
        width: '100%',
        height: '200px'
    });


    $(document).on('click', 'a[href]', function (e) {
        e.preventDefault();
        href = $(this).attr('href');
        if (!(/.+\.html/.test(href))) {
            return
        }
        if (layui.data('micro').token !== undefined && href === '/login.html') {
            return
        }
        Router.navigate(href);
        Router.check();
    });

    var changeView = function () {
        var path = Router.getFragment();
        path = path.substring(0, path.indexOf('.'));
        var nodes = path.split('/');
        var i, id = '';
        $('*.container[id]').hide();
        $(global.$bottom.find('li')).removeClass('layui-this');
        $('#' + nodes.join('-')).show();
    };


    //检查登录是否过期
    (function () {
        var _token = layui.data('micro').token;
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
                },
                error: function () {
                    layer.msg('无法连接到服务器，请检查后重试！')
                }
            });
        }
    })();

    var global = {
        $bottom: $('.fixed-bottom')
    };
    var Handler = {
        home: function () {
            changeView();
            global.$bottom.show();
            $(global.$bottom.find('li')[0]).addClass('layui-this');
            var hash = location.hash;
            $('.fixed-top li').removeClass('layui-this');
            if (hash === '#upcoming') {
                $('.fixed-top').find('li:last').addClass('layui-this');
                $("#playing").hide();
                $("#upcoming").show();
                $.ajax({
                    url: '/api/movie/upcoming',
                    method: "GET",
                    dataType: 'json',
                    success: function (resp) {
                        if (resp.code === 0) {
                            var upcoming_template = movie_list.innerHTML;
                            var upcoming_view = document.getElementById('upcoming-view');
                            laytpl(upcoming_template).render(resp.data, function (html) {
                                upcoming_view.innerHTML = html;
                            });
                        } else {
                            layer.msg(resp.msg)
                        }
                    },
                    error: function (resp) {
                        layer.msg('无法连接到服务器，请检查后重试！')

                    }
                });
            } else {
                $('.fixed-top').find('li:first').addClass('layui-this');
                $("#playing").show();
                $("#upcoming").hide();
                $.ajax({
                    url: 'http://192.168.2.64:5001/api/movie/playing',
                    method: "GET",
                    dataType: 'json',
                    success: function (resp) {
                        if (resp.code === 0) {
                            var playing_template = movie_list.innerHTML;
                            var view = document.getElementById('playing-view');
                            laytpl(playing_template).render(resp.data, function (html) {
                                view.innerHTML = html;
                            });
                        } else {
                            layer.msg(resp.msg)
                        }
                    },
                    error: function (resp) {
                        layer.msg('无法连接到服务器，请检查后重试！')

                    }
                });
            }
        },
        search: function () {
            changeView();
            global.$bottom.show();
            $(global.$bottom.find('li')[1]).addClass('layui-this');
            flow.load({
                elem: '#hotest-comments-list' //指定列表容器
                , isAuto: false
                , done: function (page, next) { //到达临界点（默认滚动触发），触发下一页
                    $.get('/api/comments/newest?page=' + page, function (res) {
                        if (res.code === 0) {
                            var movie_comment_tpl = search_comment_tpl.innerHTML;
                            laytpl(movie_comment_tpl).render(res.data, function (html) {
                                next(html, page < 1);
                            });
                        }
                    });
                }
            });

            $('#search-button').off('click').on('click', function () {
                var $input = $('#search-input');
                if ($input.is(':hidden')) {
                    $('#search-title').hide();
                    $input.show();
                    $input.focus();
                } else {
                    var key = $input.val();
                    if (key === '' || key === undefined) {
                        $input.hide();
                        $('#search-title').show();
                    } else {
                        console.log('search:' + key);
                        $('#search-comments').hide();
                        $('#search-movies').show();
                        $.ajax({
                            url: '/api/search?key=' + key,
                            method: "GET",
                            success: function (resp) {
                                if (resp.code === 0) {
                                    if (resp.data.length === 0) {
                                        layer.msg('未搜索到包含该关键字的电影');
                                        return;
                                    }
                                    var upcoming_template = movie_list.innerHTML;
                                    var upcoming_view = document.getElementById('search-movies');
                                    laytpl(upcoming_template).render(resp.data, function (html) {
                                        upcoming_view.innerHTML = html;
                                    });
                                } else {
                                    layer.msg(resp.msg)
                                }
                            },
                            error: function (resp) {
                                layer.msg('无法连接到服务器，请检查后重试！')

                            }
                        })
                    }
                }
            });

        },
        user: {
            user: function () {
                changeView();
                $('#user-page').show();
                global.$bottom.show();
                $(global.$bottom.find('li')[2]).addClass('layui-this');

                info = user_info();
                if (info) {
                    $('#user_nick').text(info.nickname);
                    $('#logout').show();
                } else {
                    $('#logout').hide();
                }
            },
            order: function () {
                changeView();
                $('#user-order').show();
                global.$bottom.hide();

                function load_order() {
                    $.ajax({
                        url: '/api/user/order',
                        method: 'GET',
                        headers: {'token': layui.data('micro').token},
                        dataType: 'json',
                        success: function (resp) {
                            if (resp.code === 0) {
                                var template = user_orders_tpl.innerHTML;
                                var view = document.getElementById('user_orders');
                                laytpl(template).render(resp.data, function (html) {
                                    view.innerHTML = html;
                                });
                            } else {
                                layer.msg(resp.msg)
                            }
                        },
                        error: function () {
                            layer.msg('无法连接到服务器，请检查后重试！')
                        }
                    });
                }

                load_order();
                $(document).off('click').on('click', 'span.cancel_order', function (e) {
                    var oid = $(this).data('oid');
                    layer.open({
                        content: '确定取消该订单吗？',
                        btn: ['确定', '我再想想'] //按钮
                        , yes: function (index) {
                            $.ajax({
                                url: '/api/order/cancel',
                                headers: {'token': layui.data('micro').token},
                                method: 'POST',
                                data: {'oid': oid},
                                success: function (resp) {
                                    if (resp.code === 0) {
                                        layer.msg(resp.msg, {"code": 1});
                                        load_order();
                                    } else {
                                        layer.msg(resp.msg, {"code": 2})
                                    }
                                }
                            })
                        }
                    });
                    return false;
                });
                $(document).on('click', 'button.user_order_unsubscribe', function (e) {
                    var oid = $(this).data('oid');
                    layer.open({
                        content: '确定退订该订单吗？',
                        btn: ['确定', '我再想想'] //按钮
                        , yes: function (index) {
                            $.ajax({
                                url: '/api/order/cancel',
                                headers: {'token': layui.data('micro').token},
                                method: 'POST',
                                data: {'oid': oid},
                                success: function (resp) {
                                    if (resp.code === 0) {
                                        layer.msg(resp.msg, {"code": 1});
                                        load_order();
                                    } else {
                                        layer.msg(resp.msg, {"code": 2})
                                    }
                                }
                            })
                        }
                    });
                    return false;
                });
                $(document).on('click', 'button.user_order_pay', function (e) {
                    var oid = $(this).data('oid');
                    layer.open({
                        content: '确定支付该订单吗？',
                        btn: ['确定', '我再想想'],//按钮
                        yes: function (index) {
                            $.ajax({
                                url: '/api/order/pay',
                                headers: {'token': layui.data('micro').token},
                                method: 'POST',
                                data: {'oid': oid},
                                success: function (resp) {
                                    if (resp.code === 0) {
                                        layer.msg(resp.msg, {"code": 1});
                                        load_order();
                                    } else {
                                        layer.msg(resp.msg, {"code": 2})
                                    }
                                }
                            })
                        }
                    });
                    return false;
                });
            },
            comment: function () {
                changeView();
                $('#user-comment').show();
                global.$bottom.hide();
                flow.load({
                    elem: '#user_comments' //指定列表容器
                    , isAuto: false
                    , done: function (page, next) { //到达临界点（默认滚动触发），触发下一页
                        $.ajax({
                            url: '/api/user/comments?page=' + page,
                            method: 'GET',
                            headers: {'token': layui.data('micro').token},
                            dataType: 'json',
                            success: function (resp) {
                                if (resp.code === 0) {
                                    var movie_comment_tpl = comment_tpl.innerHTML;
                                    laytpl(movie_comment_tpl).render(resp.data, function (html) {
                                        next(html, page < 1);
                                    });
                                }
                            }
                        });
                    }
                });
            },
            seen: function () {
                changeView();
                $('#user-seen').show();
                global.$bottom.hide();
                $.ajax({
                    url: '/api/user/seen',
                    method: 'GET',
                    headers: {'token': layui.data('micro').token},
                    dataType: 'json',
                    success: function (resp) {
                        if (resp.code === 0) {
                            var template = movie_seen_tpl.innerHTML;
                            var view = document.getElementById('user_seen_movies');
                            laytpl(template).render(resp.data, function (html) {
                                view.innerHTML = html;
                            });
                        } else {
                            layer.msg(resp.msg)
                        }
                    },
                    error: function () {
                        layer.msg('无法连接到服务器，请检查后重试！')
                    }
                });
                $(document).off('click').on('click', '.user_seen_comment', function (e) {
                    var href = $(this).data('href');
                    Router.navigate(href);
                    Router.check();
                    return false;
                })
            },
            want: function () {
                changeView();
                $('#user-want').show();
                global.$bottom.hide();
                $.ajax({
                    url: '/api/user/want',
                    method: 'GET',
                    headers: {'token': layui.data('micro').token},
                    dataType: 'json',
                    success: function (resp) {
                        if (resp.code === 0) {
                            var template = movie_want_tpl.innerHTML;
                            var view = document.getElementById('user_want_movies');
                            laytpl(template).render(resp.data, function (html) {
                                view.innerHTML = html;
                            });
                        } else {
                            layer.msg(resp.msg)
                        }
                    },
                    error: function (resp) {
                        layer.msg('无法连接到服务器，请检查后重试！')
                    }
                });
            }
        },
        login: function () {
            changeView();
            global.$bottom.hide();
        },
        register: function () {
            changeView();
            global.$bottom.hide();
        },
        forget: function () {
            changeView();
            global.$bottom.hide();
        },
        movie: function (movie) {
            changeView();
            $('#movie-comments-list').html('');
            $('#movie').on('click', '.movie-info-description', function (e) {
                    var $p = $(this).find('p');
                    var overflow = $p.css('overflow');
                    if (overflow === 'hidden') {
                        $p.css('overflow', 'auto');
                        $p.css('max-height', 'none');
                        $(this).find('i').html('&#xe619;')
                    } else {
                        $p.css('overflow', 'hidden');
                        $p.css('max-height', '80px');
                        $(this).find('i').html('&#xe61a;')
                    }
                }
            );
            $.ajax({
                url: '/api/movie',
                method: 'GET',
                data: {'mid': movie},
                success: function (resp) {
                    if (resp.code === 0) {
                        var movie_info_tpl = $('#movie_info_tpl').html();
                        var movie_info_view = document.getElementById('movie-info');
                        laytpl(movie_info_tpl).render(resp.data, function (html) {
                            movie_info_view.innerHTML = html;
                        });
                        $('#write-comment').prop('href', '/comment.html?movie=' + resp.data.id);
                        if (resp.data.status === 2) {
                            $('#movie-buy').show();
                            $('#movie-buy').prop('href', '/schedule.html?movie=' + resp.data.id)
                        } else if (resp.data.status === 3)
                            $('#movie-buy').hide();
                    } else {
                        layer.msg(resp.msg)
                    }
                    $.ajax({
                        url: '/api/user/want',
                        method: 'GET',
                        headers: {token: layui.data('micro').token},
                        data: {'mid': movie},
                        success: function (resp) {
                            if (resp.code === 0) {
                                $('button[data-want_mid]').addClass('wanted');
                                $('button[data-want_mid]').text('已想看');
                            } else {
                                $('button[data-want_mid]').removeClass('wanted');
                                $('button[data-want_mid]').text('想看');
                            }
                        }
                    });
                    $.ajax({
                        url: '/api/user/comment',
                        method: "GET",
                        headers: {token: layui.data('micro').token},
                        data: {'mid': movie},
                        success: function (resp) {
                            if (resp.code === 0) {
                                $('#write-comment').text('我的短评');
                                $('#movie_score').text(resp.data.score + '分  评分');
                            } else {
                                $('#write-comment').text('写短评');
                                $('#movie_score').text('评分');
                            }
                        }
                    });
                    //加载评论
                    flow.load({
                        elem: '#movie-comments-list' //指定列表容器
                        , isAuto: true
                        , done: function (page, next) { //到达临界点（默认滚动触发），触发下一页
                            $.get('/api/movie/comment?mid=' + movie + '&page=' + page, function (res) {
                                if (res.code === 0) {
                                    var template = comment_tpl.innerHTML;
                                    laytpl(template).render(res.data, function (html) {
                                        next(html, page < res.page);
                                    });
                                }
                            });
                        }
                    });
                },
                error: function () {
                    layer.msg('无法连接到服务器，请检查后重试！')
                }
            });

            //点赞||取消点赞
            $(document).off('click').on('click', '.support', function () {
                var that = this;
                $.ajax({
                    url: '/api/comment/support',
                    method: 'POST',
                    data: {'cid': $(this).data('cid')},
                    headers: {'token': layui.data('micro').token},
                    success: function (resp) {
                        if (resp.code === 0) {
                            layer.msg(resp.msg);
                            if (resp.msg === '点赞成功') {
                                $(that).find('i').css("color", "red");
                                $(that).find('span').text(parseInt($(that).find('span').text()) + 1)
                            } else {
                                $(that).find('i').css("color", "black");
                                $(that).find('span').text(parseInt($(that).find('span').text()) - 1)
                            }
                        } else {
                            layer.msg(resp.msg)
                        }
                    }, error: function () {
                        layer.msg('无法连接到服务器，请检查后重试！')

                    }
                })
            });
            //添加到想看
            $(document).on('click', 'button[data-want_mid]', function (e) {
                var mid = $(this).data('want_mid');
                var that = this;
                $.ajax({
                    url: '/api/user/want',
                    method: "POST",
                    data: {'mid': mid},
                    headers: {token: layui.data('micro').token},
                    success: function (resp) {
                        if (resp.code === 0) {
                            layer.msg(resp.msg);
                            if ($(that).hasClass('wanted')) {
                                $(that).removeClass('wanted');
                                $(that).text('想看');
                            } else {
                                $(that).addClass('wanted');
                                $(that).text('已想看');
                            }
                        } else {
                            layer.msg(resp.msg)
                        }
                    },
                    error: function (resp) {
                        layer.msg('无法连接到服务器，请检查后重试！')

                    }
                });

            });
            global.$bottom.hide();
        },
        comment: function (movie) {
            changeView();
            rate.render({
                elem: '#comment-rate',
                value: 3,
                half: true,
                setText: function (value) {
                    var arrs = {
                        '1': '超烂啊',
                        '2': '比较差',
                        '3': '一般般',
                        '4': '比较好',
                        '5': '完美'
                    };
                    $('#comment-score>div:first>span:first').text(value * 2);
                    $('#comment-score>div:last>span:first').text(arrs[value]);
                }
            });
            $.ajax({
                url: '/api/user/comment?mid=' + movie,
                method: "GET",
                headers: {token: layui.data('micro').token},
                success: function (resp) {
                    if (resp.code === 0) {
                        rate.render({
                            elem: '#comment-rate',
                            value: parseInt(resp.data.score) / 2,
                            half: true,
                            setText: function (value) {
                                var arrs = {
                                    '1': '超烂啊',
                                    '2': '比较差',
                                    '3': '一般般',
                                    '4': '比较好',
                                    '5': '完美'
                                };
                                $('#comment-score>div:first>span:first').text(value * 2);
                                $('#comment-score>div:last>span:first').text(arrs[value]);
                            }
                        });
                        $('#comment-content').val(resp.data.content);
                    } else {
                        rate.render({
                            elem: '#comment-rate',
                            value: 3,
                            half: true,
                            setText: function (value) {
                                var arrs = {
                                    '1': '超烂啊',
                                    '2': '比较差',
                                    '3': '一般般',
                                    '4': '比较好',
                                    '5': '完美'
                                };
                                $('#comment-score>div:first>span:first').text(value * 2);
                                $('#comment-score>div:last>span:first').text(arrs[value]);
                            }
                        });
                        $('#comment-content').val('');
                    }
                }
            });

            $('#add-comment').off('click').on('click', function (e) {
                $.ajax({
                    url: '/api/user/comment',
                    headers: {token: layui.data('micro').token},
                    data: {
                        'mid': movie,
                        'content': $('#comment-content').val(),
                        'score': $('#comment-rate-score').text()
                    },
                    method: 'POST',
                    success: function (resp) {
                        if (resp.code === 0) {
                            layer.msg(resp.msg);
                            history.back();
                        } else
                            layer.msg(resp.msg)
                    }, error: function (resp) {
                        layer.msg('无法连接到服务器，请检查后重试！')
                    }
                })
            });
            global.$bottom.hide();
        },
        schedule: function (movie) {
            changeView();
            $.ajax({
                url: '/api/schedule?mid=' + movie,
                method: 'GET',
                success: function (resp) {
                    if (resp.code === 0) {
                        var schedule_tpl = $('#schedule_tpl').html();
                        var schedule_content = document.getElementById('schedule-content');
                        laytpl(schedule_tpl).render(resp.data, function (html) {
                            schedule_content.innerHTML = html;
                        });

                    } else {
                        layer.msg(resp.msg)
                    }
                },
                error: function (resp) {
                    layer.msg('无法连接到服务器，请检查后重试！')
                }
            });
            element.on('tab(schedule-date)', function (data) {
                console.log(data.index);
                $('#schedule-date-0').hide();
                $('#schedule-date-1').hide();
                $('#schedule-date-2').hide();
                $('#schedule-date-' + data.index).show();

            });
            global.$bottom.hide();
        },
        seat: function (schedule) {
            changeView();
            $('.seats-selected').html('');
            $.ajax({
                url: '/api/schedule?sid=' + schedule,
                method: 'GET',
                success: function (resp) {
                    if (resp.code === 0) {
                        var seats_tpl = $('#seats_tpl').html();
                        var seats_view = document.getElementById('seats-view');
                        laytpl(seats_tpl).render(resp.data, function (html) {
                            seats_view.innerHTML = html;
                        });
                        $.ajax({
                            url: '/api/schedule/seats',
                            data: {'sid': schedule},
                            method: "GET",
                            success: function (resp) {
                                if (resp.code === 0) {
                                    $.each(resp.data, function (index, value) {
                                        var $disable = $('.seats-seat').find('i[data-value="' + value + '"]');
                                        $disable.removeClass('seats-seat-enable');
                                        $disable.addClass('seats-seat-disable');
                                    });
                                }
                            }
                        })
                    } else {
                        layer.msg(resp.msg)
                    }
                },
                error: function (resp) {
                    layer.msg('无法连接到服务器，请检查后重试！')
                }
            });
            $(document).off('click').on('click', '.seats-seat-enable', function (e) {
                if ($('.seats-selected').find('span').length < 4) {
                    $(this).removeClass('seats-seat-enable');
                    $(this).addClass('seats-seat-selected');
                    var seat = $(this).data('value');
                    var position = seat.split(':');
                    var item = '<span data-value="' + seat + '">' + position[0] + '排' + position[1] + '座</span> ';
                    $('.seats-selected').append(item);
                    update_total();
                } else {
                    layer.msg('已达最大购票数')
                }

            });
            $(document).on('click', '.seats-seat-selected', function (e) {
                var seat = $(this).data('value');
                if ($('.seats-selected').find('span[data-value="' + seat + '"]')) {
                    $(this).addClass('seats-seat-enable');
                    $(this).removeClass('seats-seat-selected');
                    $('.seats-selected').find('span[data-value="' + seat + '"]').remove();
                    update_total();
                }
            });
            $(document).on('click', '.seats-selected>span', function (e) {
                var $seat = $('i.seats-seat-selected[data-value="' + $(this).data('value') + '"]');
                $seat.addClass('seats-seat-enable');
                $seat.removeClass('seats-seat-selected');
                $(this).remove();
                update_total();
            });
            var update_total = function () {
                var count = $('.seats-selected').find('span').length;
                var price = parseFloat($('#seats-price').text());
                $('#seats-total').text(price * count);
                $('#seats-selected-count').text(count);

            };
            $(document).on('click', '#seats-buy', function (e) {
                var seats = [];
                $('.seats-selected').find('span').each(function (index, item) {
                    seats.push($(item).data('value'));
                });
                if (seats.length === 0) {
                    layer.msg('请选择座位');
                    return
                }
                seats = seats.join(',');
                $.ajax({
                    url: '/api/order',
                    method: 'POST',
                    headers: {'token': layui.data('micro').token},
                    data: {'sid': schedule, 'seats': seats, 'total': $('#seats-total').text()},
                    success: function (resp) {
                        if (resp.code === 0) {
                            layer.msg(resp.msg);
                            var href = '/order.html?order=' + resp.oid;
                            Router.navigate(href);
                            Router.check();
                        } else {
                            layer.msg(resp.msg)
                        }
                    }
                });
            });
            global.$bottom.hide();
        },
        order: function (order) {
            changeView();

            function fresh() {
                $.ajax({
                    url: '/api/order?oid=' + order,
                    method: 'GET',
                    data: {},
                    headers: {'token': layui.data('micro').token},
                    success: function (resp) {
                        if (resp.code === 0) {
                            var order_tpl = $('#order_tpl').html();
                            var order_view = document.getElementById('order-view');
                            laytpl(order_tpl).render(resp.data, function (html) {
                                order_view.innerHTML = html;
                            });
                        } else
                            layer.msg(resp.msg)
                    }
                });
            }

            fresh();
            $(document).off('click').on('click', '#order_pay', function (e) {
                layer.open({
                    content: '确定支付该订单吗？',
                    btn: ['确定', '我再想想'],//按钮
                    yes: function (index) {
                        $.ajax({
                            url: '/api/order/pay',
                            method: 'POST',
                            headers: {'token': layui.data('micro').token},
                            data: {'oid': order},
                            success: function (resp) {
                                if (resp.code === 0) {
                                    layer.msg(resp.msg);
                                    fresh();
                                } else {
                                    layer.msg(resp.msg);
                                }
                            }
                        })
                    }
                });
            });
            $(document).on('click', '#order_cancel', function (e) {
                $.ajax({
                    url: '/api/order/cancel',
                    method: 'POST',
                    headers: {'token': layui.data('micro').token},
                    data: {'oid': order},
                    success: function (resp) {
                        if (resp.code === 0) {
                            layer.msg(resp.msg);
                            fresh();
                        } else {
                            layer.msg(resp.msg);
                        }
                    }
                })
            });
            global.$bottom.hide();
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

    $('#logout').on('click', function () {
        layer.open({
            content: '确定退出登录吗？',
            btn: ['我要退出', '我在想想'] //按钮
            , yes: function (index) {
                $('#logout').hide();
                $('#user_nick').text('立即登录');
                layui.data('micro', {
                    key: 'token', remove: true
                });
                layer.msg('退出成功！', {icon: 1});
                layer.close(index);
            }
        });
    });

    form.on('submit(login)', function (data) {
        $.ajax({
            url: '/api/login',
            method: 'POST',
            data: data.field,
            dataType: 'json',
            success: function (resp, status, xhr) {
                if (resp.code === 0) {
                    if (layui.data('micro').token === undefined) {
                        layui.data('micro', {
                            key: 'token',
                            value: resp.token
                        });
                    }
                    Router.navigate('/user.html');
                    Router.check();
                    layer.msg(resp.msg);
                } else {
                    layer.msg(resp.msg);
                }
            },
            error: function (resp) {
                layer.msg('无法连接到服务器，请检查后重试！')
            }
        });
        return false; //阻止表单跳转。如果需要表单跳转，去掉这段即可。
    });

    form.on('submit(register)', function (data) {
        $.ajax({
            url: '/api/register',
            method: 'POST',
            data: data.field,
            dataType: 'json',
            success: function (resp) {
                console.log(resp);
                if (resp.code === 0) {
                    Router.navigate('/login.html');
                    Router.check();
                    layer.msg(resp.msg + ",请登陆！");
                }
                else {
                    layer.msg(resp.msg);
                }
            },
            error: function (resp) {
                layer.msg('无法连接到服务器，请检查后重试！')
            }
        });
        return false; //阻止表单跳转。如果需要表单跳转，去掉这段即可。
    });

    // $('button.want').on('click', function (e) {
    //     // Router.navigate('/movie.html?mid=' + $(this).data('id'));
    //     // Router.check()
    // }, false);
    //
    // $('button.buy').on('click', function (e) {
    //     Router.navigate('/wxs.html?mid=' + $(this).data('id'));
    //     Router.check();
    //     e.stopPropagation();
    // }, true);
});

var user_info = function () {
    var _token = layui.data('micro').token;
    if (!_token)
        return null;
    var info = _token.split('.')[1];
    b = new Base64();
    b = b.decode(info);
    info = JSON.parse(b);
    return info;
};