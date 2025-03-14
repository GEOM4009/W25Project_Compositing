#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Open, clip, and convert S2 imagery.

@author: adrianacaswell
"""

import os
import subprocess
import shlex
import glob
import geopandas as gpd


def prepS2(img_folder, shp_path):

    # read in shapefle
    shp_gdf = gpd.read_file(shp_path).geometry
    shp_UTM = shp_gdf.to_crs(32632)

    # should add something to check that it is a polyon
    # create union so there is only one polygon
    if len(shp_UTM) > 1:
        shp_UTM = shp_UTM.union_all()

    # get shapefile extents
    xmin, ymin, xmax, ymax = shp_UTM.bounds

    # locate all S2 SAFE files
    imgs = glob.glob(os.path.join(img_folder, "*.SAFE.zip"))

    # iterate through S2 SAFE files
    for img in imgs:

        # get basename of image for naming output
        basename = os.path.splitext(os.path.splitext(img)[0])[0]

        # set up command to convert image to datasets
        cmd = f"gdal_translate -projwin {xmin} {ymax} {xmax} {ymin} -projwin_srs EPSG:32632 -of GTiff -sds {img} {basename}.tif"
        command = shlex.split(cmd)

        # execute command using subprocess
        subprocess.run(command, capture_output=True, text=True)

        # rename outputs descriptively
        os.rename(f"{basename}_1.tif", f"{basename}_10m_clip.tif")
        os.rename(f"{basename}_2.tif", f"{basename}_20m_clip.tif")
        os.rename(f"{basename}_3.tif", f"{basename}_60m_clip.tif")
        os.rename(f"{basename}_4.tif", f"{basename}_TCI_clip.tif")

    return img_folder


# %% SOURCES
# gdalinfo
# https://gdal.org/en/stable/programs/gdalinfo.html

# gdal_translate
# https://gdal.org/en/stable/programs/gdal_translate.html#gdal-translate
# https://gdal.org/en/stable/programs/gdal_translate.html#cmdoption-gdal_translate-sds
# https://geospatial-linux.readthedocs.io/en/latest/gdal.html
