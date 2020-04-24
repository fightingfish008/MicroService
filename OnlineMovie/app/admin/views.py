import datetime
from functools import wraps

from flask import request, jsonify, session

import main  # from main import rpc # error
from app.admin import admin as app
from utils.fastdfs.fdfs_storage import save

bucket_url = 'micro-1252672422.file.myqcloud.com'


# 登录、注册认证函数
def authorize(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = session.get('login', None)
        if user:
            return func(*args, **kwargs)
        else:
            return jsonify({'code': -1, 'msg': "未登录"})

    return wrapper


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        result = main.rpc.admin.login(username, password)
        if result['code'] == 0:
            session['login'] = result['data']
        return jsonify(result)
    else:
        user = session.get('login', None)
        if user:
            return jsonify({'code': 0, 'msg': "", 'data': user})
        else:
            return jsonify({'code': -1, 'msg': "未登录"})


@app.route('/movie', methods=['GET', 'POST', 'DELETE', 'PUT'])
@app.route('/movie/<mid>', methods=['GET', 'DELETE', 'PUT'])
# @authorize
def movie(mid=None):
    if request.method == 'GET':
        if mid:
            result = main.rpc.movie.get_movie(mid)
            return jsonify(result)
        else:
            page = request.args.get('page', None)
            limit = request.args.get('limit', None)
            if page and limit:
                limit = int(limit)
                skip = (int(page) - 1) * limit
                result = main.rpc.movie.get_movies(None, skip, limit)
            else:
                result = main.rpc.movie.get_movies(None)
            return jsonify(result)
    elif request.method == 'POST':
        cover = request.files.get('cover', None)
        _tags = request.form.get('tags', None)
        tags = []
        if _tags:
            _tags = _tags.replace(',', '，')
            tags = _tags.split('，')
        movie = {
            'name': request.form.get('name', None),
            'cover': '',
            'showtime': request.form.get('showtime', ''),
            'duration': request.form.get('duration', ''),
            'director': request.form.get('director', ''),
            'players': request.form.get('players', ''),
            'country': request.form.get('country', ''),
            'description': request.form.get('description', ''),
            'type': request.form.get('type', '2D'),
            'score': request.form.get('score', '-'),
            'ctime': str(datetime.datetime.now())[:19],
            'tags': tags,
            'status': request.form.get('status', 0)  # 0:不可用，1：已下映，2：正在热播，3：未上映
        }
        movie['status'] = int(movie['status'])
        result = main.rpc.movie.add_movie(movie)
        _id = result['id']
        # upload_tencent(file, file_name, dir='cover'):
        # res = upload_tencent(cover, _id + '.png')
        buff = request.files['cover'].read()
        res = save(buff)
        r = main.rpc.movie.update_movie(_id, {'cover': res['Remote file_id']})
        return jsonify(r)
    elif request.method == 'DELETE':
        _mids = request.form.get('ids', None)
        if not _mids:
            result = {'code': -1, "msg": "ids不能为空"}
            return jsonify(result)
        mids = _mids.split(',')
        result = main.rpc.movie.del_movie(mids)
        return jsonify(result)
    elif request.method == 'PUT':
        if mid:
            _tags = request.form.get('tags', None)
            tags = []
            if _tags:
                _tags = _tags.replace(',', '，')
                tags = _tags.split('，')
            movie = {
                'name': request.form.get('name', None),
                'showtime': request.form.get('showtime', None),
                'duration': request.form.get('duration', None),
                'director': request.form.get('director', None),
                'players': request.form.get('players', None),
                'country': request.form.get('country', None),
                'description': request.form.get('description', None),
                'type': request.form.get('type', None),
                # 'rating': request.form.get('rating', None),
                'tags': tags,
                'status': request.form.get('status', None)
            }

            movie = {k: v for k, v in movie.items() if v}
            if hasattr(movie, 'status'):
                movie['status'] = int(movie['status'])
            result = main.rpc.movie.update_movie(mid, movie)
            return jsonify(result)
        else:
            _mids = request.form.get('ids', None)
            if not _mids:
                result = {'code': -1, "msg": "ids不能为空"}
                return jsonify(result)
            mids = _mids.split(',')
            status = request.form.get('status', 0)
            status = int(status) if status != None else status
            result = main.rpc.movie.update_status(mids, status)
            return jsonify(result)


@app.route('/schedule', methods=['GET', 'POST', 'DELETE', 'PUT'])
@app.route('/schedule/<sid>', methods=['GET', 'DELETE', 'PUT'])
# @authorize
def schedule(sid=None):
    if request.method == 'GET':
        if sid:
            result = main.rpc.schedule.get_schedule(sid)
            return jsonify(result)
        else:
            page = request.args.get('page', None)
            limit = request.args.get('limit', None)
            if page and limit:
                limit = int(limit)
                skip = (int(page) - 1) * limit
                result = main.rpc.schedule.get_schedules(skip, limit)
            else:
                result = main.rpc.schedule.get_schedules()
            return jsonify(result)
    elif request.method == 'POST':  # 添加
        rid = request.form.get('room', None)
        mid = request.form.get('movie', None)
        schedule = {
            'room': main.rpc.room.get_room(rid)['data'],
            'movie': main.rpc.movie.get_movie(mid)['data'],
            'start_time': request.form.get('start_time', None),
            'end_time': request.form.get('end_time', None),
            'price': request.form.get('price', None),
            'date': request.form.get('date', None),
            'ctime': str(datetime.datetime.now())[:19],
            'status': request.form.get('status', None)  # 1: 启用 ，0：禁用
        }
        schedule['status'] = int(schedule['status'])
        result = main.rpc.schedule.add_schedule(schedule)
        return jsonify(result)
    elif request.method == 'DELETE':
        _sids = request.form.get('ids', None)
        if not _sids:
            result = {'code': -1, "msg": "ids不能为空"}
            return jsonify(result)
        sids = _sids.split(',')
        result = main.rpc.schedule.del_schedule(sids)
        return jsonify(result)
    elif request.method == 'PUT':  # 更新
        if sid:
            rid = request.form.get('room', None)
            mid = request.form.get('movie', None)
            start = request.form.get('start_time', None)
            end = request.form.get('end_time', None)
            schedule = {
                'id': request.form.get('id', None),
                'room': main.rpc.room.get_room(rid)['data'],
                'movie': main.rpc.movie.get_movie(mid)['data'],
                'start_time': start if not start else start[:5],
                'end_time': end if not end else end[:5],
                'price': request.form.get('price', None),
                'date': request.form.get('date', None),
                'status': request.form.get('status', None)
            }
            schedule = {k: v for k, v in schedule.items() if v}
            if hasattr(schedule, 'status'):
                schedule['status'] = int(schedule['status'])
            result = main.rpc.schedule.update_schedule(schedule)
        else:
            _sids = request.form.get('ids', None)
            if not _sids:
                result = {'code': -1, "msg": "ids不能为空"}
                return jsonify(result)
            sids = _sids.split(',')
            status = request.form.get('status', 0)
            result = main.rpc.schedule.update_status(sids, status)
        return jsonify(result)


@app.route('/logging', methods=['GET'])
# @authorize
def logging():
    if request.method == 'GET':
        date = request.args.get('date', None)
        type = request.args.get('type', None)
        skip = request.args.get('skip', 0)
        limit = request.args.get('limit', 50)
        if date:
            result = main.rpc.logging.get_by_date(date)
            return jsonify(result)
        elif type:
            result = main.rpc.loggiong.get_by_type(type)
            return jsonify(result)
        else:
            result = main.rpc.loggiong.get_loggings(skip, limit)
            return jsonify(result)


@app.route('/room', methods=['GET', 'POST', 'DELETE', 'PUT'])
@app.route('/room/<rid>', methods=['GET', 'PUT'])
# @authorize
def room(rid=None):
    if request.method == 'GET':
        if rid:
            result = main.rpc.room.get_room(rid)
            return jsonify(result)
        else:
            page = request.args.get('page', 1)
            status = request.args.get('status', None)
            limit = request.args.get('limit', 10)
            limit = int(limit)
            skip = (int(page) - 1) * limit
            if skip != None and limit != None:
                result = main.rpc.room.get_rooms(skip, limit)
            else:
                result = main.rpc.room.get_rooms()
            return jsonify(result)
    elif request.method == 'POST':  # 添加
        room = {
            'name': request.form.get('name', None),
            'total_seat': request.form.get('total_seat', 0),
            'seat_rows': request.form.get('seat_rows', ''),
            'ctime': str(datetime.datetime.now()),
            'status': request.form.get('status', 0)
        }
        if hasattr(room, 'status'):
            room['status'] = int(room['status'])
        result = main.rpc.room.add_room(room)
        return jsonify(result)
    elif request.method == 'DELETE':
        _rids = request.form.get('ids', None)
        if not _rids:
            result = {'code': -1, "msg": "ids不能为空"}
            return jsonify(result)
        rids = _rids.split(',')
        result = main.rpc.room.del_rooms(rids)
        return jsonify(result)
    elif request.method == 'PUT':  # 更新
        room = {
            'name': request.form.get('name', None),
            'total_seat': request.form.get('total_seat', None),
            'seat_rows': request.form.get('seat_rows', None),
            'status': request.form.get('status', None)
        }
        room = {k: v for k, v in room.items() if v}
        if hasattr(room, 'status'):
            room['status'] = int(room['status'])
        result = main.rpc.room.update_room(rid, room)
        return jsonify(result)


@app.route('/poster', methods=['GET', 'POST', 'DELETE', 'PUT'])
@app.route('/poster/<pid>', methods=['GET', 'PUT'])
# @authorize
def poster(pid=None):
    if request.method == 'GET':
        if pid:
            result = main.rpc.poster.get_poster(pid)
            return jsonify(result)
        else:
            page = request.args.get('page', 1)
            limit = request.args.get('limit', 10)
            limit = int(limit)
            skip = (int(page) - 1) * limit
            status = request.args.get('status', None)
            if skip and limit:
                result = main.rpc.poster.get_posters(status, skip, limit)
            else:
                result = main.rpc.poster.get_posters(status)
            return jsonify(result)
    elif request.method == 'POST':  # 添加
        mid = request.form.get('movie', None)
        movie = main.rpc.movie.get_movie(mid)
        if movie['code'] != 0:
            return jsonify({'code': -1, 'msg': '电影信息不正确！'})
        _poster = request.files.get('poster', None)
        res = upload_tencent(_poster, mid + '.png', dir='poster')
        poster = {
            'movie': {
                'id': movie['data']['id'],
                'name': movie['data']['name']
            },
            'poster': res['access_url'],
            'ctime': str(datetime.datetime.now())[:19],
            'status': request.form.get('status', 0)
        }
        result = main.rpc.poster.add_poster(poster)
        return jsonify(result)
    elif request.method == 'DELETE':  # 批量删除
        _pids = request.form.get('ids', None)
        if not _pids:
            result = {'code': -1, "msg": "ids不能为空"}
            return jsonify(result)
        pids = _pids.split(',')
        result = main.rpc.poster.del_posters(pids)
        return jsonify(result)
    elif request.method == 'PUT':  # 更新
        if pid:
            mid = request.form.get('movie', None)
            _poster = request.files.get('poster', None)
            if _poster:
                res = upload_tencent(_poster, mid + '.png', dir='poster')
                _poster = res['access_url']
            poster = {
                'poster': _poster,
                'status': request.form.get('status', None)
            }
            poster = {k: v for k, v in poster.items() if v}

            result = main.rpc.poster.update_poster(pid, poster)
            return jsonify(result)
        else:
            _pids = request.form.get('ids', None)
            if not _pids:
                result = {'code': -1, "msg": "ids不能为空"}
                return jsonify(result)
            pids = _pids.split(',')
            status = request.form.get('status', 0)
            result = main.rpc.poster.update_status(pids, status)
            return jsonify(result)


@app.route('/comment', methods=['GET', 'DELETE', 'PUT'])
@app.route('/comment/<cid>', methods=['GET', 'DELETE', 'PUT'])
# @authorize
def comment(cid=None):
    if request.method == 'GET':
        page = request.args.get('page', 1)
        limit = request.args.get('limit', 10)
        limit = int(limit)
        skip = (int(page) - 1) * limit
        result = main.rpc.comment.get_comments(skip, limit)
        return jsonify(result)
    elif request.method == 'DELETE':
        _cids = request.form.get('ids', None)
        if not _cids:
            result = {'code': -1, "msg": "ids不能为空"}
            return jsonify(result)
        cids = _cids.split(',')
        result = main.rpc.comment.del_comments(cids)
        return jsonify(result)
    elif request.method == "PUT":
        _cids = request.form.get('ids', None)
        status = request.form.get('status', None)
        if not _cids and not status:
            result = {'code': -1, "msg": "参数不能为空"}
            return jsonify(result)
        cids = _cids.split(',')
        status = int(status)
        result = main.rpc.comment.update_comments(cids, status)
        return jsonify(result)


@app.route('/order')
# @authorize
def order():
    if request.method == 'GET':
        page = request.args.get('page', 1)
        limit = request.args.get('limit', 10)
        limit = int(limit)
        skip = (int(page) - 1) * limit
        result = main.rpc.order.get_orders_all(skip, limit)
        return jsonify(result)


@app.route('/user', methods=['GET', 'PUT'])
# @authorize
def user():
    if request.method == 'GET':
        page = request.args.get('page', 1)
        limit = request.args.get('limit', 10)
        limit = int(limit)
        skip = (int(page) - 1) * limit
        result = main.rpc.user.get_users(skip, limit)
        return jsonify(result)
    elif request.method == 'PUT':
        _uids = request.form.get('ids', None)
        if not _uids:
            result = {'code': -1, "msg": "ids不能为空"}
            return jsonify(result)
        uids = _uids.split(',')
        status = request.form.get('status', None)
        status = int(status)
        result = main.rpc.user.update_users(uids, status)
        return jsonify(result)


@app.route('/statistics')
# @authorize
def statistics():
    today = main.rpc.order.get_orders()
    pass


from cos_lib3.cos import Cos

cos = Cos(app_id=1252672422, secret_id='AKIDZw391fnGCrKWS8GgZBX7WyCBzf6IA2Yp',
          secret_key='EF5g290f5GEvMWR6ax83h8JDrFMHwKZd', region='cd')
bucket = cos.get_bucket("micro")


# 上传文件到腾讯 对象存储
def upload_tencent(file, file_name, dir='cover'):
    return bucket.upload_file_stream(file, file_name, dir_name=dir)
