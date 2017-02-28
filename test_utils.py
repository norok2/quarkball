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
import multiprocessing
import profile

import numpy as np

from quarkball.utils import Network, Caching
import quarkball.fill_caching as fill

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
    caching = fill.Caching(network.num_caches)
    caching.fill(network)
    print(repr(caching))
    print('Random Caching - Score: {}'.format(caching.score(network)))


# ======================================================================
def test_method(
        in_dirpath=IN_DIRPATH,
        out_dirpath=OUT_DIRPATH,
        source='example',
        fill_cls=Caching,
        *fill_args,
        **fill_kws):
    if not os.path.isdir(out_dirpath):
        os.makedirs(out_dirpath)
    in_filepath = os.path.join(in_dirpath, source + '.in')
    network = Network.load(in_filepath)
    out_filepath = os.path.join(out_dirpath, source + '.out')
    caching = fill_cls(network.num_caches)
    caching.fill(network, *fill_args, **fill_kws)
    caching.save(out_filepath)
    score = caching.score(network)
    print('{:20s} final score: {}'.format(source, score), flush=True)
    return score


# ======================================================================
def test_method_seq(
        in_dirpath=IN_DIRPATH,
        out_dirpath=OUT_DIRPATH,
        sources=SOURCES,
        fill_cls=Caching,
        *fill_args,
        **fill_kws):
    if not os.path.isdir(out_dirpath):
        os.makedirs(out_dirpath)
    tot_score = 0
    for source in sources:
        in_filepath = os.path.join(in_dirpath, source + '.in')
        network = Network.load(in_filepath)
        out_filepath = os.path.join(out_dirpath, source + '.out')
        caching = fill_cls(network.num_caches)
        caching.fill(network, *fill_args, **fill_kws)
        caching.save(out_filepath)
        score = caching.score(network)
        tot_score += score
        print('{:40s} score: {}'.format(source, score))
    print('\nTOTAL SCORE: {}\n'.format(tot_score))


# ======================================================================
def test_method_par(
        in_dirpath=IN_DIRPATH,
        out_dirpath=OUT_DIRPATH,
        sources=SOURCES,
        fill_cls=Caching,
        *fill_args,
        **fill_kws):
    if not os.path.isdir(out_dirpath):
        os.makedirs(out_dirpath)
    tot_score = 0
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    results = [
        pool.apply_async(
            test_method,
            (in_dirpath, out_dirpath, source, fill_cls,) + fill_args,
            fill_kws)
        for source in sources]
    for result in results:
        tot_score += result.get()
    print('\nTOTAL SCORE: {}\n'.format(tot_score))


# ======================================================================
def bruteforce(
        in_dirpath=IN_DIRPATH,
        out_dirpath=os.path.join(OUT_DIRPATH, 'bruteforce'),
        sources=SOURCES):
    print('Bruteforce')
    if not os.path.isdir(out_dirpath):
        os.makedirs(out_dirpath)
    tot_score = 0
    mp_pool = multiprocessing.Pool(multiprocessing.cpu_count())
    results = [
        mp_pool.apply_async(
            test_method,
            (in_dirpath, out_dirpath, source, fill.CachingBruteForce,
             os.path.join(out_dirpath, source + '.out')))
        for source in sources]
    for result in results:
        tot_score += result.get()
    print('\nTOTAL SCORE: {}\n'.format(tot_score))


# ======================================================================
def montecarlo(
        in_dirpath=IN_DIRPATH,
        out_dirpath=os.path.join(OUT_DIRPATH, 'montecarlo'),
        source='example',
        max_iter=int(1e8 - 1)):
    print('Montecarlo')
    if not os.path.isdir(out_dirpath):
        os.makedirs(out_dirpath)
    test_method(
        in_dirpath, out_dirpath, source, fill.CachingMonteCarlo,
        os.path.join(out_dirpath, source + '.out'), max_iter)


# ======================================================================
def evolution(
        in_dirpath=IN_DIRPATH,
        out_dirpath=os.path.join(OUT_DIRPATH, 'evolution'),
        source='example',
        max_generations=int(1e8 - 1),
        pool_size=400,
        selection=0.5,
        crossover=0.6,
        mutation_rate=0.05,
        mutation=0.1,
        elitism=0.005,
        multiproc=True):
    print('Evolution')
    if not os.path.isdir(out_dirpath):
        os.makedirs(out_dirpath)
    test_method(
        in_dirpath, out_dirpath, source, fill.CachingEvolution,
        os.path.join(out_dirpath, source + '.out'), max_generations, pool_size,
        selection, crossover, mutation_rate, mutation, elitism, multiproc)


# ======================================================================
def main():
    print(__doc__)
    begin_time = datetime.datetime.now()

    # test_network_input()
    # test_caching_output()
    # test_score()
    # test_fill()
    # pseudo_monte_carlo()
    # bruteforce()
    # montecarlo(sources=SOURCES[1])
    # evolution(source=SOURCES[0])
    evolution(source=SOURCES[1], multiproc=False)
    # profile.run(
    #     "test_method(source=SOURCES[3], fill_cls=fill.Caching)")

    end_time = datetime.datetime.now()
    print('\nExecTime: {}'.format(end_time - begin_time))


# ======================================================================
if __name__ == '__main__':
    main()
