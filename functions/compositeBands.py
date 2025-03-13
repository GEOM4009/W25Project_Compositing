#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 12 15:34:44 2025

@author: adrianacaswell
"""

import numpy as np

# input - dictionary of 3D arrays
# output - dictionary of 2D arrays that are median value composites


def compositeBands(band_dict):

    for band_name, band_array in band_dict.items():

        band_dict[band_name] = np.median(band_array, axis=0)

    return band_dict


# TODO:
# figure out how to incorperate metadata - might be able to skip for this step though
#   and have metadata out in sort bands and back in in resample
# this needs to be tested
