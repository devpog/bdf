#!/usr/bin/env python

"""
Init
    - load libraries
    - define directories
"""

import re
import os
import optparse
import logging

from core.commodity import *
from core.database import *


def main():
    # Define logger and its config
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('etl.log')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    parser = optparse.OptionParser()
    parser.add_option('-c', '--commodity',
                      dest='commodity',
                      help='commodity to work with [default: %default]')
    parser.add_option('-i', '--init', '--initialize',
                      action='store_true', dest='init',
                      help='initial database population [default: %default]')
    parser.set_defaults(commodity='gold', init=False)
    opts, args = parser.parse_args()

    # Parse input params
    commodity = opts.exchange
    run_init = opts.init

    # Set working directories
    cwd = os.getcwd()
    data_dir = os.path.join(cwd, 'data')

    # Set database
    db = Database(name='bdf')

    # Set exchange
    comm = Commodity(name=commodity)

    if run_init:
        logger.info('initial run...')
        for symbol in symbols:
            time.sleep(timeout)
            logger.info('adding records for {0}'.format(symbol))
            data = ex.fetch_ohlcv(symbol)
            db.add_records(data)
            logger.info('{0} records added'.format(len(data)))

    else:
        logger.info('updating records...')
        if currency == 'all':
            symbols = ex.symbols
        else:
            symbols = [x for x in ex.symbols if r.search(x)]

        for symbol in symbols:
            time.sleep(timeout)
            last_update = db.get_last_record(symbol)
            logger.info('adding records for {0}'.format(symbol))
            data = ex.fetch_ohlcv(symbol
                                  )
            update = data.loc[data.time > last_update, :]
            if len(update) > 0:
                db.add_records(update)
                logger.info('{0} records added'.format(len(update)))
            else:
                logger.info('no updates')


if __name__ == '__main__':
    main()
