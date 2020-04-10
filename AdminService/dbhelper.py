class DBHelper(object):
    # 单例模式
    def __new__(cls, *args, **kwargs):
        if not hasattr(DBHelper, "_instance"):
            DBHelper._instance = object.__new__(DBHelper)
        return DBHelper._instance

    def __init__(self, conf=None):
        if not conf:
            from AdminService.settings import DATABASE as conf
        uri = 'mongodb://%s:%s@%s:%s/%s' % (conf['user'], conf['password'], conf['host'], conf['port'],conf['database'])
        from pymongo import MongoClient
        self.client = MongoClient(uri)
        self.db = self.client[conf['database']]
        pass

    def close(self):
        self.client.close()

if __name__ =="__main__":
    mydb=DBHelper()
    res = mydb.db.testDB.find_one({'hello': 1})
    pass