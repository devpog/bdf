import pymongo
import datetime
import time

class Database:
    def __init__(self, id, collection='commodity', name=None, host='localhost', port=27017):

        self.__id, self.__collection = id, collection
        self.__name = name if name is not None else id

        self.__host, self.__port = host, port

        self.__conn = pymongo.MongoClient(host=self.__host, port=self.__port)
        self.__db = self.conn[self.__id]

    def __enter__(self):
        return self.__db

    def __exit__(self):
        self.__conn.close()

    def close(self):
        self.__conn.close()

    def reconnect(self):
        self.__exit__()
        self.__enter__()
        return self.__db

    def get_last_record(self, symbol):
        cursor = self.__db[self.__collection].find({self.__sname: symbol}).sort(self.__ts_field, -1)
        last_record = cursor[0][self.__ts_field]
        return last_record

    def add_records(self, data):
        self.__db[self.__collection].insert_many(data.to_dict('records'))

    def get_records(self, symbol, start_date=None, end_date=None):
        now = datetime.datetime.now()
        if start_date is not None:
            start_date = int(time.mktime(datetime.datetime.strptime(start_date, "%Y-%m-%d").timetuple()))
        else:
            start_date = now

        if end_date is not None:
            end_date = int(time.mktime(datetime.datetime.strptime(end_date, "%Y-%m-%d").timetuple()))
        else:
            end_date = now - datetime.timedelta(days=1)

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def host(self):
        return self.__host

    @property
    def port(self):
        return self.__port

    @property
    def conn(self):
        return self.__conn

    @property
    def db(self):
        return self.__db

    @property
    def collection(self):
        return self.__collection

    @collection.setter
    def collection(self, collection):
        self.__collection = collection
