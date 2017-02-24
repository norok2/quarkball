#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
quarkball2017: tests for base classes
"""

# ======================================================================
# :: Imports
from __future__ import (
    division, absolute_import, print_function, unicode_literals)

import os
import datetime
import shutil

import numpy as np

from quarkball.utils import Network, Caching
from quarkball.fill_caching import CachingRandom, CachingRandomSeed

DIRPATH = 'data'
IN_DIRPATH = os.path.join(DIRPATH, 'input')
OUT_DIRPATH = os.path.join(DIRPATH, 'output')
SOURCES = (
    'kittens', 'me_at_the_zoo', 'trending_today', 'videos_worth_spreading',)


# ======================================================================
def test_network_input(
        in_dirpath=IN_DIRPATH,
        sources=SOURCES):
    for source in sources:
        in_filepath = os.path.join(in_dirpath, source + '.in')
        network = Network.load(in_filepath)
        print(network)


# ======================================================================
def test_caching_output(
        in_dirpath=OUT_DIRPATH,
        source='example'):
    in_filepath = os.path.join(in_dirpath, source + '.out')
    caching = Caching.load(in_filepath)
    print(caching)
    out_filepath = os.path.join(in_dirpath, 'test_' + source)
    caching.save(out_filepath)


# ======================================================================
def test_score(
        in_dirpath=IN_DIRPATH,
        out_dirpath=OUT_DIRPATH,
        source='example'):
    in_filepath = os.path.join(in_dirpath, source + '.in')
    network = Network.load(in_filepath)
    print(network)
    out_filepath = os.path.join(out_dirpath, source + '.out')
    caching = Caching.load(out_filepath)
    print(caching.score(network))


# ======================================================================
def test_fill(
        in_dirpath=IN_DIRPATH,
        out_dirpath=OUT_DIRPATH,
        source='example'):
    in_filepath = os.path.join(in_dirpath, source + '.in')
    network = Network.load(in_filepath)
    out_filepath = os.path.join(out_dirpath, source + '.out')
    caching = CachingRandom(network.num_caches)
    caching.fill(network)
    print(repr(caching))
    print('Random Caching - Score: {}'.format(caching.score(network)))


# ======================================================================
def test_method(
        in_dirpath=IN_DIRPATH,
        out_dirpath=OUT_DIRPATH,
        sources=SOURCES,
        caching_method=Caching):
    tot_score = 0
    for source in sources:
        in_filepath = os.path.join(in_dirpath, source + '.in')
        network = Network.load(in_filepath)
        out_filepath = os.path.join(out_dirpath, source + '.out')
        caching = caching_method(network.num_caches)
        caching.fill(network)
        caching.save(out_filepath)
        score = caching.score(network)
        tot_score += score
        print('{} score: {}'.format(source, score))
    print('\nTOTAL SCORE: {}\n'.format(tot_score))


# ======================================================================
def pseudo_monte_carlo(
        in_dirpath=IN_DIRPATH,
        out_dirpath=OUT_DIRPATH,
        dst_subpath='pseudo_monte_carlo',
        sources=SOURCES,
        caching_method=CachingRandomSeed,
        max_iter=4 * 60 * 24,
        min_score=2652000):
    print('Pseudo Monte Carlo simulation')
    dst_dirpath = os.path.join(out_dirpath, dst_subpath)
    if not os.path.isdir(dst_dirpath):
        os.makedirs(dst_dirpath)

    # read all networks
    networks = {}
    for source in sources:
        in_filepath = os.path.join(in_dirpath, source + '.in')
        networks[source] = Network.load(in_filepath)

    # find out the best score from previous iterations
    max_tot_score = 0
    for source in sources:
        network = networks[source]
        dst_filepath = os.path.join(dst_dirpath, source + '.out')
        caching = Caching.load(dst_filepath)
        score = caching.score(network)
        max_tot_score += score
    print('Best score found: {}'.format(max_tot_score))

    # explore the solution subspace randomly, saving best results
    j = 0
    scores = []
    while j < max_iter and max_tot_score < min_score:
        tot_score = 0
        for source in sources:
            network = networks[source]
            out_filepath = os.path.join(out_dirpath, source + '.out')
            caching = caching_method(network.num_caches)
            caching.fill(network)
            caching.save(out_filepath)
            score = caching.score(network)
            tot_score += score
            print('{}: {}'.format(source[:5], score), end=', ')
        print('TOTAL: {}'.format(tot_score))
        if tot_score > max_tot_score:
            for source in sources:
                src = os.path.join(out_dirpath, source + '.out')
                dst = os.path.join(dst_dirpath, source + '.out')
                if os.path.isfile(dst):
                    os.remove(dst)
                shutil.copy(src, dst)
            max_tot_score = tot_score
            print('New max score found: {}'.format(max_tot_score))
        scores.append(tot_score)
        j += 1

    print('\nStatistics (of current batch):')
    scores = np.array(scores)
    for f in ('min', 'max', 'mean', 'std', 'median'):
        print('{:>7s} = {}'.format(f, getattr(np, f)(scores)))




# ======================================================================
def main():
    print(__doc__)
    begin_time = datetime.datetime.now()

    # test_network_input()
    # test_caching_output()
    # test_score()
    # test_fill()
    # test_method(caching_method=CachingRandom)
    pseudo_monte_carlo()

    end_time = datetime.datetime.now()
    print('\nExecTime: {}'.format(end_time - begin_time))


# ======================================================================
if __name__ == '__main__':
    main()
