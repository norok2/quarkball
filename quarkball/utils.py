#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
quarkball2017
"""

# ======================================================================
# :: Imports
from __future__ import (
    division, absolute_import, print_function, unicode_literals)

import numpy as np
import numba

# ======================================================================
# :: data structures example
# network = dict(
#     videos=np.array(num_videos, dtype=int),
#     server_latencies=np.array(dtype=int)
#     num_endpoints=int,
#     requests=list((video, endpoint, num)),
#     num_caches=int,
#     cache_size=int,
#     cache_latencies=np.array(dtype=int).shape((num_endpoints, num_caches))
# )
#
# caching= dict(
#     used=int,
#     servers=list(list()),
# )


# ======================================================================
def validate(caching, videos, cache_size):
    """
    Validate a caching.

    Args:
        caching (dict):
        videos (dict):

    Returns:

    """
    is_valid = True
    for files in caching['servers']:
        if files:
            filled = 0
            for file in files:
                filled += videos[file]
            is_valid = is_valid and (filled <= cache_size)
    return is_valid


# ======================================================================
# @numba.jit
def score(caching, requests, cache_latencies, server_latencies):
    """

    Args:
        caching ():
        requests ():
        cache_latencies ():

    Returns:

    """
    scoring = 0
    for video, endpoint, num in requests:
        for cache, videos in enumerate(caching['servers']):
            latency = max_latency = server_latencies[endpoint]
            if video in videos:
                if cache_latencies[endpoint, cache] < latency:
                    latency = cache_latencies[endpoint, cache]
        scoring += (max_latency - latency) * num
    return scoring


# ======================================================================
def load(in_filepath):
    """

    Args:
        in_filepath ():

    Returns:

    """
    network = {}
    with open(in_filepath, 'r') as file:
        names = (
            'num_videos', 'num_endpoints', 'num_requests', 'num_caches',
            'cache_size')
        network.update(
            {k: int(v) for k, v in zip(names, file.readline().split())})
        network['videos'] = np.array([int(v) for v in file.readline().split()])
        network['server_latencies'] = np.zeros(network['num_endpoints'])
        network['cache_latencies'] = np.zeros(
            (network['num_endpoints'], network['num_caches']))
        for i in range(network['num_endpoints']):
            network['server_latencies'][i], lines_to_read = [
                int(v) for v in file.readline().split()]
            for j in range(lines_to_read):
                k, latency = [int(v) for v in file.readline().split()]
                network['cache_latencies'][i, k] = latency
        network['requests'] = []
        for i in range(network['num_requests']):
            network['requests'].append(
                [int(v) for v in file.readline().split()])
    return network


# ======================================================================
def _load_output(in_filepath):
    """

    Args:
        in_filepath ():

    Returns:

    """
    caching = {}
    with open(in_filepath, 'r') as file:
        caching['used'] = int(file.readline())
        caching['servers'] = []
        for i in range(caching['used']):
            data = [int(v) for v in file.readline().split()]
            index = data[0]
            caching['servers'].append(data[1:])
    return caching


# ======================================================================
def save(out_filepath, caching):
    """

    Args:
        out_filepath ():
        caching ():

    Returns:

    """
    with open(out_filepath, 'w+') as file:
        file.write(str(caching['used']) + '\n')
        for i, server in enumerate(caching['servers']):
            file.write(str(i) + ' ' + ' '.join([str(v) for v in server]) + '\n')
