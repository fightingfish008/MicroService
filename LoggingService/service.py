from nameko.rpc import rpc

from LoggingService.dbhelper import DBHelper

'''
type 
service
ctime
message

'''


class LoggingService:
    name = 'logging'

    def __init__(self):
        self.dbhelper = DBHelper()
        self.log = self.dbhelper.db.log

    @rpc
    def add_logging(self, log):
        try:
            result = self.log.insert_one(log)
            if result.inserted_id:
                return True
            else:
                return False
        except:
            return False

    @rpc
    def add_loggings(self, logs):
        try:
            self.log.insert_many(logs)
            return True
        except:
            return False

    @rpc
    def get_loggings(self, skip=0, limit=50):
        if limit > 50: limit = 50
        result = self.log.find().skip(skip).limit(limit).sort({'ctime': -1})
        data = []
        for r in result:
            r['id'] = str(r['_id'])
            r.pop('_id')
            data.append(r)
        return data

    @rpc
    def get_by_date(self, date):
        '''
        :param date: datetime
        :return: 
        '''
        result = self.log.find({'ctime': {'$eq': date}}).sort({'ctime': -1})
        datas = []
        for r in result:
            r['id'] = str(r['_id'])
            r.pop('_id')
            datas.append(r)
        return datas

    @rpc
    def get_by_type(self, type):
        result = self.log.find({'type': type}).sort({'ctime': -1})
        datas = []
        for r in result:
            r['id'] = str(r['_id'])
            r.pop('_id')
            datas.append(r)
        return datas

    @rpc
    def clear_logging(self):
        try:
            result = self.log.delete_many({})
            return result.deleted_count
        except:
            return 0
