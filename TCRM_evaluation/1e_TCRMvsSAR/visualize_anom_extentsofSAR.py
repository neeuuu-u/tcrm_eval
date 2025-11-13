# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 16:50:04 2025
Custom dummy colorbar (discrete boxes) — no buffer version, prints map extent
@author: guilesaligo
"""

import rasterio
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import geopandas as gpd
from rasterio.plot import plotting_extent
from rasterio.warp import transform_bounds
from matplotlib.patches import Rectangle
import numpy as np

# === File paths ===
tif_file = r"C:\Users\jo_ht\Downloads\UWAN_sar\tif\anom\anom_11071200_11082132.tif"
obs_file = r"C:\Users\jo_ht\Downloads\UWAN_sar\tif\SAR\STAR_SAR_20251108213231_WP322025_32W_MERGED_FIX_3km.tif"
shp_path = r"D:\neu\CIM oct28\shp\ph_admin_mun_boundaries\PHL_adm4_PSA_pn_2016Junprj_mun.shp"

# === Color scheme ===
colors = [
    "#0D3A7A",  # Extended below -50 (added color)
    "#1B4EAB",  # -50.0 to -44.44
    "#2D72FF",  # -44.44 to -38.89
    "#4D8AFF",  # -38.89 to -33.33
    "#7DB3FF",  # -33.33 to -27.78
    "#9FC3FF",  # -27.78 to -22.22
    "#C1D2FF",  # -22.22 to -16.67
    "#D5E0FF",  # -16.67 to -11.11
    "#E9EEFF",  # -11.11 to -5.56
    "#F7F7FF",  # -5.56 to 0.0
    "#FFFFFF",  # 0.0 (center - white)
    "#FFF7F7",  # 0.0 to 5.56
    "#FFEEEE",  # 5.56 to 11.11
    "#FFD5D5",  # 11.11 to 16.67
    "#FABEBD",  # 16.67 to 22.22
    "#F89E9D",  # 22.22 to 27.78
    "#F67E7D",  # 27.78 to 33.33
    "#F53F3E",  # 33.33 to 38.89
    "#F40000",  # 38.89 to 44.44
    "#A10000",  # 44.44 to 50.0
    "#780000"   # Extended above 50 (added color)
]

# === Boundaries ===
bounds = [
    -50.0, -44.44, -38.89, -33.33, -27.78, -22.22, -16.67, -11.11, -5.56,
    0.0, 5.56, 11.11, 16.67, 22.22, 27.78, 33.33, 38.89, 44.44, 50.0
]

# === Create colormap and normalization ===
cmap = mcolors.ListedColormap(colors)
norm = mcolors.BoundaryNorm(bounds, cmap.N, extend='both')

# Set the color for masked/NaN values to black
cmap.set_bad(color='black')

# === Load model raster ===
with rasterio.open(tif_file) as src:
    data = src.read(1, masked=True)  # Read as masked array to handle NoData
    extent = plotting_extent(src)
    raster_crs = src.crs

# === Load observed raster (for map extent) ===
with rasterio.open(obs_file) as src_obs:
    obs_bounds = src_obs.bounds
    obs_crs = src_obs.crs

# Reproject observed extent if needed
if obs_crs != raster_crs:
    obs_bounds = transform_bounds(obs_crs, raster_crs,
                                  obs_bounds.left, obs_bounds.bottom,
                                  obs_bounds.right, obs_bounds.top)

# === Print map extent ===
print("\n=== Map Extent (using observed raster bounds) ===")
print(f"Left   : {obs_bounds.left}")
print(f"Right  : {obs_bounds.right}")
print(f"Bottom : {obs_bounds.bottom}")
print(f"Top    : {obs_bounds.top}")
print(f"CRS    : {raster_crs}\n")

# === Load shapefile and reproject ===
gdf = gpd.read_file(shp_path)
if gdf.crs != raster_crs:
    gdf = gdf.to_crs(raster_crs)

# === Create figure ===
fig, ax = plt.subplots(figsize=(10, 8))

# === Show raster ===
im = ax.imshow(data, cmap=cmap, norm=norm, extent=extent, origin='upper')

# === Plot landmass and boundaries ===
gdf.plot(ax=ax, facecolor="#9C9C9C", edgecolor="#878787", linewidth=0.5)

# === Use observed extent only (no buffer) ===
ax.set_xlim(obs_bounds.left, obs_bounds.right)
ax.set_ylim(obs_bounds.bottom, obs_bounds.top)

# === Print actual axis extent (final map view) ===
xlim = ax.get_xlim()
ylim = ax.get_ylim()
print("\n=== Actual Axis Extent (final map view) ===")
print(f"X limits (Lon/Easting): {xlim[0]:.4f} to {xlim[1]:.4f}")
print(f"Y limits (Lat/Northing): {ylim[0]:.4f} to {ylim[1]:.4f}")
print(f"Width: {xlim[1] - xlim[0]:.4f}")
print(f"Height: {ylim[1] - ylim[0]:.4f}")
print(f"CRS: {raster_crs}\n")

# === Gridlines ===
ax.grid(True, color='lightgray', linestyle='--', linewidth=0.6)
ax.set_axisbelow(True)

# === Title and labels ===
ax.set_title("Anomaly (MODEL - OBS)", fontsize=14, fontweight='bold')
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

# === Custom dummy color legend ===
labels = [
    "< -50", "-50 to -44", "-44 to -39", "-39 to -33", "-33 to -28",
    "-28 to -22", "-22 to -17", "-17 to -11", "-11 to -6",
    "-6 to 0", "0", "0 to 6", "6 to 11", "11 to 17",
    "17 to 22", "22 to 28", "28 to 33", "33 to 39",
    "39 to 44", "44 to 50", "> 50",
    "No Data"  # Added for NaN/NoData values
]

# Add black color for No Data
legend_colors = colors + ["#000000"]  # Append black for No Data

legend_ax = fig.add_axes([0.88, 0.12, 0.09, 0.76])
legend_ax.axis('off')

# Draw color boxes
for i, label in enumerate(labels):
    color = legend_colors[i]
    y = (len(labels) - 1 - i) / len(labels)  # top to bottom
    rect = Rectangle((0, y),
                     0.5, 1 / len(labels) * 0.8,
                     facecolor=color, edgecolor='black', linewidth=0.5)
    legend_ax.add_patch(rect)
    legend_ax.text(0.6, y + (1 / len(labels) * 0.4),
                   label, va='center', fontsize=7.5)

legend_ax.text(-0.15, 0.5, "Wind Speed Anomaly (m/s)",
               fontsize=11, fontweight='bold',
               rotation=90, va='center', ha='center')

legend_ax.set_xlim(0, 1)
legend_ax.set_ylim(0, 1)

plt.tight_layout(rect=[0, 0, 0.85, 1])
plt.show()