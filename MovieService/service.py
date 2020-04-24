from bson import ObjectId
from nameko.rpc import rpc

from MovieService.dbhelper import DBHelper
from pymongo.errors import DuplicateKeyError
from utils.dependencies import LoggingDependency


class MovieService():
    name = 'movie'
    log = LoggingDependency()

    def __init__(self):
        self.dbhelper = DBHelper()
        self.movie = self.dbhelper.db.movie

    @rpc
    def add_movie(self, movie):
        if not movie.get('name', None):
            return {"code": -1, "msg": "名称不能为空"}
        try:
            result = self.movie.insert_one(movie)
            if result.inserted_id:
                return {"code": 0, "msg": "添加成功", 'id': str(result.inserted_id)}
            else:
                return {"code": -1, "msg": "添加失败"}
        except DuplicateKeyError:
            return {"code": -1, "msg": "添加失败,电影已存在"}

    @rpc
    def del_movie(self, mids):
        if not mids: return {'code': -1, "msg": "id不能为空"}
        result = self.movie.delete_many({"_id": {'$in': [ObjectId(mid) for mid in mids]}})
        if result.deleted_count > 0:
            return {"code": 0, "msg": "删除成功", 'count': result.deleted_count}
        else:
            return {"code": -1, "msg": "删除失败,电影不存在"}

    @rpc
    def update_movie(self, mid, movie):
        if not mid:
            return {"code": -1, "msg": "id不能为空"}
        result = self.movie.update_one({'_id': ObjectId(mid)}, {'$set': movie})
        if result.matched_count > 0:
            if result.modified_count == 1:
                return {"code": 0, "msg": "更新成功"}
            else:
                return {"code": 0, "msg": "数据未修改"}
        else:
            return {"code": -1, "msg": "更新失败，电影不存在"}

    # 批量更新标签状态
    @rpc
    def update_status(self, mids, status):
        if not mids:
            return {"code": -1, "msg": "id不能为空"}
        result = self.movie.update_many({"_id": {'$in': [ObjectId(mid) for mid in mids]}}, {"$set": {'status': status}})
        if result.matched_count > 0:
            if result.modified_count > 0:
                return {"code": 0, "msg": "更新成功", 'count': result.modified_count}
            else:
                return {"code": -1, "msg": "更新失败"}
        elif result.matched_count == 0:
            return {"code": -1, "msg": "更新失败，电影不存在"}

    @rpc
    def get_movie(self, mid):
        result = self.movie.find_one({'_id': ObjectId(mid)})
        if result:
            result['id'] = str(result['_id'])
            result.pop('_id')
            return {"code": 0, "msg": "", 'data': result}
        else:
            return {'code': -1, 'msg': '电影不存在'}

    @rpc
    def search_movie(self, name):
        result = self.movie.find({'name': {"$regex": name}, 'status': {'$in': [1, 2, 3]}}, {'ctime': 0, 'status': 0})
        data = []
        for r in result:
            r['id'] = str(r['_id'])
            del r['_id']
            data.append(r)
        return {"code": 0, "msg": "", 'count': len(data), 'data': data}

    @rpc
    def get_movies(self, status=None, skip=None, limit=None):
        Q = {}
        if status:
            Q['status'] = int(status)
        if isinstance(skip, int) and isinstance(limit, int):
            result = self.movie.find(Q).skip(skip).limit(limit)
        else:
            result = self.movie.find(Q)
        count = self.movie.count(Q)
        data = []
        for r in result:
            r['id'] = str(r['_id'])
            del r['_id']
            data.append(r)
        return {"code": 0, "msg": "", 'count': count, 'data': data}

    @rpc
    def get_names(self, skip=0, limit=20):
        if limit > 20: limit = 20
        result = self.movie.find().skip(skip).limit(limit)
        count = self.movie.count()
        data = []
        for r in result:
            data.append(r['name'])
        return {"code": 0, "msg": "", 'count': count, 'data': data}
