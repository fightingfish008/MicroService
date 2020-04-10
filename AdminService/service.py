# nameko run AdminService.service --broker amqp://guest:123456@localhost
import datetime

import jwt
from nameko.rpc import rpc
from AdminService.dbhelper import DBHelper


class AdminService:
    name = 'admin'

    def __init__(self):
        self.dbhelper = DBHelper()
        self.admin = self.dbhelper.db.admin

    @rpc
    def login(self, username, passwd):
        result = self.admin.find_one({'username': username})
        if result and result.pop("password") == passwd:
            return {"code": 0, "data": result['username'], "msg": "登录成功"}
        else:
            return {"code": -1, "msg": "账号或者密码错误"}