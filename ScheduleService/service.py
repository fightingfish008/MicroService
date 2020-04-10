import datetime

from bson import ObjectId
from nameko.rpc import rpc
from pymongo.errors import DuplicateKeyError

from ScheduleService.dbhelper import DBHelper


# 排期
class ScheduleService:
    name = "schedule"

    def __init__(self):
        self.dbhelper = DBHelper()
        self.schedule = self.dbhelper.db.schedule

    @rpc
    def add_schedule(self, schedule):
        try:
            result = self.schedule.insert_one(schedule)
            if result.inserted_id:
                return {'code': 0, "msg": "添加成功"}
            else:
                return {'code': -1, "msg": "添加失败"}

        except DuplicateKeyError as e:
            return {'code': -1, "msg": "添加失败,排期已存在"}

    @rpc
    def del_schedule(self, sids):
        if not sids:
            return {'code': -1, 'msg': 'id不能为空'}
        result = self.schedule.delete_many({"_id": {'$in': [ObjectId(sid) for sid in sids]}})
        if result.deleted_count > 0:
            return {'code': 0, "msg": "删除成功"}
        else:
            return {'code': -1, "msg": "删除失败,排期不存在"}

    @rpc
    def update_schedule(self, new_data):
        sid = new_data.pop('id')
        result = self.schedule.update_one({"_id": ObjectId(sid)}, {"$set": new_data})
        if result.modified_count == 1:
            return {'code': 0, "msg": "更新成功"}
        else:
            return {'code': -1, "msg": "更新失败,排期不存在"}

    @rpc
    def update_status(self, sids, status):
        status = int(status)
        result = self.schedule.update_many({"_id": {'$in': [ObjectId(sid) for sid in sids]}},
                                           {"$set": {'status': status}})
        if result.modified_count > 0:
            return {'code': 0, "msg": "更新成功", 'count': result.modified_count}
        else:
            return {'code': -1, "msg": "更新失败,排期不存在"}

    @rpc
    def get_schedule(self, sid):
        result = self.schedule.find_one({"_id": ObjectId(sid), 'status': 1})
        if result:
            result['id'] = str(result['_id'])
            del result['_id']
            return {
                'code': 0,
                'msg': '',
                'data': result
            }
        else:
            return {'code': -1, 'msg': '该排期不存在'}

    @rpc
    def get_schedules(self, skip=None, limit=None):
        if isinstance(skip, int) and isinstance(limit, int):
            result = self.schedule.find().skip(skip).limit(limit)
        else:
            result = self.schedule.find()
        count = self.schedule.count()
        data = []
        for r in result:
            r['id'] = str(r['_id'])
            del r['_id']
            data.append(r)
        return {
            'code': 0,
            'msg': '',
            'count': count,
            'data': data
        }

    @rpc
    def get_schedules_mid(self, mid=None):
        Q = {'status': 1, 'date': {"$gte": str(datetime.date.today())}}
        if mid != None:
            Q['movie.id'] = mid
        result = self.schedule.find(Q, {"movie": 0})
        data = []
        for r in result:
            r['id'] = str(r['_id'])
            del r['_id']
            data.append(r)
        return {
            'code': 0,
            'msg': '',
            'data': {
                'schedule': data
            }
        }
