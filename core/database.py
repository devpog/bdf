import pymongo
import json
import datetime
import time

import pandas as pd

from pymongo import ReturnDocument


class Database:
    def __init__(self, name, collection='commodity', host='localhost', port=27017):
        # passed
        self.__name, self.__collection = name, collection
        self.__host, self.__port = host, port

        # static
        self.__ts_field = 'date'
        self.__column = 'commodity'

        # dynamic
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

    def populate_records(self, data):
        data.sort_values(['date'], ascending=[0], inplace=True)
        self.__db[self.__collection].insert_many(data.to_dict('records'), ordered=False)

    def get_last_record(self, commodity):
        return self.__db[self.__collection].find_one(
            {self.__column: commodity},
            sort=[(self.__ts_field, pymongo.DESCENDING)])['date']

    def add_records(self, data, commodity):
        last_updated = self.get_last_record(commodity)
        last_record = data[data[self.__ts_field] == last_updated]
        new_records = data[data[self.__ts_field] > last_updated]

        last_record_d = json.loads(last_record.to_json(orient='records', date_format='iso')[1:-1])

        self.__db[self.__collection].update_one(
            {'{0}'.format(self.__ts_field): last_updated},
            {'$set': last_record_d},
            upsert=False)

        if len(new_records) > 0:
            self.populate_records(new_records)
        else:
            pass

        return new_records

    def get_commodity(self, commodity):
        return self.__db[self.__collection].find(
            {self.__column: commodity},
            sort=[(self.__ts_field, pymongo.DESCENDING)])

    @property
    def data(self):
        return self.__db[self.__collection].find(sort=[(self.__ts_field, pymongo.DESCENDING)])

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

