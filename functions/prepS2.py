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


def prepS2(img_folder, shp_path, out_folder):
    """
    Clips Sentinel-2 SAFE zip files to area of interest and outputs TIFF file.

    Author: Adriana Caswell

    Parameters
    ----------
    img_folder : str
        Path to folder containing Sentinel-2 SAFE zip files.
    shp_path : str
        Path to area of interest (polygon) Shapefile.
    out_folder : str
        Path to folder where clipped TIFFs will be output.

    Returns
    -------
    out_folder : str
        Path to folder where clipped TIFFs will be output.

    """
    # check that paths exisit
    assert os.path.isdir(img_folder), f"{img_folder} does not exist"
    assert os.path.isfile(shp_path), f"{shp_path} does not exist"
    assert os.path.isdir(out_folder), f"{out_folder} does not exist"

    # read in shapefle
    try:
        shp_gdf = gpd.read_file(shp_path).geometry

    except:
        raise Exception(f"{shp_path} is not a shapefile")

    # convert CRS to match S2
    shp_UTM = shp_gdf.to_crs(32632)

    # create union so there is only one polygon
    if len(shp_UTM) > 1:
        shp_UTM = shp_UTM.union_all()

    # check if geometry is Polygon
    if not shp_UTM.geom_type == "Polygon":
        raise Exception(f"{shp_path} is not a polygon")

    # get shapefile extents
    xmin, ymin, xmax, ymax = shp_UTM.bounds

    # locate all S2 SAFE files
    imgs = glob.glob(os.path.join(img_folder, "*.SAFE.zip"))

    # communicate with user
    try:
        assert len(imgs) > 0
        print(f"Clipping and converting {len(imgs)} Sentinel-2 images...")

    except AssertionError:
        print(f"{img_folder} does not contain any Sentinel-2 SAFE files")

    # iterate through S2 SAFE files
    for img in imgs:

        # get basename of image for naming output
        basename = os.path.splitext(os.path.splitext(os.path.split(img)[1])[0])[0]
        out_file = os.path.join(out_folder, basename)

        # set up command to convert image to datasets
        cmd = f"gdal_translate -projwin {xmin} {ymax} {xmax} {ymin} -projwin_srs EPSG:32632 -a_nodata 32000 -of GTiff -sds {img} {out_file}.tif"
        command = shlex.split(cmd)

        # execute command using subprocess
        result = subprocess.run(command, capture_output=True, text=True)
        print(result)

        # rename 10 m, 20 m + 60 m outputs descriptively, remove TCI
        os.rename(f"{out_file}_1.tif", f"{out_file}_10m_clip.tif")
        os.rename(f"{out_file}_2.tif", f"{out_file}_20m_clip.tif")
        os.rename(f"{out_file}_3.tif", f"{out_file}_60m_clip.tif")
        os.remove(f"{out_file}_4.tif")

    print("Clipping and conversion complete.")

    return out_folder


# %% SOURCES
# gdalinfo
# https://gdal.org/en/stable/programs/gdalinfo.html

# gdal_translate
# https://gdal.org/en/stable/programs/gdal_translate.html#gdal-translate
# https://gdal.org/en/stable/programs/gdal_translate.html#cmdoption-gdal_translate-sds
# https://geospatial-linux.readthedocs.io/en/latest/gdal.html
