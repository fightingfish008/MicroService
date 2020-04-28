import datetime

import requests
import json

from pymongo import MongoClient

username = 'admin'
password = 'wxs1995.'
host = '139.199.10.230'
port = 27017
db = 'admin'

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
}


def init_db():
    uri = 'mongodb://%s:%s@%s:%s' % (username, password, host, port)
    client = MongoClient(uri)
    return client


def insert_db(db, table, item):
    client = init_db()
    try:
        result = client[db][table].insert_one(item)
    except Exception as e:
        print(e)
        return None
    return result.inserted_ids


def get_movie(name):
    client = init_db()
    result = client['micro_movie'].movie.find_one({'name': name})
    if result:
        result['id'] = str(result['_id'])
        result.pop('_id')
    return result


def get_movie_info(mid):
    url2 = 'http://m.maoyan.com/ajax/detailmovie?movieId=' + str(mid)
    resp = requests.get(url2, headers=headers)
    detail = json.loads(resp.text)
    detailMovie = detail['detailMovie']
    try:
        movie = {
            'name': detailMovie['nm'],
            'cover': detailMovie['img'].replace('w.h', '148.208'),
            'showtime': detailMovie['rt'],
            'duration': detailMovie['dur'],
            'director': detailMovie['dir'],
            'players': detailMovie['star'],
            'country': detailMovie['src'],
            'description': detailMovie['dra'],
            'type': '3D',
            'score': detailMovie['sc'],
            'ctime': str(datetime.datetime.now())[:19],
            'tags': detailMovie['cat'].split(','),
            'want': detailMovie['wish'],
            'status': 1 if detailMovie['rt'] > str(datetime.date.today()) else 2  # 0:不可用，1：已下映，2：正在热播，3：未上映
        }
    except:
        movie = None
    return movie


def fetch_playing_movie():
    url = 'http://m.maoyan.com/ajax/movieOnInfoList'
    resp = requests.get(url, headers=headers)
    _json = json.loads(resp.text)
    movies = []
    for _ in _json['movieIds']:
        movie = get_movie_info(_)
        del movie['_id']
        if not movie:
            continue
        movies.append(movie)
    print(insert_db('micro_movie', 'movie', movies))


def fetch_upcoming_movie():
    url = 'http://m.maoyan.com/ajax/mostExpected?ci=57&limit=30&offset=0&token='
    resp = requests.get(url, headers=headers)
    _json = json.loads(resp.text)
    movies = []
    for _ in _json['coming']:
        movie = get_movie_info(_['id'])
        if not movie:
            continue
        movies.append(movie)
    print(insert_db('micro_movie', 'movie', movies))


def fetch_movie_schedule():
    url = 'http://m.maoyan.com/ajax/cinemaDetail?cinemaId=10967'

    resp = requests.get(url, headers=headers)
    _json = json.loads(resp.text)
    rooms = [
        {"id": "5aefedeacaa09a08a375f5e6", "name": "1号厅", "seat_rows": "9,9,9,9,10"}
        , {"id": "5af8256acaa09a716afd7896", "name": "2号厅", "seat_rows": "9,9,9,9,9,9,9"}
        , {"id": "5af867b5caa09a7b8cd3ee0d", "name": "3号厅", "seat_rows": "9,9,9,9,9,9,9,9"}
        , {"id": "5af867bbcaa09a7b8cd3ee10", "name": "4号厅", "seat_rows": "9,9,9,9,9,9,9,9"}
        , {"id": "5b009ac4caa09a337293f958", "name": "5号厅", "seat_rows": "8,8,8,8,9,9,9"}
    ]
    t = 0
    for _1 in _json['showData']['movies']:
        duration = _1['dur']
        for _2 in _1['shows']:
            for _ in _2['plist']:
                movie = get_movie(_1['nm'])
                if not movie:
                    continue
                try:
                    schedule = {
                        'room': rooms[t % 4],
                        'movie': movie,
                        'start_time': _['tm'],
                        'end_time': end_time(_['tm'], duration),
                        'price': _['vipPrice'],
                        'date': _['dt'],
                        'ctime': str(datetime.datetime.now())[:19],
                        'status': 1  # 1: 启用 ，0：禁用
                    }
                    t += 1
                    if hasattr(schedule, '_id'):
                        del schedule['_id']
                    print(insert_db('micro_schedule', 'schedule', schedule))
                except:
                    continue


def end_time(tm, dur):
    tms = tm.split(':')
    h = int(tms[0])
    m = int(tms[1])
    dur = int(dur)
    dh = (dur // 60)
    dm = dur % 60
    if m + dm > 59:
        m = m + dm - 60
        h = h + dh + 1
    else:
        h = h + dh
        m = m + dm
    return str(h) + ':' + str(m)


from cos_lib3.cos import Cos

cos = Cos(app_id=12345678, secret_id='xxxxxxxxx',
          secret_key='xxxxxxxxxxxxxx', region='cd')
bucket = cos.get_bucket("micro")


def upload_tencent(url, file_name, dir):
    return bucket.upload_file_from_url(url, file_name, dir_name=dir)


if __name__ == '__main__':
    # fetch_playing_movie()
    # fetch_upcoming_movie()
    fetch_movie_schedule()
