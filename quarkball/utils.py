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
def score(caching, requests):
    """

    Args:
        caching ():
        requests ():

    Returns:

    """
    scoring = 0
    for video, endpoint, num in requests:
        pass

    return scoring


# ======================================================================
def load(in_filepath):
    network = {}
    with open(in_filepath, 'r+') as file:
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
def save(out_filepath, caching):
    return
