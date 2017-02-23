#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
quarkball2017
"""

# ======================================================================
# :: Imports
from __future__ import (
    division, absolute_import, print_function, unicode_literals)

import os
import datetime
from quarkball import utils

import numpy as np

DIRPATH = 'data'
IN_DIRPATH = os.path.join(DIRPATH, 'input')
OUT_DIRPATH = os.path.join(DIRPATH, 'output')
SOURCES = (
    'kittens.in', 'me_at_the_zoo.in', 'trending_today.in',
    'videos_worth_spreading.in',
    'example.in',)


# ======================================================================
def my_test_input(
        in_dirpath=IN_DIRPATH,
        sources=SOURCES):
    for source in sources:
        in_filepath = os.path.join(in_dirpath, source)
        network = utils.load(in_filepath)
        print(network['num_endpoints'])



# ======================================================================
def my_test_output(
        in_dirpath=OUT_DIRPATH,
        source='example.out'):
    in_filepath = os.path.join(in_dirpath, source)
    caching = utils._load_output(in_filepath)
    print(caching)
    out_filepath = os.path.join(in_dirpath, 'test_' + source)
    utils.save(out_filepath, caching)


# ======================================================================
def my_test_score(
        in_dirpath=IN_DIRPATH,
        out_dirpath=OUT_DIRPATH,
        source='example'):
    in_filepath = os.path.join(in_dirpath, source + '.in')
    network = utils.load(in_filepath)
    print(network)
    out_filepath = os.path.join(out_dirpath, source + '.out')
    caching = utils._load_output(out_filepath)
    print(utils.score(
        caching, network['requests'], network['cache_latencies'],
        network['server_latencies']))

# ======================================================================
def main():
    print(__doc__)
    begin_time = datetime.datetime.now()

    # my_test_input()
    # my_test_output()
    my_test_score()

    end_time = datetime.datetime.now()
    print('\nExecTime: {}'.format(end_time - begin_time))


# ======================================================================
if __name__ == '__main__':
    main()
