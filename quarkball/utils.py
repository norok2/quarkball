#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
quarkball2017: base classes
"""

# ======================================================================
# :: Imports
from __future__ import (
    division, absolute_import, print_function, unicode_literals)

import random
import multiprocessing
import numpy as np

try:
    from numba import jit
except ImportError:
    print('E: Numba not found!')


    def jit(_):
        return _
else:
    print('I: Using Numba!')


# ======================================================================
class Network(object):
    def __init__(
            self,
            videos,
            endpoint_latencies,
            cache_size,
            cache_latencies,
            requests=None):
        """
        Generate the network.

        Args:
            videos (np.ndarray): The video array.
                The values correspond to the video size in MB.
                The indexes correspond to the video ID.
            endpoint_latencies (np.ndarray): The latency of endpoints.
            cache_size (int): The capacity of each caching server in MB.
            cache_latencies (np.ndarray): The cache latency of endpoints.
                First dim goes through endpoints.
                Second dim goes through caches.
            requests (list[tuple]): The list of requests.
                Each tuple contains:
                - the video ID;
                - the requesting endpoint;
                - the number of requests.
        """
        self.videos = videos
        self.endpoint_latencies = endpoint_latencies
        self.cache_size = cache_size
        self.cache_latencies = cache_latencies
        self._requests = requests

    # ----------------------------------------------------------
    @property
    def num_videos(self):
        return len(self.videos)

    # ----------------------------------------------------------
    @property
    def num_endpoints(self):
        return len(self.endpoint_latencies)

    # ----------------------------------------------------------
    @property
    def num_caches(self):
        return self.cache_latencies.shape[1]

    # ----------------------------------------------------------
    @property
    def num_requests(self):
        return len(self.requests)

    # ----------------------------------------------------------
    @property
    def requests(self):
        return self._requests

    # ----------------------------------------------------------
    @requests.setter
    def requests(self, value):
        self._requests = value

    # ----------------------------------------------------------
    def __str__(self):
        text = '{}: '.format(self.__class__.__name__)
        names = ['num_videos', 'num_endpoints', 'num_caches', 'num_requests']
        for name in names:
            text += '{}={}  '.format(name, getattr(self, name))
        return text

    # ----------------------------------------------------------
    def __repr__(self):
        return str(self.__dict__)

    # ----------------------------------------------------------
    @classmethod
    def load(cls, filepath):
        with open(filepath, 'r') as file:
            num_videos, num_endpoints, num_requests, num_caches, cache_size = [
                int(val) for val in file.readline().split()]
            videos = np.array([int(v) for v in file.readline().split()])
            endpoint_latencies = np.zeros(num_endpoints)
            cache_latencies = np.zeros((num_endpoints, num_caches))
            for i in range(num_endpoints):
                endpoint_latencies[i], lines_to_read = [
                    int(val) for val in file.readline().split()]
                for j in range(lines_to_read):
                    k, latency = [int(v) for v in file.readline().split()]
                    cache_latencies[i, k] = latency
            requests = []
            for i in range(num_requests):
                requests.append(
                    tuple(int(val) for val in file.readline().split()))
        self = cls(
            videos, endpoint_latencies, cache_size, cache_latencies, requests)
        return self

    # ----------------------------------------------------------
    def save(self, filepath):
        with open(filepath, 'w+') as file:
            num_videos = self.num_videos
            num_endpoints = self.num_endpoints
            num_requests = self.num_requests
            num_caches = self.num_caches
            cache_size = self.cache_size

            #     , num_endpoints, num_requests, num_caches, cache_size = [
            #     int(val) for val in file.readline().split()]
            # videos = np.array([int(v) for v in file.readline().split()])
            # endpoint_latencies = np.zeros(num_endpoints)
            # cache_latencies = np.zeros((num_endpoints, num_caches))
            # for i in range(num_endpoints):
            #     endpoint_latencies[i], lines_to_read = [
            #         int(val) for val in file.readline().split()]
            #     for j in range(lines_to_read):
            #         k, latency = [int(v) for v in file.readline().split()]
            #         cache_latencies[i, k] = latency
            # requests = []
            # for i in range(num_requests):
            #     requests.append([int(val) for val in file.readline().split()])

    # ----------------------------------------------------------
    def score(self, caching):
        return _score(
            caching.caches, self.requests, self.cache_latencies,
            self.endpoint_latencies)


# ======================================================================
class Caching(object):
    def __init__(
            self,
            caches=None):
        """
        Caching of videos.

        Args:
            caches (list[set]): The videos contained in each caching server.
                The information on the cache size (maximum memory available)
                and videos' size is not stored here.
        """
        try:
            iter(caches)
        except TypeError:
            if caches > 0:
                caches = [set() for i in range(caches)]
            else:
                raise AttributeError(
                    'Either `caches` or `num_caches` must be supplied!')
        finally:
            self._caches = caches

    # ----------------------------------------------------------
    @property
    def num_caches(self):
        return len(self.caches)

    # ----------------------------------------------------------
    @property
    def caches(self):
        return self._caches

    # ----------------------------------------------------------
    @caches.setter
    def caches(self, value):
        self._caches = value

    # ----------------------------------------------------------
    def __str__(self):
        text = '{}: '.format(self.__class__.__name__)
        names = ['num_caches']
        for name in names:
            text += '{}={}  '.format(name, getattr(self, name))
        return text

    # ----------------------------------------------------------
    def __repr__(self):
        return str(self.__dict__)

    # ----------------------------------------------------------
    @classmethod
    def load(cls, filepath):
        self = cls([])
        with open(filepath, 'r') as file:
            num_caching = int(file.readline())
            for i in range(num_caching):
                data = [int(val) for val in file.readline().split()]
                # index = data[0]
                self.caches.append(set(data[1:]))
        return self

    # ----------------------------------------------------------
    def save(self, filepath):
        with open(filepath, 'w+') as file:
            file.write(str(len(self.caches)) + '\n')
            for i, server in enumerate(self.caches):
                file.write(
                    '{} {}\n'.format(i, ' '.join([str(val) for val in server])))

    # ----------------------------------------------------------
    def validate(self, videos, cache_size):
        is_valid = True
        for cached_videos in self.caches:
            if cached_videos:
                avail_cache = cache_size
                for cached_video in cached_videos:
                    avail_cache -= videos[cached_video]
                is_valid = is_valid and (avail_cache >= 0)
            if not is_valid:
                break
        return is_valid

    # ----------------------------------------------------------
    def score(self, network):
        return _score(
            self.caches, network.requests, network.cache_latencies,
            network.endpoint_latencies)

    # ----------------------------------------------------------
    def clear(self):
        self.caches = [set() for i in range(self.num_caches)]

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
@jit
def _score(caches, requests, cache_latencies, endpoint_latencies):
    score = 0
    num_tot = 0
    for video, endpoint, num in requests:
        num_tot += num
        latency = max_latency = endpoint_latencies[endpoint]
        for cache, videos in enumerate(caches):
            if video in videos:
                cache_latency = cache_latencies[endpoint, cache]
                if cache_latency and cache_latency < latency:
                    latency = cache_latencies[endpoint, cache]
        score += (max_latency - latency) * num
    score = int(score / num_tot * 1000)
    return score


# ======================================================================
def _score_par(caches, requests, cache_latencies, endpoint_latencies):
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    scores, nums = [], []
    results = [
        pool.apply_async(
            _score_request,
            (caches, video, endpoint, num, cache_latencies, endpoint_latencies))
        for video, endpoint, num in requests]
    # todo
    scores, nums = zip(*results)


# ======================================================================
def _score_request(
        caches, video, endpoint, num, cache_latencies, endpoint_latencies):
    latency = max_latency = endpoint_latencies[endpoint]
    for cache, videos in enumerate(caches):
        if video in videos:
            cache_latency = cache_latencies[endpoint, cache]
            if cache_latency and cache_latency < latency:
                latency = cache_latencies[endpoint, cache]
    score = (max_latency - latency) * num
    return score, num
