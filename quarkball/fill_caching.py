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
            cache_free = network.cache_size
            random.shuffle(new_videos)
            for new_video in new_videos:
                video_size = network.videos[new_video]
                if video_size <= cache_free and new_video not in cache:
                    cache.add(new_video)
                    cache_free -= video_size
                if min_video_size > cache_free:
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
            cache_free = network.cache_size
            for new_video in new_videos:
                video_size = network.videos[new_video]
                if video_size <= cache_free and new_video not in cache:
                    cache.add(new_video)
                    cache_free -= video_size
                if min_video_size > cache_free:
                    break


# ======================================================================
class CachingSortRequests(Caching):
    def __init__(self, *args, **kwargs):
        Caching.__init__(self, *args, **kwargs)

    # ----------------------------------------------------------
    def fill(self, network):
        sorted_requests = np.array(network.requests)
        min_video_size = np.min(network.videos)
        new_videos = list(range(network.num_videos))
        for i, cache in enumerate(self.caches):
            cache_free = network.cache_size
            random.shuffle(new_videos)
            for new_video in new_videos:
                video_size = network.videos[new_video]
                if video_size <= cache_free and new_video not in cache:
                    cache.add(new_video)
                    cache_free -= video_size
                if min_video_size > cache_free:
                    break


# ======================================================================
class CachingBruteForce(Caching):
    def __init__(self, *args, **kwargs):
        Caching.__init__(self, *args, **kwargs)

    # ----------------------------------------------------------
    def fill(self, network, id=None):
        pass
