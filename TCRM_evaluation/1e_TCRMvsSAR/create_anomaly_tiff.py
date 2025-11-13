# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 16:39:31 2025

@author: guilesaligo
"""

import rasterio
from rasterio.warp import reproject, Resampling
import numpy as np
import os

# === File paths ===
obsWinds = r"C:\Users\jo_ht\Downloads\UWAN_sar\tif\SAR\STAR_SAR_20251110100804_WP322025_32W_MERGED_FIX_3km.tif"
modelWinds = r"C:\Users\jo_ht\Downloads\UWAN_sar\tif\TCRM\init [1108_0600]\1110_1008\evolution.001-00001_2025-11-08_101000.tif"

# === Output path ===
output_filename = 'anom_11081800_11101008.tif'
output_path = r"C:\Users\jo_ht\Downloads\UWAN_sar\tif\anom\anom_11081800_11101008.tif"

# === Open raster files ===
with rasterio.open(modelWinds) as src_model, rasterio.open(obsWinds) as src_obs:
    model_data = src_model.read(1)
    
    # Create an empty array with model's shape for reprojected observed data
    obs_resampled = np.empty_like(model_data, dtype='float32')
    
    # Reproject observed raster to model grid
    reproject(
        source=rasterio.band(src_obs, 1),
        destination=obs_resampled,
        src_transform=src_obs.transform,
        src_crs=src_obs.crs,
        dst_transform=src_model.transform,
        dst_crs=src_model.crs,
        resampling=Resampling.bilinear  # smooth interpolation
    )
    
    # Compute anomaly
    anomaly = model_data.astype('float32') - obs_resampled

    # Copy metadata from model raster
    out_meta = src_model.meta.copy()
    out_meta.update({
        "dtype": "float32",
        "count": 1
    })

# === Save anomaly raster ===
with rasterio.open(output_path, 'w', **out_meta) as dest:
    dest.write(anomaly, 1)

print(f"Anomaly raster saved as: {output_path}")
