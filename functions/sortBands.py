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


def sortBands(img_folder):

    # find all images in folder
    imgs = glob.glob(os.path.join(img_folder, "*0m_clip.tif"))

    # set up dictionary of empty list
    # key = band name, value = empty list to append to
    bands = {
        "B01": [],
        "B02": [],
        "B03": [],
        "B04": [],
        "B05": [],
        "B08": [],
        "B11": [],
        "B12": [],
    }

    # iterate through list of TIFFs
    for img in imgs:

        # for the 10 m resolution raster
        if img.endswith("_10m_clip.tif"):

            # open raster
            with rio.open(img) as src:

                # select band of interest
                B02 = src.read(3)
                B03 = src.read(2)
                B04 = src.read(1)
                B08 = src.read(4)

                # append band of interest to bands dict list
                bands["B02"].append(B02)
                bands["B03"].append(B03)
                bands["B04"].append(B04)
                bands["B08"].append(B08)

        # for the 20 m resolution raster
        elif img.endswith("_20m_clip.tif"):

            # open raster
            with rio.open(img) as src:

                # select band of interest
                B01 = src.read(2)
                B05 = src.read(6)
                B11 = src.read(10)
                B12 = src.read(11)

                # append band of interest to bands dict list
                bands["B01"].append(B01)
                bands["B05"].append(B05)
                bands["B11"].append(B11)
                bands["B12"].append(B12)

    # convert lists to arrays
    for band_name, band_array in bands.items():
        bands[band_name] = np.array(band_array, dtype=object)

    return bands


# TODO:
# figure out how to deal with raster metadata - will need 10 m and 20 m metadata
