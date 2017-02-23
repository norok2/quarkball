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
    'kittens.in', 'me_at_the_zoo.in', 'trending_toda.in',
    'videos_worth_spreading.in')


# ======================================================================
def my_test_input(
        in_dirpath=IN_DIRPATH,
        sources=SOURCES):
    for source in sources:
        in_filepath = os.path.join(in_dirpath, source)
        utils.load(in_filepath)


# ======================================================================
def main():
    print(__doc__.strip())
    begin_time = datetime.datetime.now()

    my_test_input()

    end_time = datetime.datetime.now()
    print('ExecTime: {}'.format(end_time - begin_time))


# ======================================================================
if __name__ == '__main__':
    main()
