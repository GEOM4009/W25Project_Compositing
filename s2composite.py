"""Functions for S2CompoTool."""

import os
import subprocess
import shlex
import glob
import geopandas as gpd
import rasterio as rio
from rasterio.plot import show
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
from statistics import stdev


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

        # check if file exists
        assert os.path.isfile(img), f"{img} does not exist"

        # get basename of image for naming output
        basename = os.path.splitext(os.path.splitext(os.path.split(img)[1])[0])[0]
        out_file = os.path.join(out_folder, basename)

        # set up command to convert image to datasets
        cmd = f"gdal_translate -projwin {xmin} {ymax} {xmax} {ymin} -projwin_srs EPSG:32632 -a_nodata 32000 -of GTiff -sds {img} {out_file}.tif"
        command = shlex.split(cmd, posix=False)

        # execute command using subprocess
        subprocess.run(command, capture_output=True, text=True)

        # rename 10 m, 20 m + 60 m outputs descriptively, remove TCI
        try:
            os.rename(f"{out_file}_1.tif", f"{out_file}_10m_clip.tif")
            os.rename(f"{out_file}_2.tif", f"{out_file}_20m_clip.tif")
            os.rename(f"{out_file}_3.tif", f"{out_file}_60m_clip.tif")
            os.remove(f"{out_file}_4.tif")

        # if the file already exists, remove the files
        except FileExistsError:
            print(f"Overwriting {basename}_10m_clip.tif")
            os.remove(f"{out_file}_10m_clip.tif")
            os.rename(f"{out_file}_1.tif", f"{out_file}_10m_clip.tif")

            print(f"Overwriting {basename}_20m_clip.tif")
            os.remove(f"{out_file}_20m_clip.tif")
            os.rename(f"{out_file}_2.tif", f"{out_file}_20m_clip.tif")

            print(f"Overwriting {basename}_60m_clip.tif")
            os.remove(f"{out_file}_60m_clip.tif")
            os.rename(f"{out_file}_3.tif", f"{out_file}_60m_clip.tif")

    print("Clipping and conversion complete.")

    # Sources:
    # https://gdal.org/en/stable/programs/gdal_translate.html#gdal-translate
    # https://gdal.org/en/stable/programs/gdal_translate.html#cmdoption-gdal_translate-sds
    # https://geospatial-linux.readthedocs.io/en/latest/gdal.html


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

    print("Compositing bands...")

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

        print(f"{band_name} median composite created.")

    print("Compositing complete.")


def resampleBandsTo10m(
    img_folder, out_folder=None, resampling_method="bilinear", overwrite=True
):
    """
    Resample specific Sentinel-2 bands to 10m resolution.

    Author: Mumu Ba

    Parameters
    ----------
    img_folder : str
        Path to folder containing clipped Sentinel-2 TIFF files.
    out_folder : str, optional
        Path to folder where resampled TIFFs will be saved.
        If None, resampled files will be saved in `img_folder` (default: None).
    resampling_method : str
        Resampling method (default: 'bilinear').
    overwrite : bool
        If True, overwrite original files; if False, save as new files with "_resampled" suffix.

    Returns
    -------
    resampled_files : list
        List of resampled file paths.
    """
    # Validate input folder
    if not os.path.isdir(img_folder):
        raise FileNotFoundError(f"Input folder {img_folder} does not exist.")

    # Create output folder if specified
    if out_folder:
        os.makedirs(out_folder, exist_ok=True)
    else:
        out_folder = img_folder  # Save in same folder by default

    # List of valid bands to resample
    valid_bands = ["B01", "B02", "B03", "B04", "B05", "B08", "B11", "B12"]

    # Locate all TIFFs
    imgs = glob.glob(os.path.join(img_folder, "*_composite.tif"))

    if not imgs:
        print("No composite TIFFs found. Exiting.")
        return []

    resampled_files = []

    print(
        f"Resampling {len(imgs)} bands to 10m resolution using {resampling_method}..."
    )

    for img in imgs:
        band_name = os.path.basename(img).split("_")[0]

        # Only resample valid bands
        if band_name not in valid_bands:
            print(f"Skipping {img}: Not a valid band.")
            continue

        # Set output file path
        output_file = (
            os.path.join(out_folder, os.path.basename(img))
            if overwrite
            else os.path.join(out_folder, f"{band_name}_resampled_10m.tif")
        )

        # Skip resampling if overwrite is disabled and output already exists
        if not overwrite and os.path.exists(output_file):
            print(f"Skipping {output_file}: Already exists.")
            resampled_files.append(output_file)
            continue

        # GDAL resampling command
        cmd = [
            "gdalwarp",
            "-r",
            resampling_method,
            "-of",
            "GTiff",
            "-tr",
            "10",
            "10",
            img,
            output_file,
        ]

        # Execute resampling
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Handle GDAL errors
        if result.returncode != 0:
            print(f"Error resampling {img}: {result.stderr}")
        else:
            resampled_files.append(output_file)
            print(f"Resampled: {output_file}")

    print("Resampling complete.")

    return resampled_files


