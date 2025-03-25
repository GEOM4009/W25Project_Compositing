"""Functions for creating Sentinel-2 composites using S2CompoTool."""

import os
import subprocess
import shlex
import glob
import geopandas as gpd
import rasterio as rio
import numpy as np


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
        subprocess.run(command, capture_output=True, text=True)

        # rename 10 m, 20 m + 60 m outputs descriptively, remove TCI
        os.rename(f"{out_file}_1.tif", f"{out_file}_10m_clip.tif")
        os.rename(f"{out_file}_2.tif", f"{out_file}_20m_clip.tif")
        os.rename(f"{out_file}_3.tif", f"{out_file}_60m_clip.tif")
        os.remove(f"{out_file}_4.tif")

    print("Clipping and conversion complete.")


def sortBands(img_folder):
    """
    Sort Sentinel-2 images by band for bands of interest.

    Author: Adriana Caswell

    Parameters
    ----------
    img_folder : str
        Path to folder containing Sentinel-2 TIFF files clipped using prepS2().

    Returns
    -------
    band_dict : dict
        Dictionary of 3D arrays for each band of interest. Key corrosponds to band of
        interest: B01, B02, B03, B04, B05, B08, B11, B12. Value is the 3D array containing
        masked arrays.
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
    band_dict = {
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

                        # convert to masked array
                        B02_ma = np.ma.masked_equal(B02, 32000)
                        B03_ma = np.ma.masked_equal(B03, 32000)
                        B04_ma = np.ma.masked_equal(B04, 32000)
                        B08_ma = np.ma.masked_equal(B08, 32000)

                        # append band of interest to band_dict list
                        band_dict["B02"].append(B02_ma)
                        band_dict["B03"].append(B03_ma)
                        band_dict["B04"].append(B04_ma)
                        band_dict["B08"].append(B08_ma)

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

                        # convert to masked array
                        B05_ma = np.ma.masked_equal(B05, 32000)
                        B11_ma = np.ma.masked_equal(B11, 32000)
                        B12_ma = np.ma.masked_equal(B12, 32000)

                        # append band of interest to band_dict list
                        band_dict["B05"].append(B05_ma)
                        band_dict["B11"].append(B11_ma)
                        band_dict["B12"].append(B12_ma)

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

                        # convert to masked array
                        B01_ma = np.ma.masked_equal(B01, 32000)

                        # append band of interest to band_dict list
                        band_dict["B01"].append(B01_ma)

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
    for band_name, band_array in band_dict.items():
        band_dict[band_name] = np.ma.stack(band_array)

    # update metadata so that it can be used for one band
    meta10.update({"count": 1})
    meta20.update({"count": 1})
    meta60.update({"count": 1})

    return band_dict, meta10, meta20, meta60


def compositeBands(band_dict, meta10, meta20, meta60, out_folder):
    """
    Create a median value composite from band dictionary created using sortBands().

    Author: Adriana Caswell

    Parameters
    ----------
    band_dict : dict
        Dictionary of 3D arrays for each band of interest. Key corrosponds to band of
        interest: B01, B02, B03, B04, B05, B08, B11, B12. Value is the 3D array containing
        masked arrays.
    meta10 : dict
        Metadata for 10 m bands.
    meta20 : dict
        Metadata for 20 m bands.
    meta60 : dict
        Metadata for 30 m bands.
    out_folder : str
        Path to folder where composite TIFFs will be output.

    """
    # lists of bands based on resolution
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
    
def resampleBands(img_folder, resampling_method="bilinear", overwrite=True):
    """
    Resample Sentinel-2 bands to 10m resolution.

    Parameters
    ----------
    img_folder : str
        Path to folder containing clipped Sentinel-2 TIFF files.
    resampling_method : str
        Resampling method ('bilinear', 'nearest', 'cubic'). Default is 'bilinear'.
    overwrite : bool
        If True, overwrite original files. If False, create new resampled files.

    Returns
    -------
    resampled_files : list
        List of file paths for the resampled bands.
    """
    
    # Find all clipped TIFF files
    imgs = glob.glob(os.path.join(img_folder, "*_clip.tif"))

    # Communicate with user
    print(f"Resampling {len(imgs)} bands to 10m resolution...")

    resampled_files = []

    # Iterate over images and resample
    for img in imgs:
        # Set output path (overwrite or create new file)
        if overwrite:
            output_file = img
        else:
            output_file = img.replace(".tif", "_resampled_10m.tif")

        # GDAL command for resampling
        cmd = f"gdalwarp -r {resampling_method} -of GTiff -tr 10 10 {img} {output_file}"

        # Execute command using subprocess
        subprocess.run(shlex.split(cmd), capture_output=True, text=True)

        # Append to list of resampled files
        resampled_files.append(output_file)

    print("Resampling complete.")
    return resampled_files

