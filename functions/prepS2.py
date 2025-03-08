#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Open, convert, and clip S2 imagery.

In-progress - need to figure out how to clip image. This also needs to be made into a function. 
Also, this workflow will only work for S2 images that cover the full AOI. So we may need
to figure something out to include images that only cover part of the AOI.

@author: adrianacaswell
"""

import os
import subprocess
import shlex
import glob
import geopandas as gpd
import rasterio as rio
from rasterio.mask import mask

# function inputs
s2_path = (
    "/Users/adrianacaswell/Documents/Carleton/Coursework/W25/GEOM4009/Project/Data/S2"
)
shp_path = "/Users/adrianacaswell/Documents/Carleton/Coursework/W25/GEOM4009/Project/Data/Corsica/StudyArea.shp"


# %% adriana's clip function from assignment 4
# use this for now but figure out how GDAL warp works
def img_clip(image, bounds, outfile):
    """
    Clip raster image to bounds of interest.

    Parameters
    ----------
    image : rasterio.io.DatasetReader
        Raster image of interest reader.
    bounds : GeoSeries
        Geometry of bounds of interest.
    outfile : str
        Path to output TIFF.

    Returns
    -------
    outfile : str
        Path to output TIFF.

    """
    # create clip
    clip, clip_transform = mask(image, bounds, crop=True)

    # update metadata
    clip_meta = image.meta.copy()
    clip_meta.update(
        {
            "height": clip.shape[1],
            "width": clip.shape[2],
            "transform": clip_transform,
            "nodata": 0,
        }
    )

    # write the clip to a file
    with rio.open(outfile, "w", **clip_meta) as out:
        out.write(clip)

    return outfile


# %% read in shapefle
shp_gdf = gpd.read_file(shp_path).geometry
shp_UTM = shp_gdf.to_crs(32632)

# %%
# navigate to folder containing S2 images
os.chdir(s2_path)

# locate all S2 SAFE files
imgs = glob.glob("*.SAFE.zip")

output = []

# iterate through S2 SAFE files
for img in imgs:

    # get basename of image for naming output
    basename = os.path.splitext(os.path.splitext(img)[0])[0]

    # ideally here we will use gdalwarp instead of gdal_translate to clip the image
    # can use gdalwarp cutline to clip to shapefile but haven't figured this out
    # then gdalwarp will output a clipped TIFF
    # probably also want to set it up to export to a subfolder

    # set up command to convert image to datasets
    cmd = f"gdal_translate -sds {img} {basename}.tif"
    command = shlex.split(cmd)

    # execute command using subprocess
    result = subprocess.run(command, capture_output=True, text=True)

    # clip images
    with rio.open(f"{basename}_1.tif") as src:
        img_clip(src, shp_UTM, f"{basename}_10m_clip.tif")

    with rio.open(f"{basename}_2.tif") as src:
        img_clip(src, shp_UTM, f"{basename}_20m_clip.tif")

    with rio.open(f"{basename}_3.tif") as src:
        img_clip(src, shp_UTM, f"{basename}_60m_clip.tif")

    with rio.open(f"{basename}_4.tif") as src:
        img_clip(src, shp_UTM, f"{basename}_TCI_clip.tif")

    # rename outputs descriptively
    # os.rename(f"{basename}_1.tif", f"{basename}_10m.tif")
    # os.rename(f"{basename}_2.tif", f"{basename}_20m.tif")
    # os.rename(f"{basename}_3.tif", f"{basename}_60m.tif")
    # os.rename(f"{basename}_4.tif", f"{basename}_TCI.tif")

    output.append(
        [
            f"{basename}_10m_clip.tif",
            f"{basename}_20m_clip.tif",
            f"{basename}_60m_clip.tif",
            f"{basename}_TCI_clip.tif",
        ]
    )

# have the function return output (a list of lists containing band names)

# %% SOURCES
# gdalinfo
# https://gdal.org/en/stable/programs/gdalinfo.html

# gdal_translate
# https://gdal.org/en/stable/programs/gdal_translate.html#gdal-translate
# https://gdal.org/en/stable/programs/gdal_translate.html#cmdoption-gdal_translate-sds

# gdalwarp
# https://gdal.org/en/latest/programs/gdalwarp.html#gdalwarp
# https://joeyklee.github.io/broc-cli-geo/guide/XX_raster_cropping_and_clipping.html
