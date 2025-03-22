#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 12 15:34:44 2025

@author: adrianacaswell
"""

import numpy as np
import rasterio as rio
import os

# input - dictionary of 3D arrays
# output - dictionary of 2D arrays that are median value composites


def compositeBands(band_dict, meta10, meta20, meta60, out_folder):

    bands10 = ["B02", "B03", "B04", "B08"]
    bands20 = ["B05", "B11", "B12"]
    bands60 = ["B01"]

    for band_name, band_array in band_dict.items():

        # take the median value of the bands (ignoring masked data)
        comp = np.ma.median(band_array, axis=0)
        np.ma.set_fill_value(comp, 32000)  # reset comp value now that it is 2D
        comp = comp.filled()  # convert to np.array (filling no data values)

        # reshape composite to be 3D array
        comp_rs = np.reshape(comp, (1, comp.shape[0], comp.shape[1]))

        # set output file
        out_file = os.path.join(out_folder, band_name + "_composite.tif")

        # write composites
        if band_name in bands10:
            with rio.open(out_file, "w", **meta10) as dest:
                dest.write(comp_rs)

        elif band_name in bands20:
            with rio.open(out_file, "w", **meta20) as dest:
                dest.write(comp_rs)

        elif band_name in bands60:
            with rio.open(out_file, "w", **meta60) as dest:
                dest.write(comp_rs)

        print(f"{band_name} composite created.")
