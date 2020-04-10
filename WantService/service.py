from nameko.rpc import rpc

from SearchService.dbhelper import DBHelper


class WantService:
    name = 'want'

    def __init__(self):
        self.dbhelper = DBHelper()
        self.want = self.dbhelper.db.want

    @rpc
    def get_want_user(self, uid):
        if not uid:
            return {
                'code': -1, 'msg': 'id不能为空'
            }
        result = self.want.insert_one({'uid': uid})
        return {
            'code': 0, 'msg': '', 'data': result, 'count': len(result)
        }

    @rpc
    def get_want_movie(self, mid):
        if not mid:
            return {
                'code': -1, 'msg': 'id不能为空'
            }
        result = self.want.insert_one({'mid': mid})
        return {
            'code': 0, 'msg': '', 'data': result, 'count': len(result)
        }

    @rpc
    def add_want(self, want):
        uid = want['uid']
        mid = want['movie']['id']
        result = self.want.update_one({'uid': uid, 'movie.id': mid}, {'$set': want}, update=True)
        if result.inserted_id:
            return {
                'code': 0, 'msg': '添加成功'
            }
        else:
            return {
                'code': -1, 'msg': '添加失败'
            }
