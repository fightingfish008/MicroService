import datetime
import random
from functools import wraps

import jwt
from flask import request, jsonify

import config
import main
from app.user import user as app


def identify(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            token = request.headers['token']
        except Exception as e:
            return jsonify({'code': -11, 'msg': '未登录，请登录后重试！'})
        info = decode_auth_token(token)
        if not isinstance(info, dict):
            return jsonify({'code': -11, 'msg': info})
        else:
            setattr(request, 'token', info)
        return func(*args, **kwargs)

    return wrapper


def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, config.SECRET_KEY, options={'verify_exp': True})
        return payload
    except jwt.ExpiredSignatureError:
        return 'Token过期'
    except jwt.InvalidTokenError:
        return '无效Token'


@app.route('/register', methods=["POST"])
def register():
    data = {
        'phone': request.form.get('phone', None),
        'nickname': request.form.get('nickname', None),
        'password': request.form.get('password', None),
        'status': 1,
        'ctime': str(datetime.datetime.now())[:19],
        'last_login': 0
    }
    result = main.rpc.user.register(data)
    return jsonify(result)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        phone = request.form.get("phone", None)
        passwd = request.form.get("password", None)
        result = main.rpc.user.login(phone, passwd)
        return jsonify(result)
    else:
        try:
            token = request.headers['token']
        except Exception as e:
            return jsonify({'code': -11, 'msg': '未登录，请登录后重试！'})
        info = decode_auth_token(token)
        if not isinstance(info, dict):
            return jsonify({'code': -11, 'msg': info})
        else:
            return jsonify({'code': 0, 'msg': ''})  # token 可用


@app.route('/search')
def search():
    search = request.args.get('key', '')
    result = main.rpc.movie.search_movie(search)
    return jsonify(result)


@app.route('/movie')
def movie():
    skip = request.args.get('skip', 0)
    limit = request.args.get("limit", 20)
    mid = request.args.get('mid', None)
    skip = int(skip)
    limit = int(limit)
    if mid:
        result = main.rpc.movie.get_movie(mid)
    else:
        result = main.rpc.movie.get_movies(1, skip, limit)
    return jsonify(result)


@app.route('/movie/playing')
def movie_playing():
    skip = request.args.get('skip', 0)
    limit = request.args.get("limit", 20)
    result = main.rpc.movie.get_movies(2, skip, limit)
    seen = random.randint(0, 10)
    for _ in result['data']:
        _['seen'] = seen
    return jsonify(result)


@app.route('/movie/upcoming')
def movie_upcoming():
    skip = request.args.get('skip', 0)
    limit = request.args.get("limit", 20)
    result = main.rpc.movie.get_movies(3, skip, limit)
    return jsonify(result)


@app.route('/movie/comment')
def movie_comment():
    page = request.args.get('page', 1)
    limit = request.args.get("limit", 20)
    mid = request.args.get('mid', None)
    limit = int(limit)
    skip = (int(page) - 1) * limit
    result = main.rpc.comment.get_comments_by_movie(mid, skip, limit)
    return jsonify(result)


@app.route('/comment/support', methods=['GET', 'POST'])
@identify
def comment_support():
    if request.method == 'POST':
        uid = request.token['uid']
        cid = request.form.get('cid', None)
        result = main.rpc.comment.support(uid, cid)
        return jsonify(result)
    else:
        uid = request.token['uid']
        cid = request.args.get('cid', None)
        result = main.rpc.comment.support(uid, cid)
        return jsonify(result)


@app.route('/comments/newest')
def comments_newest():
    page = request.args.get("page", 1)
    limit = request.args.get("limit", 20)
    limit = int(limit)
    skip = (int(page) - 1) * limit
    result = main.rpc.comment.get_newest(skip, limit)
    return jsonify(result)


@app.route('/order/pay', methods=["POST"])
@identify
def order_pay():
    oid = request.form.get('oid', None)
    result = main.rpc.order.update_order(oid)
    return jsonify(result)


@app.route('/order/cancel', methods=["POST"])
@identify
def order_cancel():
    oid = request.form.get('oid', None)
    result = main.rpc.order.cancel_order(oid)
    return jsonify(result)


