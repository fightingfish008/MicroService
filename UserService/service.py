import datetime
import jwt
from bson import ObjectId

from UserService.dbhelper import DBHelper
from nameko.rpc import rpc
from pymongo.errors import DuplicateKeyError


class UserService:
    name = 'user'

    def __init__(self):
        self.dbhelper = DBHelper()
        self.user = self.dbhelper.db.user
        self.want = self.dbhelper.db.want

    @rpc
    def get_want_by_user(self, uid):
        result = self.want.find({'uid': uid})
        data = []
        for _ in result:
            _['movie']['wid'] = str(_['_id'])
            data.append(_['movie'])
        return {"code": 0, "msg": "", 'data': data}

    @rpc
    def get_want_by_mid(self, uid, mid):
        result = self.want.find_one({'uid': uid, 'movie.id': mid})
        if result:
            return {"code": 0, "msg": "已添加到想看列表"}
        else:
            return {"code": -1, "msg": "未添加到想看列表"}

    @rpc
    def get_want_count_movie(self, mid):
        result = self.want.count({'mid': mid})
        return result

    @rpc
    def add_or_del_want(self, want):
        uid = want['uid']
        mid = want['movie']['id']
        result = self.want.find_one({'uid': uid, 'movie.id': mid})
        if result:
            self.want.remove({'_id': result['_id']})
            data = {'code': 0, 'msg': '已从想看电影列表移除'}
        else:
            self.want.insert_one(want)
            data = {'code': 0, 'msg': '成功添加到想看电影列表'}
        return data

    @rpc
    def get_user(self, uid):
        result = self.user.find_one({'_id': ObjectId(uid)}, {'nickname': 1, '_id': 1})
        result['id'] = str(result['_id'])
        del result['_id']
        return result

    @rpc
    def get_users(self, skip=None, limit=None):
        if isinstance(skip, int) and isinstance(limit, int):
            result = self.user.find({}, {'password': 0}).skip(skip).limit(limit)
        else:
            result = self.user.find({}, {'password': 0})
        count = self.user.count()
        data = []
        for _ in result:
            _['id'] = str(_['_id'])
            _['phone'] = _['phone'][:3] + '*****' + _['phone'][8:]
            del _['_id']
            data.append(_)
        return {
            'code': 0,
            'msg': '',
            'count': count,
            'data': data
        }

    @rpc
    def update_users(self, uids, status):
        result = self.user.update_many({'_id': {'$in': [ObjectId(uid) for uid in uids]}}, {'$set': {'status': status}})
        if result.matched_count > 0:
            if result.modified_count > 0:
                return {'code': 0, 'msg': '更新成功'}
            else:
                return {'code': 0, 'msg': '状态未更改'}
        else:
            return {'code': -1, 'msg': '用户不存在'}

    @rpc
    def login(self, phone, passwd):
        result = self.user.find_one({'phone': phone})
        if not result:
            return {"code": -1, "msg": "账号不存在！"}
        if int(result['status']) == 0:
            return {"code": -1, "msg": "账号被冻结，请联系管理员解除冻结"}
        if result and result.get("password", None) == self.crypto(passwd):
            data = {
                'uid': str(result['_id']),
                "phone": result['phone'],
                "nickname": result['nickname'],
                "admin": False,
                "super": False,
            }
            token = self.encode_auth_token(data)
            return {"code": 0, "token": token.decode(), "msg": "登录成功"}
        else:
            return {"code": -1, "msg": "账号或者密码错误"}

    @rpc
    def register(self, user):
        user["password"] = self.crypto(user["password"])
        try:
            result = self.user.insert_one(user)
            if result.inserted_id:
                return {"code": 0, "msg": "注册成功"}
        except DuplicateKeyError as e:
            return {"code": -1, "msg": "该手机号已注册，请登录"}
        except Exception as e:
            return {"code": -1, "msg": "注册失败"}

    @rpc
    def lock(self, uid):
        result = self.user.update_one({'_id': uid}, {"$set": {"status": 0}})
        if result.matched_count == 1:
            if result.midified_count == 1:
                return {"code": 0, "msg": "禁用成功"}
            else:
                return {"code": -1, "msg": "禁用失败"}
        else:
            return {"code": -1, "msg": "启用成功"}

    @rpc
    def update(self, user):
        uid = user['id']
        del user['id']
        upgradable = ['password', 'nick', 'status']  # 允许更新的值
        for k, v in user:
            if not k in upgradable:
                del upgradable[k]
        result = self.user.update_one({"_id", uid}, {"$set": user})
        if result.matched_count == 1:
            if result.midified_count == 1:
                return {"code": 0, "msg": "更新成功"}
            else:
                return {"code": -1, "msg": "更新失败"}
        else:
            return {"code": -1, "msg": "更新失败"}

    def crypto(self, src):
        import hashlib
        m = hashlib.md5()
        m.update(src.encode('utf-8'))
        return m.hexdigest()

    def encode_auth_token(self, data):
        """
        生成认证Token
        :param user_id: int
        :param login_time: int(timestamp)
        :return: string
        """
        from UserService.settings import SECRET_KEY
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
                'iat': datetime.datetime.utcnow(),
            }
            payload.update(data)
            return jwt.encode(
                payload,
                SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            return e
