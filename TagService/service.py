from bson import ObjectId
from nameko.rpc import rpc

from TagService.dbhelper import DBHelper
from pymongo.errors import DuplicateKeyError
from utils.dependencies import LoggingDependency


class TagService():
    name = 'tag'
    log = LoggingDependency()

    def __init__(self):
        self.dbhelper = DBHelper()
        self.tag = self.dbhelper.db.tag

    @rpc
    def add_tag(self, tag):
        try:
            result = self.tag.insert_one(tag)
            if result.inserted_id:
                return {"code": 0, "msg": "添加成功"}
            else:
                return {"code": -1, "msg": "添加失败"}
        except DuplicateKeyError as e:
            return {"code": -1, "msg": "添加失败，标签已存在"}

    @rpc
    def del_tag(self, tids):
        if not tids: return {'code': -1, "msg": "id不能为空"}
        result = self.tag.delete_many({"_id": {'$in': [ObjectId(tid) for tid in tids]}})
        if result.deleted_count > 0:
            return {"code": 0, "msg": "删除成功"}
        else:
            return {"code": -1, "msg": "删除失败"}

    @rpc
    def update_tag(self, tid, tag):
        if not tid:
            return {"code": -3, "msg": "id不能为空"}
        result = self.tag.update_one({"_id": ObjectId(tid)}, {"$set": tag})
        if result.matched_count == 1:
            if result.modified_count == 1:
                return {"code": 0, "msg": "更新成功"}
            else:
                return {"code": -1, "msg": "更新失败"}
        elif result.matched_count == 0:
            return {"code": -1, "msg": "更新失败，标签不存在"}

    # 批量更新标签状态
    @rpc
    def update_status(self, tids, status):
        if not tids:
            return {"code": -3, "msg": "id不能为空"}
        result = self.tag.update_many({"_id": {'$in': [ObjectId(tid) for tid in tids]}}, {"$set": {'status': status}})
        if result.matched_count > 0:
            if result.modified_count > 0:
                return {"code": 0, "msg": "更新成功", 'count': result.modified_count}
            else:
                return {"code": -1, "msg": "更新失败"}
        elif result.matched_count == 0:
            return {"code": -1, "msg": "更新失败，标签不存在"}

    # 根据 获取标签
    @rpc
    def get_tag(self, tid):
        result = self.tag.find()
        data = []
        for r in result:
            r['id'] = str(r['_id'])
            del r['_id']
            data.append(r)
        return data

    @rpc
    def get_tags(self, status=None, skip=0, limit=10):
        if limit > 10 or limit <= 0: limit = 10
        Q = {}
        if status != None:
            Q['status'] = status
        result = self.tag.find(Q)
        data = []
        for r in result:
            r['id'] = str(r['_id'])
            r['ctime'] = str(r['ctime'])[:19]
            del r['_id']
            data.append(r)
        return {
            'code': 0,
            'msg': '',
            'count': len(data),
            'data': data
        }
