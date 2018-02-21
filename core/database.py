import pymongo
import datetime
import time


class Database:
    def __init__(self, name, collection='commodity', host='localhost', port=27017):

        self.__name, self.__collection = name, collection

        self.__host, self.__port = host, port

        self.__conn = pymongo.MongoClient(host=self.__host, port=self.__port)
        self.__db = self.conn[self.__name]

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

    def add_records(self, data):
        self.__db[self.__collection].insert_many(data.to_dict('records'))

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
