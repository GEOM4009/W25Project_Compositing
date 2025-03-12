import os
import zipfile
import rasterio
from rasterio.mask import mask
import geopandas as gpd

def extract_zip(zip_path, extract_to):
    """Extract all files from the ZIP into the extract_to directory."""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def find_shapefile_with_associated_files(folder):
    """Find shapefile and associated .shp, .shx, .prj files in the folder."""
    shapefile = None
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".shp"):
                shapefile = os.path.join(root, file)
                shapefile_prj = shapefile.replace(".shp", ".prj")
                if os.path.exists(shapefile_prj):
                    return shapefile, shapefile_prj
    return None, None

def reproject_shapefile(shapefile, target_crs):
    """Reproject the shapefile to the target CRS (Sentinel-2 CRS: EPSG:32632)."""
    study_area = gpd.read_file(shapefile)
    reprojected_study_area = study_area.to_crs(target_crs)
    return reprojected_study_area

def clip_all_bands(input_folder, output_folder, reprojected_shapefile):
    """Clip all Sentinel-2 bands to the reprojected shapefile and save them."""
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".jp2"):  # Check if the file is a band file
                band_path = os.path.join(root, file)
                print(f"Processing {band_path}")

                destination_path = os.path.join(output_folder, file)

                with rasterio.open(band_path) as src:
                    if reprojected_shapefile.crs != src.crs:
                        print(f"Reprojecting raster from {src.crs} to {reprojected_shapefile.crs}.")
                        # Reproject raster here if necessary

                    try:
                        out_image, out_transform = mask(src, reprojected_shapefile.geometry, crop=True)
                        
                        if out_image is None:
                            print(f"No intersection for {file}. Skipping...")
                            continue

                        with rasterio.open(destination_path, 'w', driver='JP2OpenJPEG',
                                           count=1, dtype=out_image.dtype,
                                           crs=src.crs, transform=out_transform,
                                           width=out_image.shape[2], height=out_image.shape[1]) as dst:
                            dst.write(out_image)

                        print(f"Clipped {file} and saved to {destination_path}")
                    except ValueError as e:
                        print(f"Error processing {file}: {e}")
                        continue

def main():
    zip_folder = "C:\\School\\GIS\\Project\\Sentinal"
    cropped_folder = "C:\\School\\GIS\\Project\\Cropped"
    shapefile_folder = "C:\\School\\GIS\\Project\\Corsica"

    if not os.path.exists(cropped_folder):
        os.makedirs(cropped_folder)

    shapefile, shapefile_prj = find_shapefile_with_associated_files(shapefile_folder)
    if shapefile is None:
        print("Shapefile or associated files not found. Exiting...")
        return

    print(f"Found shapefile: {shapefile} with CRS from {shapefile_prj}")

    # Reproject the shapefile to Sentinel-2 CRS (EPSG:32632)
    reprojected_shapefile = reproject_shapefile(shapefile, 'EPSG:32632')

    # Process each .zip file in the zip_folder
    for zip_file in os.listdir(zip_folder):
        if zip_file.endswith(".zip"):
            zip_path = os.path.join(zip_folder, zip_file)
            extract_to = os.path.join(zip_folder, zip_file[:-4])  # Remove .zip extension

            print(f"Extracting {zip_file}...")
            extract_zip(zip_path, extract_to)

            found_img_data = False
            for root, dirs, files in os.walk(extract_to):
                if 'IMG_DATA' in dirs:
                    img_data_folder = os.path.join(root, 'IMG_DATA')
                    found_img_data = True
                    break

            if found_img_data:
                print(f"Found IMG_DATA folder at: {img_data_folder}")
                print(f"Clipping all bands from {img_data_folder}...")
                clip_all_bands(img_data_folder, cropped_folder, reprojected_shapefile)
            else:
                print(f"IMG_DATA folder not found in {zip_file}. Skipping...")

    print("Clipping complete.")

if __name__ == "__main__":
    main()
