#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
quarkball2017
"""

# ======================================================================
# :: Future Imports
from __future__ import (
    division, absolute_import, print_function, unicode_literals)


import numpy as np

# ======================================================================
# :: data structures example
# istance = dict(
#     videos=np.array(num_videos, dtype=int),
#     num_endpoints=int,
#     requests=list((video, endpoint, num)),
#     num_caches=int,
#     cache_size=int,
#     latencies=np.array(dtype=int).shape((num_endpoints, num_caches))
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

    Returns:

    """
    scoring = 0

    return scoring
