from nameko.rpc import rpc, RpcProxy

from SearchService.dbhelper import DBHelper


class SearchService:
    name = 'search'
    movie = RpcProxy('movie')

    def __init__(self):
        self.dbhelper = DBHelper()
        self.db = self.dbhelper.db.tag

    @rpc
    def search(self, name):
        pass
