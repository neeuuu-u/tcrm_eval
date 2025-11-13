# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 16:17:14 2025

@author: guilesaligo
"""
import rasterio
from rasterio.plot import show
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os
import numpy as np

# === File paths ===
tif_file = r"C:\Users\jo_ht\Downloads\UWAN_sar\tif\SAR\STAR_SAR_20251108213231_WP322025_32W_MERGED_FIX_3km.tif"

shapefile = r"D:\neu\CIM oct28\shp\ph_admin_mun_boundaries\PHL_adm4_PSA_pn_2016Junprj_mun.shp"

# === Define color bins and corresponding colors ===
bounds = [
    0.0, 2.78, 5.56, 8.33, 11.11, 13.89, 16.67, 19.44, 22.22,
    25.0, 27.78, 30.56, 33.33, 36.11, 38.89, 41.67, 44.44, 47.22, 50.0
]

colors = [
    "#000000", "#7d7dd6", "#7d7dfc", "#7daeff", "#69d4f4",
    "#7effff", "#8cffcf", "#eaff73", "#fff479", "#ffcf73",
    "#ff8360", "#ff7373", "#ff5c5c", "#a55fa8", "#c78ad8",
    "#e1bce9", "#f3dff5", "#ffffff", "#ffffff"
]


# Create colormap and normalization
cmap = mcolors.ListedColormap(colors)
norm = mcolors.BoundaryNorm(bounds, cmap.N)

# Set the color for masked/null values to black
cmap.set_bad(color='black')

# === Load raster ===
with rasterio.open(tif_file) as src:
    wind_data = src.read(1, masked=True)  # Read as masked array
    extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
    crs = src.crs

# === Load shapefile ===
gdf = gpd.read_file(shapefile)
if gdf.crs != crs:
    gdf = gdf.to_crs(crs)

# === Plot ===
fig, ax = plt.subplots(figsize=(10, 10))

# Plot landmass and boundaries
gdf.plot(ax=ax, facecolor="#9C9C9C", edgecolor="#878787", linewidth=0.5)

# Show raster
im = ax.imshow(wind_data, cmap=cmap, norm=norm, extent=extent, origin='upper')


# === Colorbar ===
# Centered tick positions (middle of color bins)
tick_positions = [(bounds[i] + bounds[i+1]) / 2 for i in range(len(bounds) - 1)]
tick_labels = [
    f"{bounds[i]:.3f}–{bounds[i+1]-1:.3f}" if i < len(bounds) - 2 else f"{bounds[i]:.3f}+"
    for i in range(len(bounds) - 1)
]

cbar = plt.colorbar(im, ax=ax, fraction=0.036, pad=0.04)
cbar.set_ticks(tick_positions)
cbar.set_ticklabels(tick_labels)
cbar.ax.tick_params(size=0, width=0)  # remove tick lines
cbar.set_label('Wind Speed (m/s)', fontsize=11)


# === Visualization boundaries ===
ax.set_xlim(123.7172, 127.6862)
ax.set_ylim(11.9123, 16.6754)

# === Gridlines ===
ax.grid(True, color='lightgray', linestyle='--', linewidth=0.6)
ax.set_axisbelow(True)

# === Title and labels ===
ax.set_title("SAR Winds on 110825 21:32 UTC (m/s)", fontsize=14, fontweight='bold')
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

plt.tight_layout()
plt.show()