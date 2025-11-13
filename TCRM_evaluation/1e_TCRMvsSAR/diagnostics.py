# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 2025
Resample one raster to match another raster’s grid and print detailed diagnostics.
@author: guilesaligo
"""

import rasterio
from rasterio.warp import reproject, Resampling
import numpy as np
import os

# === File paths ===
model_tif = r"C:\Users\jo_ht\Downloads\UWAN_sar\tif\TCRM\init [1108_0600]\1110_1008\evolution.001-00001_2025-11-08_101000.tif"
obs_tif = r"C:\Users\jo_ht\Downloads\UWAN_sar\tif\SAR\STAR_SAR_20251110100804_WP322025_32W_MERGED_FIX_3km.tif"

# === Output ===
output_dir = r"C:\Users\jo_ht\Downloads\UWAN_sar\tif\resampled"
os.makedirs(output_dir, exist_ok=True)

# Choose which raster to resample: "model" or "obs"
resample_target = "model"

# === Open both rasters ===
with rasterio.open(model_tif) as src_model, rasterio.open(obs_tif) as src_obs:
    model_data = src_model.read(1)
    obs_data = src_obs.read(1)

    print("\n=== MODEL RASTER INFO ===")
    print(f"File: {os.path.basename(model_tif)}")
    print(f"  CRS:        {src_model.crs}")
    print(f"  Resolution: {src_model.res}")
    print(f"  Shape:      {model_data.shape}")
    print(f"  Bounds:     {src_model.bounds}")
    print(f"  Transform:\n{src_model.transform}\n")

    print("=== OBSERVED RASTER INFO ===")
    print(f"File: {os.path.basename(obs_tif)}")
    print(f"  CRS:        {src_obs.crs}")
    print(f"  Resolution: {src_obs.res}")
    print(f"  Shape:      {obs_data.shape}")
    print(f"  Bounds:     {src_obs.bounds}")
    print(f"  Transform:\n{src_obs.transform}\n")

    # === Determine resampling direction ===
    if resample_target == "model":
        print("Resampling OBSERVED raster to MODEL grid...\n")
        ref = src_model
        src = src_obs
        src_data = obs_data
        output_filename = os.path.join(output_dir, f"obs_resampled_to_model.tif")
    else:
        print("Resampling MODEL raster to OBSERVED grid...\n")
        ref = src_obs
        src = src_model
        src_data = model_data
        output_filename = os.path.join(output_dir, f"model_resampled_to_obs.tif")

    # === Create empty destination array ===
    dst_array = np.empty((ref.height, ref.width), dtype="float32")

    # === Perform reprojection and resampling ===
    reproject(
        source=src_data,
        destination=dst_array,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=ref.transform,
        dst_crs=ref.crs,
        resampling=Resampling.bilinear
    )

    print("✅ Resampling complete.")

    # === Diagnostics after resampling ===
    print("\n=== DIAGNOSTICS AFTER RESAMPLING ===")
    print(f"  New shape:      {dst_array.shape}")
    print(f"  Target CRS:     {ref.crs}")
    print(f"  Target res:     {ref.res}")
    print(f"  Target bounds:  {ref.bounds}\n")

    # === Prepare output metadata ===
    out_meta = ref.meta.copy()
    out_meta.update({
        "dtype": "float32",
        "count": 1
    })

    # === Save resampled raster ===
    with rasterio.open(output_filename, 'w', **out_meta) as dest:
        dest.write(dst_array, 1)

    print(f"✅ Resampled raster saved as:\n{output_filename}")
