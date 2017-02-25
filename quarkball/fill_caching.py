#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import numpy as np

from quarkball.utils import Network, Caching


# random.seed(0)


# ======================================================================
class CachingRandom(Caching):
    def __init__(self, *args, **kwargs):
        Caching.__init__(self, *args, **kwargs)

    # ----------------------------------------------------------
    def fill(self, network):
        min_video_size = np.min(network.videos)
        new_videos = list(range(network.num_videos))
        for i, cache in enumerate(self.caches):
            avail_cache = network.cache_size
            random.shuffle(new_videos)
            for new_video in new_videos:
                video_size = network.videos[new_video]
                if video_size <= avail_cache and new_video not in cache:
                    cache.add(new_video)
                    avail_cache -= video_size
                if min_video_size > avail_cache:
                    break


# ======================================================================
class CachingRandomSeed(Caching):
    def __init__(self, *args, **kwargs):
        Caching.__init__(self, *args, **kwargs)

    # ----------------------------------------------------------
    def fill(self, network):
        min_video_size = np.min(network.videos)
        new_videos = list(range(network.num_videos))
        random.shuffle(new_videos)
        for i, cache in enumerate(self.caches):
            avail_cache = network.cache_size
            for new_video in new_videos:
                video_size = network.videos[new_video]
                if video_size <= avail_cache and new_video not in cache:
                    cache.add(new_video)
                    avail_cache -= video_size
                if min_video_size > avail_cache:
                    break


# ======================================================================
class CachingSortRequests(Caching):
    def __init__(self, *args, **kwargs):
        Caching.__init__(self, *args, **kwargs)

    # ----------------------------------------------------------
    def fill(self, network):
        # sort requests by number of requests divided by video size
        sorted_requests = sorted(
            network.requests, key=lambda x: x[2] / network.videos[x[1]])
        min_video_size = np.min(network.videos)
        new_videos = list(range(network.num_videos))
        free_caches = np.ones(network.num_caches) * network.cache_size
        cached_requests = []
        for request in sorted_requests:
            if request not in cached_requests:
                video, endpoint, num = request
                sorted_caches = np.argsort(
                    network.cache_latencies[endpoint, :])
                for i in list(sorted_caches):
                    # if
                    free_caches[i] = network.cache_size
                    random.shuffle(new_videos)
                    for new_video in new_videos:
                        video_size = network.videos[new_video]
                        if video_size <= free_caches[i] and new_video not in self.caches[i]:
                            self.caches[i].add(new_video)
                            free_caches[i] -= video_size
                        if min_video_size > free_caches[i]:
                            break


# ======================================================================
class CachingBruteForce(Caching):
    def __init__(self, *args, **kwargs):
        Caching.__init__(self, *args, **kwargs)

    # ----------------------------------------------------------
    def fill(self, network, id=None):
        pass
