import requests

import pandas as pd
import numpy as np

from random import choice
from lxml import html
from bs4 import BeautifulSoup


class Commodity:
    def __init__(self, name):
        # passed
        self.__name = name

        # dynamic
        self.__url_path = 'https://www.investing.com/commodities/{0}-historical-data'.format(name)

    def fetch_price(self):
        # various user agents to iterate over
        user_agents = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']

        # randomly pick user agent
        def get_headers():
            return {'User-Agent': choice(user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}

        # get web page
        r = requests.get(self.__url_path, headers=get_headers())
        bs = BeautifulSoup(r.text, "lxml")

        # get table with historical prices
        table = bs.find_all('table')[3]

        # get headers
        headers = [e.get_text().lower().replace('.', '').replace('%', '').strip() for e in table.find_all('th')]

        # find all rows, excluding headers
        rows = table.find_all('tr')[1:]

        # parse table getting headers and rows
        data = [[e.get_text() for e in row.find_all('td')] for row in rows]
        df = pd.DataFrame(data, columns=headers)

        # change column types
        for col in df.columns:
            if col == 'date':
                df[col] = pd.to_datetime(df[col])
            elif col == 'vol':
                df[col] = df[col].apply(lambda x: x.replace('K', '').replace('-', '0')).astype('float') * 1000
            elif col == 'change':
                df[col] = df[col].apply(lambda x: x.replace('%', '')).astype('float') * 0.01
            else:
                df[col] = df[col].apply(lambda x: x.replace(',', '')).astype('float')

        # add commodity name and re-order columns
        df['commodity'] = self.__name
        columns = df.columns.tolist()
        columns.insert(1, 'commodity')

        # remove duplicated column name
        columns.pop()

        # re-arrange columns
        df = df[columns]

        # set index for TS processing
        df.set_index('date', inplace=True)

        return df

    def store(self):
        pass

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def data(self):
        return self.fetch_price()
