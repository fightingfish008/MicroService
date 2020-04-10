import datetime
import re
import time

from pymongo.errors import DuplicateKeyError
from werkzeug.security import generate_password_hash

# print(generate_password_hash('wxs'))
# print(generate_password_hash('wxs'))

# print(datetime.date.today())

from pymongo import MongoClient

username = 'admin'
password = 'wxs1995.'
host = '139.199.10.230'
port = 27017
db = 'admin'


def create_index(client):
    a = client.micro_schedule.schedule.find(
        {'mid': '5af8620dcaa09a7b8a707937', 'status': '1', 'date': {"$gte": str(datetime.date.today())}})
    for _ in a:
        print(_['date'], _['movie']['name'])
    # pass


def DuplicateKey(client):
    client.wxs.user.create_index([('tags', 1)], unique=True)
    print(client.wxs.user.list_indexes())
    try:
        order = {
            'uid': '123',
            'schedule': {'id': '5af82b75caa09a648ed33153'},
            'total': 123,
            'seats': ["1:1", "1:2", "1:3", "1:4"],
            'ctime': str(datetime.datetime.now())[:19],
            'status': 0  # 0:待付款，1:已取消，2：已付款，3：已退订，4：已退款
        }
        client.micro_order.order.insert(order)
    except DuplicateKeyError as e:
        msg = e.details['errmsg']
        print(msg)
        m = re.search(r'(\d+):(\d+)', msg)
        print(m.group(0))
        print(m.group(1))
        print(m.group(2))


def update_movie_status_2_int():
    client = init()
    dbs = ['movie', 'room', 'user', 'schedule', 'order', 'comment', 'admin']
    for _ in dbs:
        moviedb = client['micro_' + _][_].update_many({'status': '0'}, {'$set': {'status': 0}})
        moviedb = client['micro_' + _][_].update_many({'status': '1'}, {'$set': {'status': 1}})
        moviedb = client['micro_' + _][_].update_many({'status': '2'}, {'$set': {'status': 2}})
        moviedb = client['micro_' + _][_].update_many({'status': '3'}, {'$set': {'status': 3}})


def update_movie_country(client):
    # result = client.micro_movie.movie.find({'country': None})
    # for r in result:
    #     print(r.get('country','dasdsad'))
    moviedb = client.micro_movie.movie.update_many({'country': None}, {'$set': {'country': "美国"}})
    pass


def get_schedule():
    client = init()
    result = client['micro_schedule']['schedule'].find({'status': 1, 'date': {"$gte": str(datetime.date.today())}})
    for _ in result:
        print(_)


def init():
    uri = 'mongodb://%s:%s@%s:%s' % (username, password, host, port)
    client = MongoClient(uri)
    return client


if __name__ == '__main__':
    # update_movie_status_2_int()
    a = '2018-05-26 19:39:12'
    print(datetime.datetime.strptime(a, "%Y-%m-%d %H:%M:%S"))
    print(str(datetime.datetime.now().time())[:5])
    print(str(datetime.datetime.now().date()))
