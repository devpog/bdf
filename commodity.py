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

    # Set working directories
    cwd = os.getcwd()
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

    parser.set_defaults(commodity='gold', init=False, price=False)
    opts, args = parser.parse_args()

    # Parse input params
    commodity = opts.commodity
    run_init = opts.init

    # Set database
    db = Database(name='bdf')

    # Set commodity
    comm = Commodity(name=commodity)

    if run_init:
        logger.info('initial run...')
        logger.info('adding records for {0}'.format(commodity))

        db.populate_records(comm.data)
        logger.info('{0} records added'.format(len(comm.data)))
    else:
        logger.info('updating records for {0}'.format(commodity))
        data = db.add_records(comm.data, commodity)
        if len(data) > 0:
            logger.info('{0} records added'.format(len(data)))
        else:
            logger.info("updated today's record".format(len(data)))


if __name__ == '__main__':
    main()