@app.route('/order', methods=["GET", "POST"])
@identify
def order():
    if request.method == 'GET':
        uid = request.token['uid']
        oid = request.args.get('oid', None)
        if oid:
            result = main.rpc.order.get_order(oid, uid)
            return jsonify(result)
        else:
            result = main.rpc.order.get_orders(uid)
            return jsonify(result)
    else:
        sid = request.form.get('sid', None)
        _seats = request.form.get('seats', None)
        total = request.form.get('total', None)
        if total and sid and _seats:
            total = float(total)
            seats = _seats.split(',')
        else:
            return jsonify({'code': -1, "msg": "数据异常"})
        schedule = main.rpc.schedule.get_schedule(sid)
        if schedule['code'] != 0:
            return jsonify(schedule)
        order = {
            'uid': request.token['uid'],
            'schedule': schedule['data'],
            'total': total,
            'seats': seats,
            'ctime': str(datetime.datetime.now())[:19],
            'status': 0  # 0:待付款，1:已付款，2：已完成，3：已取消，4：已退订
        }
        result = main.rpc.order.add_order(order)
        return jsonify(result)


@app.route('/schedule', methods=["GET"])
def schedule():
    mid = request.args.get('mid', None)
    sid = request.args.get('sid', None)
    if sid:
        result = main.rpc.schedule.get_schedule(sid)
    else:
        result = main.rpc.schedule.get_schedules_mid(mid)
        if not result.get('movie', None):
            movie = main.rpc.movie.get_movie(mid)
            if movie['code'] == 0:
                result['data']['movie'] = movie['data']
    return jsonify(result)


@app.route('/schedule/seats', methods=["GET"])
def schedule_seats():
    sid = request.args.get('sid', None)
    result = main.rpc.order.get_sold_seats(sid)
    return jsonify(result)


@app.route('/user/order', methods=["GET", "DELETE"])
@identify
def user_order():
    if request.method == 'GET':
        uid = request.token['uid']
        result = main.rpc.order.get_orders(uid)
        return jsonify(result)
    else:
        pass


@app.route('/user/seen', methods=["GET"])
@identify
def user_seen():
    uid = request.token['uid']
    result = main.rpc.order.get_seen(uid)
    return jsonify(result)


@app.route('/user/want', methods=["GET", "POST"])
@identify
def user_want():
    if request.method == "GET":
        uid = request.token['uid']
        mid = request.args.get('mid', None)
        if mid:
            result = main.rpc.user.get_want_by_mid(uid, mid)
        else:
            result = main.rpc.user.get_want_by_user(uid)
        return jsonify(result)
    else:
        mid = request.form.get('mid', None)
        if mid:
            movie = main.rpc.movie.get_movie(mid)
        else:
            return jsonify({"code": -1, "msg": "mid不能为空"})
        if movie['code'] == 0:
            want = {
                'uid': request.token['uid'],
                'movie': movie['data'],
                'ctime': str(datetime.datetime.now())[:19]
            }
            result = main.rpc.user.add_or_del_want(want)
            return jsonify(result)
        else:
            return jsonify({"code": -1, "msg": "mid不存在"})


@app.route('/user/comment', methods=["GET", "POST"])
@identify
def user_comment():
    if request.method == 'GET':
        uid = request.token['uid']
        mid = request.args.get('mid', None)
        if mid:
            result = main.rpc.comment.get_comment(uid, mid)
        else:
            result = main.rpc.comment.get_comments_by_user(uid)
        return jsonify(result)
    else:
        mid = request.form.get('mid', None)
        uid = request.token['uid']
        user = main.rpc.user.get_user(uid)
        movie = main.rpc.movie.get_movie(mid)
        content = request.form.get('content', None)
        if not content:
            result = main.rpc.comment.del_comment(uid, mid)
            return jsonify(result)
        if movie['code'] == 0:
            comment = {
                'movie': {
                    'id': movie['data']['id'],
                    'name': movie['data']['name'],
                    'cover': movie['data']['cover']
                },
                'user': user,
                'content': content,
                'score': request.form.get('score', 6),
            }
            result = main.rpc.comment.add_comment(comment)
        else:
            result = {'code': -1, 'msg': movie['msg']}
        return jsonify(result)


@app.route('/user/comments')
@identify
def user_comments():
    uid = request.token['uid']
    result = main.rpc.comment.get_comments_by_user(uid)
    return jsonify(result)
