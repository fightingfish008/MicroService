from bson import ObjectId
from nameko.rpc import rpc

from PosterService.dbhelper import DBHelper


class PosterService:
    name = 'poster'

    def __init__(self):
        self.dbhelper = DBHelper()
        self.poster = self.dbhelper.db.poster

    @rpc
    def add_poster(self, poster):
        result = self.poster.insert_one(poster)
        if result.inserted_id:
            return {"code": 0, "msg": "添加成功"}
        else:
            return {"code": -1, "msg": "添加失败"}

    @rpc
    def update_status(self, pids, status=0):
        result = self.poster.update_many({"_id": {'$in': [ObjectId(pid) for pid in pids]}},
                                         {"$set": {'status': status}})
        if result.modified_count > 1:
            return {"code": 0, "msg": "更新成功"}
        else:
            return {"code": -1, "msg": "更新失败"}

    @rpc
    def update_poster(self, pid, poster):
        result = self.poster.update_one({"_id": ObjectId(pid)}, {"$set": poster})
        if result.matched_count > 0:
            if result.modified_count > 0:
                return {"code": 0, "msg": "更新成功"}
            else:
                return {"code": -1, "msg": "未修改数据"}
        else:
            return {"code": -1, "msg": "更新失败，海报不存在"}

    @rpc
    def del_posters(self, pid):
        result = self.poster.delete_one({"_id": ObjectId(pid)})
        if result.deleted_count == 1:
            return {"code": 0, "msg": "删除成功"}
        else:
            return {"code": -1, "msg": "删除失败，海报不存在"}

    @rpc
    def get_poster(self, pid):
        result = self.poster.find({'_id': ObjectId(pid)})
        result['id'] = str(result['_id'])
        del result['_id']
        return {'code': 0, 'msg': '', 'data': result}

    @rpc
    def get_posters(self, status=None, skip=0, limit=10):
        Q = {}
        if status:
            Q['status'] = status
        if skip and limit:
            result = self.poster.find(Q).skip(skip).limit(limit)
        else:
            result = self.poster.find(Q)
        data = []
        for r in result:
            r['id'] = str(r['_id'])
            del r['_id']
            data.append(r)
        return {'code': 0, 'msg': '', 'data': data}
