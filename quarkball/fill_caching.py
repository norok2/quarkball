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
        caches_free = np.ones(network.num_caches) * network.cache_size
        for i, cache in enumerate(self.caches):
            while min_video_size < caches_free[i]:
                new_video = random.randint(0, network.num_videos - 1)
                video_size = network.videos[new_video]
                if video_size <= caches_free[i] and new_video not in cache:
                    cache.add(new_video)
                    caches_free[i] -= video_size


# ======================================================================
class CachingRandomSeed(Caching):
    def __init__(self, *args, **kwargs):
        Caching.__init__(self, *args, **kwargs)

    # ----------------------------------------------------------
    def fill(self, network):
        min_video_size = np.min(network.videos)
        caches_free = np.ones(network.num_caches) * network.cache_size
        for i, cache in enumerate(self.caches):
            new_video = random.randint(0, network.num_videos - 1)
            j = 0
            while min_video_size < caches_free[i] and j < network.num_videos:
                video_size = network.videos[new_video]
                if video_size <= caches_free[i] and new_video not in cache:
                    cache.add(new_video)
                    caches_free[i] -= video_size
                else:
                    new_video = (new_video + 1) % network.num_videos
                j += 1


# ======================================================================
class CachingBruteForce(Caching):
    def __init__(self, *args, **kwargs):
        Caching.__init__(self, *args, **kwargs)

    # ----------------------------------------------------------
    def fill(self, network):
        pass

