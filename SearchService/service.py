from nameko.rpc import rpc, RpcProxy

from SearchService.dbhelper import DBHelper
from utils.dependencies import LoggingDependency


class SearchService:
    name = 'search'
    movie = RpcProxy('movie')
    log = LoggingDependency()

    def __init__(self):
        self.dbhelper = DBHelper()
        self.db = self.dbhelper.db.tag

    @rpc
    def search(self, name):
        pass
