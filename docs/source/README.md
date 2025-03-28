# About W25Project_Compositing  
## Sentinel-2 Compositing Tool

This tool creates median value composites from 
multiple Sentinel-2 images for B01, B02, B03, B05, B08, B11, and B12. It resamples the composites
to a finer 10 m resolution and generates detailed statistical analyses of the data. By clipping 
the imagery to a specific area of interest 
(AOI), this tool allows users to focus on relevant regions and ensure that the data used is 
both accurate and tailored for their needs. Additionally, it resamples the composite bands 
to a 10m resolution, enhancing spatial resolution for more precise analysis. The tool provides 
in-depth statistical summaries, such as the mean, variance, and other metrics, helping users 
better understand the data’s characteristics and variability. Developed by Adriana Caswell, 
Christian Devey, and Muhammad Ba, this tool is designed for people  in the field of geospatial 
analysis looking to create median value composites of Sentinel-2 imagery.

---

## Features
- **Preprocessing**: Clips Sentinel-2 SAFE files to your area of interest (AOI) and converts 
them to TIFF format for further analysis.  
- **Compositing**: Creates median value composites from multiple Sentinel-2 bands, ensuring 
a robust representation of the observed area over time.  
- **Resampling**: Resamples the composite bands to 10m resolution for higher spatial detail.  
- **Statistics**: Provides detailed statistical analysis for each composite band, helping 
to better understand the underlying data patterns.  
- **Visualization**: Displays composite bands and individual bands for further visual interpretation 
and analysis.  

---

## Installation  

1. Clone this repository: [https://github.com/GEOM4009/W25Project_Compositing.git](https://github.com/GEOM4009/W25Project_Compositing.git)

2. Download and install [Anaconda](https://www.anaconda.com/download#Downloads)

3. Create a conda environment by navigate to W25Project_Compositing in the Anaconda Prompt
and running the following command:
```
conda env create -f s2compo_env.yml
```

4. Activate the environment
```
conda activate s2compo
```

5. Open the Sentinel-2 Composting Tool and follow the Instructions below
```
jupyter lab S2CompoTool.ipynb
```

---

## Instructions 

### 1. Download Sentinel-2 Imagery  
Download the Sentinel-2 imagery for your area of interest from the [Copernicus Browser](https://dataspace.copernicus.eu/explore-data/data-collections/sentinel-data/sentinel-2).  


### 2. User Input Setup  
Define **User input** variables in the S2CompoTool Jupyter Notebook.

### 3. Running the Code  
Once the setup is complete, you can *Run All Cells* or go through the workflow cell-by-cell.


#### 3.1 Preprocessing
The tool will automatically preprocess the Sentinel-2 data, clip it to the AOI, and convert 
the bands to TIFF format. The clipped TIFF files will be saved in the user input `clippedS2` 
directory, ensuring they are ready for compositing.  

After this step, users have the option to perform cloud masking 
(cloud masking functionality is not a part of the tool) or remove images with excessive 
cloud cover to improve the compositing results.


#### 3.2 Compositing and Resampling
The tool will create median value composites from the clipped bands and resample them to 
10m resolution for detailed analysis. The generated composites and resampled composites will 
be stored in the `composites` directory:  
- **Median composites**: Median composites for each band. Saved as B**_composite.tif.
- **Resampled composites**: The median composites resampled to a 10m resolution for improved 
spatial analysis. Saved as B**_resampled10m.tif.


#### 3.3 Statistics 
Once the median value composites are created, the tool can provide statistics on the composite 
bands to help analyze the data further. The statistics are essential for understanding the 
overall composition of the data and can be used to draw insights for specific applications 
like vegetation analysis or land use classification. Available Statistics: 
- **Mean**: Average value for each pixel across all the images in the composite.  
- **Standard Deviation**: The measure of variation of pixel values in the composite.  
- **Min and Max**: The range of pixel values across all the bands in the composite.  


#### 3.4 Visualization
The tool can display individual bands or RGB composites for visual inspection:  
- **RGB Composite**: Uses bands B02 (blue), B03 (green), and B04 (red) for generating a 
RGB composite image.  
- **Individual Bands**: Displays each band separately, such as B01, B02, etc., to allow 
for detailed analysis of specific wavelengths.  

---

## Example Workflow  
1. **Download Sentinel-2 data**  
2. **Define user inputs**: In the S2CompoTool, specify the input, output, and AOI paths in the user input section.  
3. **Run S2CompoTool**: Preprocess, create composites, and resample.  
4. **Visualize results**: View the composites and individual bands for analysis.  
5. **Analyze the data**: Use the statistics and visual output to gain insights about your area of interest.  

---

## Troubleshooting 
If you encounter any issues, refer to the following troubleshooting steps:  
- **Missing Files**: Ensure that all required input files, such as the Sentinel-2 SAFE files and AOI shapefile, are correctly specified in the input section.
- **File Paths**: Make sure all paths are correct and accessible. The script may fail if paths are incorrectly specified or if files are missing.    
- **Memory Issues**: If the process takes too long or runs out of memory, try processing smaller regions or reduce the number of bands used.  

---

## Credits  
- **Adriana Caswell**, **Christian Devey**, and **Muhammad Ba** for the tool's development  
- **Dr. Derek Mueller and Dr. Anders Knudby** for initiating the project and providing guidance throughout its development

---
