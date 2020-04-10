from pymongo import MongoClient

username = 'admin'
password = 'wxs1995.'
host = '139.199.10.230'
port = 27017
db = 'admin'


def create_index(client):
    client.micro_user.user.create_index([('phone', 1)], unique=True)
    client.micro_user.want.create_index([('uid', 1), ('movie.id', 1)], unique=True)
    client.micro_room.room.create_index([('name', 1)], unique=True)
    client.micro_comment.comment.create_index([('movie.id', 1), ('user.id', 1)], unique=True)
    client.micro_comment.supported.create_index([('uid', 1), ('cid', 1)], unique=True)
    client.micro_schedule.schedule.create_index([('date', 1), ('start_time', 1), ('movie.id', 1)], unique=True)
    client.micro_order.order.create_index([('seats', 1), ('schedule.id', 1)],
                                          partialFilterExpression={'status': {'$gt': 2}}, unique=True)  # 座位唯一索引
    client.micro_movie.movie.create_index([('name', 1)], unique=True)  # 电影唯一索引


def init():
    uri = 'mongodb://%s:%s@%s:%s' % (username, password, host, port)
    client = MongoClient(uri)
    create_index(client)


if __name__ == '__main__':
    init()