def showRGB(red_band, green_band, blue_band):
    """
    Combine red, green, and blue band TIFF files to display RGB composite.

    Author: Adriana Caswell

    Parameters
    ----------
    red_band : str
        Path to TIFF for red band.
    green_band : str
        Path to TIFF for green band.
    blue_band : str
        Path to TIFF for blue band.

    Returns
    -------
    None.

    """
    with rio.open(red_band) as red_src, rio.open(green_band) as green_src, rio.open(
        blue_band
    ) as blue_src:

        red = red_src.read(1).astype(np.float32)
        green = green_src.read(1).astype(np.float32)
        blue = blue_src.read(1).astype(np.float32)

    # Stack bands into a 3D array (H, W, 3)
    rgb = np.stack([red, green, blue], axis=-1)

    # Normalize (if needed, for uint16 or float scaling)
    rgb = rgb / np.percentile(rgb, 99)  # Scale to 0-1 using the 99th percentile
    rgb = np.clip(rgb, 0, 1)  # Ensure values are in the range [0, 1]

    # Plot the RGB image
    plt.figure(figsize=(10, 10))
    plt.imshow(rgb)
    plt.show()

    # Source: ChatGPT


def showBands(imgs):
    """
    Display 8 bands in one figure.

    Author: Adriana Caswell

    Parameters
    ----------
    imgs : list of str
        List of paths to TIFF files.

    Returns
    -------
    None.

    """
    fig, axes = plt.subplots(4, 2, figsize=(21, 21))

    axes = axes.flatten()

    for i, img in enumerate(imgs):

        # can only handle specific number of subplots
        if i > len(axes):
            break

        # if file doesn't exist, skip
        try:
            assert os.path.isfile(img)

        except AssertionError:
            print(f"{img} does not exist")
            break

        # extract band name from file
        band = os.path.splitext(os.path.splitext(os.path.split(img)[1])[0])[0][:3]

        # open TIFF and plots
        with rio.open(img) as src:

            show(src, title=band, ax=axes[i])

    plt.show()

    # Sources:
    # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html
    # https://rasterio.readthedocs.io/en/stable/topics/plotting.html
    # ChatGPT


printStatus = True
# gridSpacing = 5000
# numSamples = 500
REGION_SIZE = 9

cellSizes = {
    "B01": 60,
    "B02": 10,
    "B03": 10,
    "B04": 10,
    "B05": 20,
    "B08": 10,
    "B11": 20,
    "B12": 20,
}


def makeGrid(sampleBand, lineSpace, cellSize):
    """
    Creates a Grid Over the Area of Intrest.  Outputs a Dictionary storing grid information.

    Author: Christian Devey

    Parameters
    ----------
    sampleBand : arr
        3D masked array, i.e. an array of Sentinel Bands
    lineSpace : int
        The desired spacing in meters between grid lines
    cellSize : int
        The resolution of each cell in the sample band in meters


    Returns
    -------
    grid : dict
        Dictionary representing a grid over the area of interest.
        The Keys are
        "lineSpace": The spacing in meters between lines
        "horzLns": An array of the height of each horizontal line of the grid
        "vertLns": An array of the height of each horizontal line of the grid
        "cPoinOffset": The spacing between 

    """
    grid = {}

    # Get spatial data

    aoiHeight = len(sampleBand) * cellSize
    aoiWidth = len(sampleBand[0]) * cellSize

    if printStatus:
        print("aoiHeight ", aoiHeight, ", aoiWidth ", aoiWidth, end=", ")

    grdHorzLns = []
    for lnHeight in range(0, aoiHeight, lineSpace):
        grdHorzLns.append(lnHeight)

    grdVertLns = []
    for lnDist in range(0, aoiWidth, lineSpace):
        grdVertLns.append(lnDist)

    grid["lineSpace"] = lineSpace
    grid["horzLns"] = grdHorzLns
    grid["vertLns"] = grdVertLns
    grid["cPoinOffset"] = lineSpace / 2

    return grid


def grabRegionStats(imageLayer, x, y, rSize):
    """
    Gets Coefficiant of variation of cells surounding the center cell.  
    Outputs a float Coefficiant of variation.
 
    Author: Christian Devey
 
    Parameters
    ----------
    imageLayer : arr
        2D masked array, representing a Sentinel Bands
    x : int
        The X coordinate of the center cell
    y : int
        The Y coordinate of the center cell
    rSize : The width of the region 
 
 
    Returns
    -------
    cv : float
        The coeffician for variation of the cells examined 
 
    """
    
    halfRSize = rSize // 2
    values = []

    for i in range(0 - halfRSize, halfRSize, 1):
        if i + y >= len(imageLayer):
            break
        for j in range(0 - halfRSize, halfRSize, 1):
            if j + x >= len(imageLayer[0]):
                break
            if not imageLayer[i + y][j + x] is ma.masked:
                ma.append(values, imageLayer[i + y][j + x])

    if len(values) < 2:
        return None
    mean = values.mean()
    if mean == 0:
        return None
    stDiv = stdev(values)
    cv = stDiv / mean

    return cv


