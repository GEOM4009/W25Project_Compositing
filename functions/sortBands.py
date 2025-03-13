#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sort bands.

@author: adrianacaswell
"""

# input - folder of TIFF files
# output - dictionary of 3D arrays

# for this to work, all the bands will need to be clipped to the same AOI
# and the bands will need to have the same metadata

import rasterio as rio
import numpy as np
import glob
import os


def sortBands(tiff_path):

    imgs = glob.glob(os.path.join(tiff_path, "*0m_clip.tif"))

    # set up dictionary of empty arrays (alternate idea - list of arrays)
    # key = band name, value = empty array to append to
    bands = {
        "B01": np.empty(0),
        "B02": np.empty(0),
        "B03": np.empty(0),
        "B04": np.empty(0),
        "B05": np.empty(0),
        "B08": np.empty(0),
        "B11": np.empty(0),
        "B12": np.empty(0),
    }

    # bands = {
    #     "B01": [],
    #     "B02": [],
    #     "B03": [],
    #     "B04": [],
    #     "B05": [],
    #     "B08": [],
    #     "B11": [],
    #     "B12": [],
    # }

    # iterate through list of TIFFs
    for img in imgs:

        # for the 10 m resolution raster
        if img.endswith("_10m_clip.tif"):

            print(img)

            # open raster
            with rio.open(img) as src:

                # select band of interest
                B02 = src.read(2)
                B03 = src.read(3)
                B04 = src.read(4)
                B08 = src.read(5)

                # append band of interest to bands dict array
                np.append(bands["B03"], B02, axis=0)
                np.append(bands["B03"], B03, axis=0)
                np.append(bands["B04"], B04, axis=0)
                np.append(bands["B08"], B08, axis=0)

                # bands["B02"].append(B02)
                # bands["B03"].append(B03)
                # bands["B04"].append(B04)
                # bands["B08"].append(B08)

        # for the 20 m resolution raster
        elif img.endswith("_20m_clip.tif"):

            # open raster
            with rio.open(img) as src:

                # select band of interest
                B01 = src.read(2)
                B05 = src.read(6)
                B11 = src.read(10)
                B12 = src.read(11)

                # append band of interest to bands dict array
                np.append(bands["B01"], B01, axis=0)
                np.append(bands["B05"], B05, axis=0)
                np.append(bands["B11"], B11, axis=0)
                np.append(bands["B12"], B12, axis=0)

                # bands["B01"].append(B01)
                # bands["B05"].append(B05)
                # bands["B11"].append(B11)
                # bands["B12"].append(B12)

    return bands


# TODO:
# test
# figure out how to deal with raster metadata - will need 10 m and 20 m metadata
# needs all bands to be clipped to the same dimensions to work
