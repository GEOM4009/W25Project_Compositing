# W25Project_Compositing  
## Compositing tool group project

This tool is designed to process Sentinel-2 imagery, leveraging advanced techniques to create median value composites from multiple satellite images, resample them to a finer 10m resolution, and generate detailed statistical analyses of the data. By clipping the imagery to a specific area of interest (AOI), this tool allows users to focus on relevant regions and ensure that the data used is both accurate and tailored for their needs. Additionally, it resamples the composite bands to a 10m resolution, enhancing spatial resolution for more precise analysis. The tool provides in-depth statistical summaries, such as the mean, variance, and other metrics, helping users better understand the data’s characteristics and variability. Developed by Adriana Caswell, Christian Devey, and Muhammad Ba, this tool is designed for the analysis of Sentinel-2 imagery and for anyone working with satellite data in the field of geospatial analysis.  

---

## Features
- **Preprocessing**: Clips Sentinel-2 bands to your area of interest (AOI) and converts them to TIFF format for further analysis.  
- **Compositing**: Creates median value composites from multiple Sentinel-2 bands, ensuring a robust representation of the observed area over time.  
- **Resampling**: Resamples the composite bands to 10m resolution for higher spatial detail.  
- **Visualization**: Displays composite bands and individual bands for further visual interpretation and analysis.  
- **Statistics**: Provides detailed statistical analysis for each composite band, helping to better understand the underlying data patterns.  

---

## Instructions  

### 1. Download Sentinel-2 Imagery  
Download the Sentinel-2 imagery for your area of interest from the Copernicus Browser (https://dataspace.copernicus.eu/explore-data/data-collections/sentinel-data/sentinel-2).  

### 2. User Input Setup  
In the **User input** section of the script, define the following paths:  
- **inputS2**: Path to the directory containing the zipped Sentinel-2 SAFE files. This is where you’ll store the raw Sentinel-2 images.  
- **clippedS2**: Directory where clipped TIFF files will be saved after preprocessing the raw images.  
- **composites**: Directory where the median composites and resampled composites will be saved. This is where the processed images will be stored.  
- **AIOShp**: Path to the shapefile representing your area of interest (AOI). This will be used to clip the Sentinel-2 bands.  
- **lineSpacing**: Spacing for grid statistics (in meters). This will help in calculating statistics like mean, variance, etc., over a grid defined by this spacing.  

### 3. Running the Code  
Once the setup is complete:  
- The tool will automatically preprocess the Sentinel-2 data, clip it to the AOI, and convert the bands to TIFF format.  
- Afterward, the tool will create median value composites from the clipped bands and resample them to 10m resolution for detailed analysis.  

### 4. Processing Results  
The tool will generate several outputs in the `composites` directory:  
- **Median Composites**: Composite files created for each band based on the median value of the images in the specified period.  
- **Resampled Composites**: The median composites resampled to a 10m resolution for improved spatial analysis.  

### 5. Composite Statistics  

Once the median value composites are created, the tool can provide statistics on the composite bands to help analyze the data further. The statistics are essential for understanding the overall composition of the data and can be used to draw insights for specific applications like vegetation analysis or land use classification.  

#### Available Statistics  
- **Mean**: Average value for each pixel across all the images in the composite.  
- **Standard Deviation**: The measure of variation of pixel values in the composite.  
- **Min and Max**: The range of pixel values across all the bands in the composite.  

### 6. Visualizing the Composites  
The tool can display individual bands or RGB composites for visual inspection:  
- **RGB Composite**: Uses bands B02 (blue), B03 (green), and B04 (red) for generating a true-color composite image.  
- **Individual Bands**: Displays each band separately, such as B01, B02, etc., to allow for detailed analysis of specific wavelengths.  

### 7. Output Locations  
- **Clipped Files**: After preprocessing, the clipped files will be saved in the `clippedS2` directory, ensuring they are ready for compositing.  
- **Composites**: The generated composite images (both median and resampled) will be stored in the `composites` directory. These are the final output files that you will analyze.  

---

## Example Workflow  
1. **Download and organize Sentinel-2 data**.  
2. **Define file paths**: Specify the input, output, and AOI paths in the user input section.  
3. **Run the script**: Preprocess, create composites, and resample.  
4. **Visualize results**: View the composites and individual bands for analysis.  
5. **Analyze the data**: Use the statistics and visual output to gain insights about your area of interest.  

---

## User Support  
If you encounter any issues, refer to the following troubleshooting steps:  
- **Missing Files**: Ensure that all required input files, such as the Sentinel-2 SAFE files and AOI shapefile, are correctly specified in the input section.  
- **Memory Issues**: If the process takes too long or runs out of memory, try processing smaller regions or reduce the number of bands used.  
- **File Paths**: Make sure all paths are correct and accessible. The script may fail if paths are incorrectly specified or if files are missing.  

---

## Credits  
- **Adriana Caswell**, **Christian Devey**, and **Muhammad Ba** for the tool's development.  
- **Copernicus Open Access Hub** for providing Sentinel-2 imagery.  
- Various Python libraries and tools, including `numpy`, and `rasterio` were used in the development of this tool.
- **Dr. Knudby** for initiating the project and providing guidance throughout its development.

---