def getStatsGrid(bandGroup, grid, cellSize):
    """
    Calculates and records stats from grid center points.

    Author: Christian Devey

    Parameters
    ----------
    bandGroup : arr
        3D masked arrays, i.e. an array of Sentinel Bands
    grid : dict
        Dictionart storing grid information
    cellSize : int
        The resolution of each cell in the sample band in meters


    Returns
    -------
    stats : dict
        Dictionary With the collected stats.
        The Keys are
        "Mins": The Minimum values found at each grid center point
        "Maxs": The maximum values found at each grid center point
        "StDivs": The Standard dieveation of the values found at each grid center point
        "CoeffVars": The coefficients of variation of the points around each center point
        "NumValidVals":  number of valid data points at the grid centers

    """
    
    
    stats = {
        "Mins": ma.array([]),
        "Maxs": ma.array([]),
        "StDivs": ma.array([]),
        "Vals": ma.array([]),
        "CoeffVars": ma.array([]),
        "NumValidVals": [],
    }
    maskedDummy = ma.array([0], mask=[1])
    rowIndexG = 0

    # gridToCell = grid["lineSpace"]/cellSize

    while rowIndexG < len(grid["horzLns"]):
        rowIndexR = int(
            (rowIndexG * grid["lineSpace"] + grid["cPoinOffset"]) // cellSize
        )
        if rowIndexR >= len(bandGroup[0]):
            break
        if printStatus:
            print("row ", rowIndexG + 1, sep="", end=", ")
        cvRow = ma.array([])
        rowMins = ma.array([])
        rowMaxs = ma.array([])
        rowVals = ma.array([])
        rowStDivs = ma.array([])
        rNumValid = []
        colIndexG = 0
        while colIndexG < len(grid["vertLns"]):
            colIndexR = int(
                (colIndexG * grid["lineSpace"] + grid["cPoinOffset"]) // cellSize
            )
            if colIndexR >= len(bandGroup[0][0]):
                break

            cvCell = ma.array([])
            cellVals = ma.array([])
            # validCellVals =[]
            cNumValid = 0
            for layer in bandGroup:
                if not layer[rowIndexR][colIndexR] is ma.masked:
                    cellVal = ma.array([layer[rowIndexR][colIndexR]], mask=[0])
                    # validCellVals =validCellVals.append(cellVal[0])
                else:
                    cellVal = ma.array([layer[rowIndexR][colIndexR]], mask=[1])
                cellVals = ma.append(cellVals, cellVal)
                cv = grabRegionStats(layer, colIndexR, rowIndexR, REGION_SIZE)
                if cv == None:
                    cvma = maskedDummy
                else:
                    cvma = ma.array([cv], [0])
                cvCell = ma.append(cvCell, cvma)
                cNumValid += 1

            cvRow = ma.append(cvRow, cvCell)
            rowVals = ma.append(rowVals, cellVals)
            rNumValid.append(cNumValid)
            if cNumValid > 1:
                rowMaxs = ma.append(rowMaxs, max(cellVals))
                rowMins = ma.append(rowMins, min(cellVals))
                if cNumValid > 2:
                    rowStDivs = ma.append(rowStDivs, stdev(cellVals.compressed()))
                else:
                    rowStDivs = ma.append(rowStDivs, maskedDummy)
            else:
                rowMaxs = ma.append(rowMaxs, maskedDummy)
                rowMins = ma.append(rowMins, maskedDummy)
                rowStDivs = ma.append(rowStDivs, maskedDummy)
            colIndexG += 1

        stats["Mins"] = ma.append(stats["Mins"], rowMins)
        stats["Maxs"] = ma.append(stats["Maxs"], rowMaxs)
        stats["StDivs"] = ma.append(stats["StDivs"], rowStDivs)
        stats["Vals"] = ma.append(stats["Vals"], rowVals)
        stats["CoeffVars"] = ma.append(stats["CoeffVars"], cvRow)
        stats["NumValidVals"].append(rNumValid)
        rowIndexG += 1

    return stats


def gridStats(sortedBands, lineSpace):
    """
    Calculates and records stats from grid center points.

    Author: Christian Devey

    Parameters
    ----------
    sortedBands : dict
        Dictionary of 3D masked arrays, i.e. an array of Sentinel Bands
    lineSpace : int
        The desired spacing in meters between grid lines


    Returns
    -------
    bandStats : dict
        Dictionary With the collected stats.
        The Keys are
        "Mins": The Minimum values found at each grid center point
        "Maxs": The maximum values found at each grid center point
        "StDivs": The Standard dieveation of the values found at each grid center point
        "CoeffVars": The coefficients of variation of the points around each center point
        "NumValidVals":  number of valid data points at the grid centers

    """
    
    if printStatus:
        print("making grid")
    grid = makeGrid(sortedBands["B01"][0], lineSpace, cellSizes["B01"])
    bandStats = {}
    for bandKey in sortedBands:
        if printStatus:
            print("\nlooking at ", bandKey)
        bandStats[bandKey] = getStatsGrid(
            sortedBands[bandKey], grid, cellSizes[bandKey]
        )

    return bandStats
