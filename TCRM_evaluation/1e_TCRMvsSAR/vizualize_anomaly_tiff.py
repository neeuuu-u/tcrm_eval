# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 16:50:04 2025
Custom dummy colorbar (discrete boxes)
@author: guilesaligo
"""

import rasterio
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import geopandas as gpd
from rasterio.plot import plotting_extent
from matplotlib.patches import Rectangle

# === File paths ===
tif_file = r"C:\Users\jo_ht\Downloads\UWAN_sar\tif\anom\anom_11071200_11080935.tif"
shp_path = r"D:\neu\CIM oct28\shp\ph_admin_mun_boundaries\PHL_adm4_PSA_pn_2016Junprj_mun.shp"

# === Color scheme ===
# colors = [
#     "#1B4EAB",  # -16 and below
#     "#2D72FF",  # -11 to -15
#     "#7DB3FF",  # -6 to -10
#     "#C1D2FF",  # -1 to -5
#     "#FFFFFF",  # 0 (narrow)
#     "#FFFFFF",  # 0 (narrow)
#     "#FABEBD",  # 1 to 5
#     "#F67E7D",  # 6 to 10
#     "#F40000",  # 11 to 15
#     "#A10000"   # 16 and above
# ]

colors = [
    "#A10000",  # 16 and above
    "#F40000",  # 11 to 15
    "#F67E7D",  # 6 to 10
    "#FABEBD",  # 1 to 5
    "#FFFFFF",  # 0 (narrow)
    "#FFFFFF",  # 0 (narrow)
    "#C1D2FF",  # -1 to -5
    "#7DB3FF",  # -6 to -10
    "#2D72FF",  # -11 to -15
    "#1B4EAB"   # -16 and below
]

# === Boundaries (must be len(colors) + 1) ===
bounds = [-16, -11, -6, -1, 0, 1, 6, 11, 16]

# === Create colormap and normalization ===
cmap = mcolors.ListedColormap(colors)
norm = mcolors.BoundaryNorm(bounds, cmap.N, extend='both')

# === Load raster ===
with rasterio.open(tif_file) as src:
    data = src.read(1)
    extent = plotting_extent(src)
    raster_crs = src.crs  # get CRS for reprojection

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

# === Set map boundaries ===
ax.set_xlim(123.5, 129)
ax.set_ylim(12, 18.5)

# === Gridlines ===
ax.grid(True, color='lightgray', linestyle='--', linewidth=0.6)
ax.set_axisbelow(True)

# === Title and labels ===
ax.set_title("Anomaly (MODEL - OBS)", fontsize=14, fontweight='bold')
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

# === Custom dummy color legend ===
labels = [
    "≤ -16", "-11 to -15", "-6 to -10", "-1 to -5",
    "0", "1 to 5", "6 to 10", "11 to 15", "≥ 16"
]

# Legend
legend_ax = fig.add_axes([0.88, 0.25, 0.09, 0.5])
legend_ax.axis('off')

# Draw color boxes
y_positions = list(range(len(labels)))[::-1]  # top to bottom
for i, label in enumerate(labels):
    color = colors[i + (1 if i > 3 else 0)] if i < 4 else colors[i + 1]
    width = 0.5 if color == "#FFFFFF" else 0.5
    y = i / len(labels)
    rect = Rectangle((0, y), width, 1/len(labels)*0.8, facecolor=color,
                     edgecolor='black', linewidth=0.5)
    legend_ax.add_patch(rect)
    legend_ax.text(width + 0.05, y + (1/len(labels)*0.4), label, va='center', fontsize=10)

legend_ax.text(-0.15, 0.5, "Wind Speed Anomaly (m/s)",
               fontsize=11, fontweight='bold',
               rotation=90, va='center', ha='center')

legend_ax.set_xlim(0, 1)
legend_ax.set_ylim(0, 1)

plt.tight_layout(rect=[0, 0, 0.85, 1])
plt.show()
