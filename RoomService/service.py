from bson import ObjectId
from nameko.rpc import rpc
from pymongo.errors import DuplicateKeyError

from RoomService.dbhelper import DBHelper
from utils.dependencies import LoggingDependency


class RoomService:
    name = "room"
    log = LoggingDependency()

    def __init__(self):
        self.dbhelper = DBHelper()
        self.room = self.dbhelper.db.room

    @rpc
    def add_room(self, room):
        if not room.get('name', None):
            return {'code': -1, "msg": "名称不能为空"}
        try:
            result = self.room.insert_one(room)
            if result.inserted_id:
                return {'code': 0, "msg": "添加成功"}
            else:
                return {'code': -1, "msg": "添加失败"}
        except DuplicateKeyError:
            return {'code': -1, "msg": "影厅已存在"}

    @rpc
    def del_rooms(self, rids):
        result = self.room.delete_many({"_id": {'$in': [ObjectId(rid) for rid in rids]}})
        if result.deleted_count > 0:
            return {'code': 0, "msg": "删除成功", 'count': result.deleted_count}
        elif result.matched_count == 0:
            return {'code': -1, "msg": "删除失败,影厅不存在!"}

    @rpc
    def update_room(self, rid, room):
        result = self.room.update_one({"_id": ObjectId(rid)}, {"$set": room})
        if result.matched_count and result.modified_count > 0:
            return {'code': 0, "msg": "更新成功"}
        elif result.matched_count == 0:
            return {'code': -1, "msg": "更新失败，影厅不存在!"}

    @rpc
    def get_room(self, rid):
        result = self.room.find_one({"_id": ObjectId(rid)})
        result['id'] = str(result['_id'])
        del result['_id']
        return {
            'code': 0,
            'msg': '',
            'count': 1,
            'data': result
        }

    @rpc
    def get_rooms(self, skip=0, limit=20):
        result = self.room.find()
        data = []
        for r in result:
            r['id'] = str(r['_id'])
            del r['_id']
            data.append(r)
        return {
            'code': 0,
            'msg': '',
            'count': len(data),
            'data': data
        }
