# -*- coding: utf-8 -*-
"""
Created on Mon Jun  9 04:09:07 2025

@author: guilesaligo
"""

import xarray as xr
import numpy as np
from scipy.interpolate import griddata
import os
from rasterio.transform import from_origin
import rasterio

filename = 'RCM1_SHUB_2025_09_25_09_34_58_0812108098_128.10E_12.15N_HV_C-12_MERGED01_wind_level2'

# Load NetCDF
dataDir = r'C:\Users\kduco\Documents\Severe_Wind\2025\CIM_OCT\SAR\OPONG_0925_09_34_58'
ds = xr.open_dataset(os.path.join(dataDir,f'{filename}.nc'))
var = ds["sar_wind"]
lat = ds["latitude"].values
lon = ds["longitude"].values
values = var.values

# Flatten coordinates and values
points = np.column_stack((lon.ravel(), lat.ravel()))
values = values.ravel()

# Define target grid resolution
n_cols, n_rows = 500, 500  # can be changed based on desired resolution
grid_lon, grid_lat = np.meshgrid(
    np.linspace(np.min(lon), np.max(lon), n_cols),
    np.linspace(np.min(lat), np.max(lat), n_rows)
)

# Interpolate to a regular grid
grid_data = griddata(points, values, (grid_lon, grid_lat), method='linear')

# Flip data vertically if needed (latitude usually decreases from top to bottom)
grid_data = np.flipud(grid_data)

# Calculate grid resolution
xres = (np.max(lon) - np.min(lon)) / (n_cols - 1)
yres = (np.max(lat) - np.min(lat)) / (n_rows - 1)

# Define affine transform
transform = from_origin(np.min(lon), np.max(lat), xres, yres)

# Save as GeoTIFF
raster_out = os.path.join(dataDir,f"{filename}.tif")
with rasterio.open(
    raster_out,
    "w",
    driver="GTiff",
    height=grid_data.shape[0],
    width=grid_data.shape[1],
    count=1,
    dtype=grid_data.dtype,
    crs="EPSG:4326",  # Use EPSG:32651 or other if UTM or different CRS
    transform=transform,
) as dst:
    dst.write(grid_data, 1)

