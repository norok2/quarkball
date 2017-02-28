#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random
import itertools
import datetime
import operator
import shutil
import copy
import multiprocessing
import time

import numpy as np

from quarkball.utils import Network, Caching, jit


# random.seed(0)


# ======================================================================
def _random_cache(videos, avail_cache, min_video_size=None):
    if min_video_size is None:
        min_video_size = np.min(videos)
    new_videos = list(range(len(videos)))
    cache = set()
    random.shuffle(new_videos)
    for new_video in new_videos:
        video_size = videos[new_video]
        if video_size <= avail_cache:
            cache.add(new_video)
            avail_cache -= video_size
        if min_video_size > avail_cache:
            break
    return cache


# ======================================================================
def _breeding(pool, network, crossover=0.5, mutation_rate=0.1, mutation=0.01):
    pool = sorted(pool, key=operator.itemgetter(0), reverse=True)
    score, caching = copy.deepcopy(pool[0])
    min_video_size = np.min(network.videos)
    if crossover is None:
        raise NotImplementedError('Dynamic recombination not implemented!')
    else:
        # crossover
        other_caching = pool[1][1]
        for i in random.sample(range(network.num_caches),
                               int(network.num_caches * (1 - crossover))):
            caching.caches[i] = copy.deepcopy(other_caching.caches[i])

        # mutation
        if random.random() >= mutation_rate:
            for i in random.sample(range(network.num_caches),
                                   int(network.num_caches * mutation)):
                caching.caches[i] = _random_cache(
                    network.videos, network.cache_size, min_video_size)
    score = caching.score(network)
    return score, caching


# ======================================================================
class CachingRandomPar(Caching):
    def __init__(self, *args, **kwargs):
        Caching.__init__(self, *args, **kwargs)

    # ----------------------------------------------------------
    def fill(self, network):
        min_video_size = np.min(network.videos)
        mp_pool = multiprocessing.Pool(multiprocessing.cpu_count())
        results = [
            mp_pool.apply_async(
                _random_cache,
                (network.videos, network.cache_size, min_video_size))
            for i in range(self.num_caches)]
        self.caches = [result.get() for result in results]
        mp_pool = None


# ======================================================================
class CachingRandomSeed(Caching):
    def __init__(self, *args, **kwargs):
        Caching.__init__(self, *args, **kwargs)

    # ----------------------------------------------------------
    def fill(self, network):
        min_video_size = np.min(network.videos)
        new_videos = list(range(network.num_videos))
        random.shuffle(new_videos)
        for cache in self.caches:
            avail_cache = network.cache_size
            for new_video in new_videos:
                video_size = network.videos[new_video]
                if video_size <= avail_cache:
                    cache.add(new_video)
                    avail_cache -= video_size
                if min_video_size > avail_cache:
                    break


# ======================================================================
class CachingMonteCarlo(Caching):
    def __init__(self, *args, **kwargs):
        Caching.__init__(self, *args, **kwargs)

    # ----------------------------------------------------------
    def fill(self, network, filepath=None, max_iter=int(1e10)):
        filename = os.path.basename(filepath)
        if os.path.isfile(filepath):
            curr_caching = Caching.load(filepath)
            curr_score = curr_caching.score(network)
            print('montecarlo partial best - {:20s} SCORE: {}'.format(
                filename, curr_score), flush=True)
        else:
            curr_score = 0
        begin_time = datetime.datetime.now()
        j = 0
        while j < max_iter:
            min_video_size = np.min(network.videos)
            self.caches = [
                _random_cache(
                    network.videos, network.cache_size, min_video_size)
                for i in range(self.num_caches)]
            score = self.score(network)
            end_time = datetime.datetime.now()
            print('montecarlo - {:20s} SCORE: {:7d}  ({})  j={}, t={}'.format(
                filename, score, curr_score, j, end_time - begin_time),
                flush=True)
            begin_time = end_time
            if score > curr_score:
                curr_score = score
                best_caches = self.caches
                print('montecarlo partial best - {:20s} SCORE: {}'.format(
                    filename, score), flush=True)
                self.save(filepath)
            j += 1


# ======================================================================
class CachingBruteForce(Caching):
    def __init__(self, *args, **kwargs):
        Caching.__init__(self, *args, **kwargs)

    # ----------------------------------------------------------
    def fill(self, network, filepath=None):
        print('Working on `{}`'.format(filepath), flush=True)
        filename = os.path.basename(filepath)
        max_videos = np.sum(
            np.cumsum(np.sort(network.videos)) < network.cache_size)
        print('max num videos: {}'.format(max_videos), flush=True)
        possible_caches = []
        for uncut_cache in \
                itertools.combinations(range(network.num_videos), max_videos):
            cut_size = np.sum(
                np.cumsum([network.videos[i]
                           for i in uncut_cache]) < network.cache_size)
            possible_caches.append(uncut_cache[:cut_size])
        print('num caches poss.: {}'.format(len(possible_caches)), flush=True)
        curr_score = 0
        best_caches = None
        for caches in \
                itertools.combinations(possible_caches, network.num_caches):
            self.caches = caches
            score = self.score(network)
            print('bruteforce partial - {:20s} SCORE: {}'.format(
                filename, score), flush=True)
            if score > curr_score:
                curr_score = score
                best_caches = caches
                print('bruteforce partial best - {:20s} SCORE: {}'.format(
                    filename, score), flush=True)
                self.save(filepath)
        self.caches = best_caches


