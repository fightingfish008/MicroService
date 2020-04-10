import datetime
import json

import requests
import schedule
import time
from pymongo import MongoClient

username = 'admin'
password = 'wxs1995.'
host = '139.199.10.230'
port = 27017
db = 'admin'

client = None


def init_db():
    global client
    if not client:
        uri = 'mongodb://%s:%s@%s:%s' % (username, password, host, port)
        client = MongoClient(uri)
    return client


def update_schedule():
    client = init_db()
    result = client['micro_schedule']['schedule'].update_many(
        {'status': 1, 'date': {'$lt': str(datetime.datetime.now().date())}}, {'$set': {'status': 0}})
    print(result.modified_count)
    result = client['micro_schedule']['schedule'].update_many(
        {'status': 1, 'date': {'$lte': str(datetime.datetime.now().date())},
         'start_time': {"$lt": str(datetime.datetime.now().time())[:5]}}, {'$set': {'status': 0}})
    print(result.modified_count)


def update_order():
    client = init_db()
    result = client['micro_order']['order'].find({'status': 0}, {'_id': 1, 'ctime': 1})
    ids = []
    for _ in result:
        ctime = datetime.datetime.strptime(_['ctime'], "%Y-%m-%d %H:%M:%S")
        if (datetime.datetime.now() - ctime).seconds > 15 * 60:
            ids.append(_['_id'])
    result = client['micro_order']['order'].update_many({'status': 0, '_id': {'$in': ids}}, {'$set': {'status': 3}})
    print(result.modified_count)


def movie_update_status():
    client = init_db()
    result = client['micro_movie']['movie'].update_many({'showtime': {'$lte': str(datetime.date.today())}},
                                                        {'$set': {'status': 2}})
    if result.modified_count > 0:
        print('ok')
    else:
        print('error')


def insert_db(db, table, item):
    client = init_db()
    try:
        result = client[db][table].insert_many(item)
    except:
        print(item)
        return None
    return result.inserted_ids


def get_movie(name):
    client = init_db()
    result = client['micro_movie'].movie.find_one({'name': name})
    if result:
        result['id'] = str(result['_id'])
        result.pop('_id')
    return result


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


def fetch_movie_schedule():
    url = 'http://m.maoyan.com/ajax/cinemaDetail?cinemaId=10967'
    resp = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'})
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
                    print(insert_db('micro_schedule', 'schedule', [schedule]))
                except:
                    continue


schedule.every().minutes.do(update_order)  # 自动取消未完成订单
schedule.every().minutes.do(update_schedule)  # 自动取消未完成订单
schedule.every().day.at("02:30").do(fetch_movie_schedule)  # 自动抓取电影排期


def start():
    while True:
        schedule.run_pending()
        time.sleep(10)


if __name__ == '__main__':
    start()
    # update_schedule()
