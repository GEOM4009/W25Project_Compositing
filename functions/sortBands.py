#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sort bands.

@author: adrianacaswell
"""

import rasterio as rio
import numpy as np
import glob
import os


def sortBands(img_folder):
    """
    Sort Sentinel-2 images by band for bands of interest.

    Author: Adriana Caswell

    Parameters
    ----------
    img_folder : str
        Path to folder containing Sentinel-2 TIFF files clipped to the same AOI.

    Returns
    -------
    bands : dict
        Dictionary of 3D arrays for each band of interest. Key corrosponds to band of
        interest: B01, B02, B03, B04, B05, B08, B11, B12. Value is the 3D array.
    meta10 : dict
        Metadata for 10 m bands.
    meta20 : dict
        Metadata for 20 m bands.
    meta60 : dict
        Metadata for 60 m bands.

    """
    # find all images in folder
    assert os.path.isdir(img_folder), f"{img_folder} does not exist"
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

    print("Sorting images by band...")

    # iterate through list of TIFFs
    for img in imgs:

        # for the 10 m resolution raster
        if img.endswith("_10m_clip.tif"):

            # open raster
            with rio.open(img) as src:

                # get 10 m metadata
                # check if meta10 exists (from previous 10 m imgs)
                try:
                    meta10

                    # if it does, check if img metadata matches meta10
                    try:
                        assert meta10 == src.meta

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

                    # if img metadata doesn't match, notify user
                    except AssertionError:
                        print(
                            f"{img} metadata is inconsistent with other 10 m images. Unable to sort image bands."
                        )

                # if meta10 doesn't exist, create variable
                except NameError:
                    meta10 = src.meta

        # for the 20 m resolution raster
        elif img.endswith("_20m_clip.tif"):

            # open raster
            with rio.open(img) as src:

                # get 20 m metadata
                # check if meta20 exists (from previous 20 m imgs)
                try:
                    meta20

                    # if it does, check if img metadata matches meta10
                    try:
                        assert meta20 == src.meta

                        # select band of interest
                        B05 = src.read(1)
                        B11 = src.read(5)
                        B12 = src.read(6)

                        # append band of interest to bands dict list
                        bands["B05"].append(B05)
                        bands["B11"].append(B11)
                        bands["B12"].append(B12)

                    # if img metadata doesn't match, notify user
                    except AssertionError:
                        print(
                            f"{img} metadata is inconsistent with other 20 m images. Unable to sort image bands."
                        )

                # if meta20 doesn't exist, create variable
                except NameError:
                    meta20 = src.meta

        # for the 60 m resolution raster
        elif img.endswith("_60m_clip.tif"):

            # open raster
            with rio.open(img) as src:

                # get 60 m metadata
                # check if meta20 exists (from previous 60 m imgs)
                try:
                    meta60

                    # if it does, check if img metadata matches meta10
                    try:
                        assert meta60 == src.meta

                        # select band of interest
                        B01 = src.read(1)

                        # append band of interest to bands dict list
                        bands["B01"].append(B01)

                    # if img metadata doesn't match, notify user
                    except AssertionError:
                        print(
                            f"{img} metadata is inconsistent with other 60 m images. Unable to sort image bands."
                        )

                # if meta60 doesn't exist, create variable
                except NameError:
                    meta60 = src.meta

    print("Sort complete.")

    # convert lists to arrays
    for band_name, band_array in bands.items():
        bands[band_name] = np.array(band_array, dtype=object)

    return bands, meta10, meta20, meta60
