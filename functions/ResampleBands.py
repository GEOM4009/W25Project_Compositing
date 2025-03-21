# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 15:41:57 2025

@author: mumub

"""
"""
Resample Sentinel-2 Bands to 10m

# input - folder of clipped Sentinel-2 TIFF files
# output - list of resampled 10m TIFF file paths

# Bands must be clipped to the same AOI and have matching metadata
"""

import glob
import os
import subprocess

def resampleBandsTo10m(img_folder, resampling_method="bilinear", overwrite=True):
    """
    Resample bands to 10m resolution.

    Parameters:
    - img_folder (str): Path to clipped Sentinel-2 images.
    - resampling_method (str): Resampling method (default: 'bilinear').
    - overwrite (bool): If True, overwrite original files; otherwise, create new ones.

    Returns:
    - resampled_files (list): List of resampled file paths.
    """

    # Find all clipped TIFF files in the folder
    imgs = glob.glob(os.path.join(img_folder, "*_clip.tif"))

    resampled_files = []

    # Iterate over each image
    for img in imgs:
        # Set output file path (overwrite or new file)
        output_file = img if overwrite else img.replace(".tif", "_resampled_10m.tif")

        # Build and run gdalwarp command to resample to 10m
        cmd = f"gdalwarp -r {resampling_method} -of GTiff -tr 10 10 {img} {output_file}"
        subprocess.run(cmd.split(), capture_output=True, text=True)

        # Append the resampled file path
        resampled_files.append(output_file)

    return resampled_files


"""
# Customize the following parameters:

img_folder = "path/to/your/folder"  # Path to the folder with clipped TIFF images
resampling_method = "bilinear"  # Resampling method (e.g., 'nearest', 'bilinear', 'cubic')
overwrite = True  # Set True to overwrite original files, False to create new ones

# Call the function
resampled_files = resampleBandsTo10m(img_folder, resampling_method, overwrite)

# Output the list of resampled files
print(f"Resampled files: {resampled_files}")

# input - folder of clipped TIFF files
# output - list of resampled 10m TIFF file paths

# Bands must be clipped to the same AOI and have matching metadata
"""



