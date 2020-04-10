import datetime

import pymongo
from bson import ObjectId
from nameko.rpc import rpc

from CommentService.dbhelper import DBHelper


class CommentService:
    name = 'comment'

    def __init__(self):
        self.dbhelper = DBHelper()
        self.comment = self.dbhelper.db.comment
        self.supported = self.dbhelper.db.supported

    @rpc
    def add_comment(self, comment):
        uid = comment['user']['id']
        mid = comment['movie']['id']
        result = self.comment.update_one({'user.id': uid, 'movie.id': mid},
                                         {'$set': comment,
                                          '$setOnInsert': {'support': 0,
                                                           'ctime': str(datetime.datetime.now())[:19],
                                                           'status': 1}},
                                         upsert=True)
        if result.upserted_id:
            return {'code': 0, "msg": "评论成功"}
        if result.matched_count > 0:
            if result.modified_count > 0:
                return {'code': 0, "msg": "评论成功"}
            else:
                return {'code': 0, "msg": "评论未修改"}
        else:
            return {'code': -1, "msg": "评论失败"}

    @rpc
    def support(self, uid, cid):
        # 点过赞再次点击取消赞
        count = self.supported.count({'uid': uid, 'cid': cid})
        if count > 0:  # 已经点过赞了
            result = self.comment.update_one({"_id": ObjectId(cid)}, {"$inc": {'support': -1}})
            self.supported.find_one_and_delete({'uid': uid, 'cid': cid})
            msg = "取消点赞"
        else:  # 未点过赞
            result = self.comment.update_one({"_id": ObjectId(cid)}, {"$inc": {'support': 1}})
            self.supported.insert_one({'uid': uid, 'cid': cid, 'ctime': str(datetime.datetime.now())[:19]})
            msg = "点赞成功"
        if result.matched_count > 0:
            if result.modified_count > 0:
                return {'code': 0, "msg": msg}
            else:
                return {'code': -1, "msg": "点赞失败"}
        else:
            return {'code': -1, "msg": "点赞失败，评论不存在"}

    @rpc
    def update_comments(self, cids, status):
        result = self.comment.update_many({"_id": {'$in': [ObjectId(cid) for cid in cids]}},
                                          {"$set": {'status': int(status)}})
        if result.modified_count > 0:
            return {'code': 0, "msg": "删除成功", 'count': result.deleted_count}
        else:
            return {'code': -1, "msg": "删除失败"}

    @rpc
    def del_comments(self, cids):
        result = self.comment.delete_many({"_id": {'$in': [ObjectId(cid) for cid in cids]}})
        if result.deleted_count > 0:
            return {'code': 0, "msg": "删除成功", 'count': result.deleted_count}
        else:
            return {'code': -1, "msg": "删除失败"}

    @rpc
    def del_comment(self, uid, mid):
        result = self.comment.delete_one({'user.id': uid, 'movie.id': mid})
        if result.deleted_count > 0:
            return {'code': 0, "msg": "评论已删除"}
        else:
            return {'code': -1, "msg": ""}

    @rpc
    def get_comments(self, skip=None, limit=None):
        if isinstance(skip, int) and isinstance(limit, int):
            result = self.comment.find().skip(skip).limit(limit)
        else:
            result = self.comment.find()
        count = self.comment.count()
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
    def get_comment_id(self, cid):
        Q = {'_id': ObjectId(cid)}
        result = self.comment.find_one(Q)
        result['id'] = str(result['_id'])
        del result['_id']
        return {
            'code': 0,
            'msg': '',
            'data': result
        }

    @rpc
    def get_comment(self, uid, mid):
        Q = {'user.id': uid, 'movie.id': mid}
        result = self.comment.find_one(Q)
        if result:
            result['id'] = str(result['_id'])
            del result['_id']
            return {'code': 0, 'msg': '', 'data': result}
        else:
            return {'code': -1, 'msg': '评论不存在'}

    @rpc
    def get_comments_by_user(self, uid):
        Q = {'user.id': uid}
        result = self.comment.find(Q)
        count = self.comment.count(Q)
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
    def get_comments_by_movie(self, mid, skip=None, limit=None):
        Q = {'movie.id': mid}
        if isinstance(skip, int) and isinstance(limit, int):
            result = self.comment.find(Q).skip(skip).limit(limit)
        else:
            result = self.comment.find(Q)
        count = self.comment.count(Q)
        data = []
        for r in result:
            r['id'] = str(r['_id'])
            del r['_id']
            data.append(r)
        return {
            'code': 0,
            'msg': '',
            'page': int(count // limit),
            'data': data
        }

    @rpc
    def get_newest(self, skip=0, limit=20):
        result = self.comment.find().sort('support', pymongo.DESCENDING).skip(skip).limit(limit)
        data = []
        for _ in result:
            _['id'] = str(_['_id'])
            del _['_id']
            data.append(_)
        return {
            'code': 0,
            'msg': '',
            'data': data
        }
