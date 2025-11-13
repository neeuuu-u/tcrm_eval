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

# Load NetCDF
filename = 'evolution.001-00001_2025-11-10_101000'
dataDir = r"C:\Users\jo_ht\Downloads\UWAN_sar\TCRM output [snapshot]\init [1108_1800]\1110_1008"
ds = xr.open_dataset(os.path.join(dataDir, f'{filename}.nc'))

var = ds["gust_speed"]
values = var.squeeze().values


# Handle lat/lon shapes
lat = ds["lat"].values
lon = ds["lon"].values

# Create meshgrid if lat/lon are 1D
if lat.ndim == 1 and lon.ndim == 1:
    lon, lat = np.meshgrid(lon, lat)

# Ensure shapes match
if lon.shape != lat.shape or lon.shape != values.shape:
    raise ValueError(f"Shape mismatch: lon={lon.shape}, lat={lat.shape}, values={values.shape}")

# Flatten coordinates and values
points = np.column_stack((lon.ravel(), lat.ravel()))
values = values.ravel()

# Define target grid resolution
n_cols, n_rows = 500, 500
grid_lon, grid_lat = np.meshgrid(
    np.linspace(np.min(lon), np.max(lon), n_cols),
    np.linspace(np.min(lat), np.max(lat), n_rows)
)

# Interpolate to regular grid
grid_data = griddata(points, values, (grid_lon, grid_lat), method='linear')

# Flip vertically if necessary
grid_data = np.flipud(grid_data)

# Grid resolution
xres = (np.max(lon) - np.min(lon)) / (n_cols - 1)
yres = (np.max(lat) - np.min(lat)) / (n_rows - 1)

# Affine transform
transform = from_origin(np.min(lon), np.max(lat), xres, yres)

# Save GeoTIFF
raster_out = os.path.join(dataDir, f"{filename}.tif")
with rasterio.open(
    raster_out,
    "w",
    driver="GTiff",
    height=grid_data.shape[0],
    width=grid_data.shape[1],
    count=1,
    dtype=grid_data.dtype,
    crs="EPSG:4326",
    transform=transform,
) as dst:
    dst.write(grid_data, 1)
