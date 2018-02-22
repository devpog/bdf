#!/usr/bin/env python

"""
Init
    - load libraries
    - define directories
"""

import re
import os
import sys
import optparse
import logging

from core.commodity import *
from core.database import *


def main():

    # Set working directories
    cwd = os.path.dirname(sys.argv[0])
    data_dir = os.path.join(cwd, 'data')

    log_dir = os.path.join(cwd, 'log')
    log_file = os.path.join(log_dir, 'commodity.log')

    # Define logger and its config
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Set args parser
    parser = optparse.OptionParser()

    # commodity option
    parser.add_option('-c', '--commodity',
                      dest='commodity',
                      help='commodity to work with [default: %default]')
    # init option
    parser.add_option('-i', '--init', '--initialize',
                      action='store_true', dest='init',
                      help='initial database population [default: %default]')
    # price option
    parser.add_option('-p', '--price',
                      action='store_true', dest='price',
                      help='calculate price [default: %default]')

    # commodity option
    parser.add_option('-s', '--start_date',
                      dest='start_date',
                      help='start date for price calculation [default: %default]')

    parser.add_option('-e', '--end_date',
                      dest='end_date',
                      help='start date for price calculation [default: %default]')

    parser.set_defaults(commodity='gold', init=False, price=False, start_date=None, end_date=None)
    opts, args = parser.parse_args()

    # Parse input params
    commodity = opts.commodity
    run_init = opts.init
    get_price = opts.price
    start_date = opts.start_date
    end_date = opts.end_date

    # Set database
    db = Database(name='bdf')

    # Set commodity
    comm = Commodity(name=commodity)

    if run_init and not get_price:
        logger.info('initial run...')
        logger.info('adding records for {0}'.format(commodity))

        db.populate_records(comm.data)
        logger.info('{0} records added'.format(len(comm.data)))
        exit(0)
    elif not run_init and not get_price:
        logger.info('updating records for {0}'.format(commodity))
        data = db.add_records(comm.data, commodity)
        if len(data) > 0:
            logger.info('{0} records added'.format(len(data)))
        else:
            logger.info("updated today's record".format(len(data)))
        exit(0)
    elif not run_init and get_price:
        p = re.compile(r'\d{4}-\d{2}-\d{2}')
        if start_date is not None and end_date is not None:
            if not p.match(start_date) or not p.match(end_date):
                print('date error: parameters start_date or end_date must be in a form of YYYY-MM-DD')
            else:
                data = db.get_stats(commodity=commodity, metric='price', start_date=start_date, end_date=end_date)
                print(data)
                exit(0)


if __name__ == '__main__':
    main()