# ======================================================================
class CachingEvolution(Caching):
    def __init__(self, *args, **kwargs):
        Caching.__init__(self, *args, **kwargs)

    # ----------------------------------------------------------
    def fill(
            self,
            network,
            filepath=None,
            max_generations=int(1e7 - 1),
            pool_size=400,
            selection=0.5,
            crossover=0.6,
            mutation_rate=0.05,
            mutation=0.1,
            elitism=0.005,
            multiproc=True):
        dirpath = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        basename = os.path.splitext(filename)[0]
        evo_dirpath = os.path.join(dirpath, basename)
        old_evo_dirpath = os.path.join(dirpath, '_old_' + basename)

        if not os.path.isdir(evo_dirpath):
            os.makedirs(evo_dirpath)

        pool_filenames, pool_dirpath = [], ''
        if os.path.isdir(evo_dirpath):
            pool_filenames = os.listdir(evo_dirpath)
            pool_dirpath = evo_dirpath
        if len(pool_filenames) != pool_size and os.path.isdir(old_evo_dirpath):
            pool_filenames = os.listdir(old_evo_dirpath)
            pool_dirpath = old_evo_dirpath
        if len(pool_filenames) != pool_size:
            pool = []
            if os.path.isfile(filepath):
                caching = Caching.load(filepath)
                pool.append((caching.score(network), caching))
            for _ in range(pool_size - len(pool)):
                caching = Caching(network.num_caches)
                caching.fill(network)
                pool.append((caching.score(network), caching))
        else:
            pool = [
                (int(name.split('_')[0]),
                 Caching.load(os.path.join(pool_dirpath, name)))
                for name in pool_filenames]

        pool = sorted(pool, key=operator.itemgetter(0), reverse=True)

        begin_time = datetime.datetime.now()
        generation = 0
        best_score = pool[0][0]
        mp_pool = multiprocessing.Pool(multiprocessing.cpu_count()) \
            if multiproc else None
        while generation < max_generations:
            # selection
            selected = pool[:int(pool_size * selection)]

            # elitism
            elite = copy.deepcopy(pool[:int(pool_size * elitism) + 1])

            # crossover and mutate
            num_generators = 2

            if multiproc:
                results = [
                    mp_pool.apply_async(
                        _breeding,
                        ([selected[i] for i in sorted(random.sample(
                            range(len(selected)), num_generators))],
                         network, crossover, mutation_rate, mutation))
                    for _ in range(pool_size - len(elite))]
                offspring = [result.get() for result in results]
            else:
                offspring = [
                    _breeding([selected[i] for i in sorted(random.sample(
                        range(len(selected)), num_generators))], network,
                              crossover, mutation_rate, mutation)
                    for _ in range(pool_size - len(elite))]
            pool = elite + offspring

            # delete old generation
            if os.path.isdir(old_evo_dirpath):
                shutil.rmtree(old_evo_dirpath, ignore_errors=True)
                shutil.rmtree(old_evo_dirpath, ignore_errors=True)
            shutil.move(evo_dirpath, old_evo_dirpath)
            os.makedirs(evo_dirpath)

            # save new generation
            pool = sorted(pool, key=operator.itemgetter(0), reverse=True)
            [caching.save(
                os.path.join(evo_dirpath,
                             '{:07d}_id{:04d}_gen{:06d}__'.format(
                                 score, i, generation) + filename))
             for i, (score, caching) in enumerate(pool)]

            if pool[0][0] > best_score:
                pool[0][1].save(filepath)
                best_score = pool[0][0]

            end_time = datetime.datetime.now()
            print('evolution - {:20s} SCORE: {:7d}, gen={}, t={}'.format(
                filename, best_score, generation, end_time - begin_time),
                flush=True)
            begin_time = end_time

            generation += 1

        # return best result
        self.caches = pool[0][1].caches


# ======================================================================
class CachingOptimByRequests(Caching):
    def __init__(self, *args, **kwargs):
        Caching.__init__(self, *args, **kwargs)

    # ----------------------------------------------------------
    def fill(self, network):
        # sort requests by number of requests divided by video size
        sorted_requests = sorted(
            network.requests,
            key=lambda x: x[2] / network.videos[x[1]], reverse=True)
        # key=lambda x: x[2])[::-1]
        # min_video_size = np.min(network.videos)
        free_caches = np.ones(network.num_caches) * network.cache_size
        cached_requests = []
        for request in sorted_requests:
            if request not in cached_requests:
                new_video, endpoint, num = request
                # sorted_caches = np.argsort(
                #     network.cache_latencies[endpoint, :])
                sorted_caches = np.argsort(
                    network.cache_latencies[endpoint, :] / (free_caches + 1))
                sorted_caches = sorted_caches[
                    network.cache_latencies[endpoint, :] > 0]
                for i in list(sorted_caches):
                    video_size = network.videos[new_video]
                    if (video_size <= free_caches[i] and
                                new_video not in self.caches[i]):
                        self.caches[i].add(new_video)
                        free_caches[i] -= video_size
                        cached_requests.append(request)


# ======================================================================
class CachingOptimByCaches(Caching):
    def __init__(self, *args, **kwargs):
        Caching.__init__(self, *args, **kwargs)

    # ----------------------------------------------------------
    def fill(self, network):
        # sort requests by number of requests divided by video size
        sorted_requests = sorted(
            network.requests,
            key=lambda x: x[2] / network.videos[x[1]], reverse=True)
        # key=lambda x: x[2])[::-1]
        min_video_size = np.min(network.videos)
        free_caches = np.ones(network.num_caches) * network.cache_size
        cached_requests = []
        for i, cache in enumerate(self.caches):
            for request in sorted_requests:
                if request not in cached_requests:
                    new_video, endpoint, num = request
                    video_size = network.videos[new_video]
                    if (video_size <= free_caches[i] and
                                new_video not in cache):
                        cache.add(new_video)
                        free_caches[i] -= video_size
                        cached_requests.append(request)
                if free_caches[i] < min_video_size:
                    break
