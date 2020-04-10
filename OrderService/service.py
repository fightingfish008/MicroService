import re

from bson import ObjectId
from nameko.rpc import rpc

from OrderService.dbhelper import DBHelper
from pymongo.errors import DuplicateKeyError


class OrderService:
    name = 'order'

    def __init__(self):
        self.dbhelper = DBHelper()
        self.order = self.dbhelper.db.order

    # 生成新订单
    @rpc
    def add_order(self, order):
        try:
            result = self.order.insert_one(order)
            return {'code': 0, "msg": "订单生成成功", "oid": str(result.inserted_id)}
        except DuplicateKeyError as e:
            msg = e.details['errmsg']
            m = re.search(r'(\d+):(\d+)', msg)
            return {'code': -1, "msg": "生成订单失败,座位<" + str(m.group(1)) + "排" + str(m.group(2)) + "座>已售出!"}

    # 取消订单
    @rpc
    def cancel_order(self, oid):
        result = self.order.update_one({'_id': ObjectId(oid)}, {"$set": {'status': 3}})
        if result.matched_count == 1:
            if result.modified_count == 1:
                return {'code': 0, "msg": "订单取消成功"}
            else:
                return {'code': -1, "msg": "取消订单失败，订单已经取消了"}
        else:
            return {'code': -1, "msg": "订单不存在"}

    # 支付成功后,更新订单
    @rpc
    def update_order(self, oid):
        if not oid:
            return {'code': -1, "msg": "id不能为空"}
        result = self.order.update_one({'_id': ObjectId(oid)}, {"$set": {'status': 1}})
        if result.matched_count == 1:
            if result.modified_count == 1:
                return {'code': 0, "msg": "支付成功"}
            else:
                return {'code': -1, "msg": "支付失败，订单已经支付过了"}
        else:
            return {'code': -1, "msg": "订单不存在"}

    @rpc
    def get_order(self, oid, uid=None):
        Q = {'_id': ObjectId(oid)}
        if uid:
            Q['uid'] = uid
        result = self.order.find_one(Q)
        result['id'] = str(result['_id'])
        del result['_id']
        return {
            'code': 0,
            'msg': '',
            'data': result
        }

    @rpc
    def get_orders(self, uid, status=None):
        Q = {'uid': uid}
        if status:
            Q['status'] = status
        result = self.order.find(Q)
        count = self.order.count(Q)
        data = []
        for r in result:
            r['id'] = str(r['_id'])
            del r['_id']
            data.append(r)
        return {'code': 0, 'msg': '', 'count': count, 'data': data}

    @rpc
    def get_seen(self, uid):
        Q = {'uid': uid, 'status': 2}
        result = self.order.find(Q)
        count = self.order.count(Q)
        data = []
        mids = []  # 暂时这样写吧，有时间再优化，dict无法hash，无法使用set去重
        for r in result:
            if r['schedule']['movie']['id'] in mids:
                continue
            mids.append(r['schedule']['movie']['id'])
            data.append(r['schedule']['movie'])
        return {'code': 0, 'msg': '', 'count': count, 'data': data}

    @rpc
    def get_orders_all(self, skip=None, limit=None):
        if isinstance(skip, int) and isinstance(limit, int):
            result = self.order.find().skip(skip).limit(limit)
        else:
            result = self.order.find()
        count = self.order.count()
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
    def get_sold_seats(self, sid):
        result = self.order.find({'schedule.id': sid, 'status': {'$in': [0, 1, 2]}}, {'seats': 1})
        data = set()
        if result:
            for _ in result:
                for __ in _['seats']:
                    data.add(__)
        return {'code': 0, 'msg': '', 'data': list(data)}
