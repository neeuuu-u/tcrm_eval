# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 09:16:59 2025

@author: jo_ht
"""

#neu's first code [09/08/2025]! yey

# CELL 0: WORKFLOW OVERVIEW
# --------------------------
# This Jupyter Notebook automates preparing of CSV files from TCRM for comparison to ecmwf_env data
# for multiple tropical cyclones (TCs).

# Workflow:
# A. CELL 1 & 2: Cleaning CSVs to remove rows with missing values in specific columns (_filtered CSVs)
# B. CELL 3: Run cleaning across all CSVs and subfolders
#      - input_base  (folder with raw CSVs)
#      - columns_to_check  (columns to filter, can use letters)

# C. CELL 4: List all _filtered CSV files for verification
# 4. CELL 5: Function to reorder CSV rows based on specified columns (creates _reordered CSVs)
# 5. # CELL 6a: IDENTIFY _FILTERED FOLDER
#    - filtered_folder  (optional manual override)

# CELL 6b: CREATE _EDITED FOLDER STRUCTURE
#    - main_output_folder  (folder path/name)

# CELL 6d: REORDER CSVS
#    - reorder_by_letters  (columns to reorder/group by)      


# CELL 1: IMPORT LIBRARIES
# ------------------------
import os
import pandas as pd
import shutil


# CELL 2: CLEANING FUNCTION (Recursive + Only Process MonthDate CSVs)
# -------------------------------------------------------------------
# Purpose:
#   - Recursively scan all subfolders under folder_path
#   - Process only CSV files containing a month+date segment (e.g., "_Jul23_")
#   - Skip any CSVs with "_DayN" in their names
#   - Drop rows with missing values in specified columns
#   - Save filtered files with "_filtered" appended

import os
import pandas as pd
import re

def clean_folder(folder_path, columns_to_check):
    """
    Recursively reads all CSV files under folder_path that:
      ✅ Contain a month+date pattern like '_Jul23_'
      ❌ Do NOT contain '_DayN'
    Removes rows with missing values in columns_to_check
    and saves filtered versions with '_filtered' appended.
    """
    # Pattern: underscores + 3-letter month + 2-digit day + underscore
    month_pattern = re.compile(r"_[A-Za-z]{3}\d{2}_")  # e.g., "_Jul23_"

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if not file.endswith(".csv"):
                continue  # process only CSV

            # ❌ Skip DayN files (e.g., "_Day1", "_Day12")
            if re.search(r"_Day\d+", file):
                print(f"Skipping Day file: {file}")
                continue

            # ✅ Only process files with "_MonDD_" in filename
            if not month_pattern.search(file):
                print(f"Skipping (no valid month+date): {file}")
                continue

            input_file = os.path.join(root, file)
            print(f"\nProcessing: {input_file}")

            try:
                # Read CSV
                df = pd.read_csv(input_file)

                # Drop rows with missing values in specified columns
                df_cleaned = df.dropna(subset=columns_to_check)

                # Save filtered version next to original
                base, ext = os.path.splitext(file)
                output_file = os.path.join(root, f"{base}_filtered{ext}")
                df_cleaned.to_csv(output_file, index=False)

                print(f"  → Filtered file saved as: {output_file}")

            except Exception as e:
                print(f"  ⚠️ Failed to process {file}: {e}")


# CELL 3: RUN CLEANING (Recursive CSV only, skip Day files)
# --------------------------------------------------------
# Purpose: Recursively scan all subfolders under `input_base`,
# filter only valid CSVs (with "_MonDD"), ignore "_DayN",
# drop rows with missing K/L, and save to mirrored "_filtered" tree.

import os
import pandas as pd
import re

# --- USER CONFIG ---
input_base = r"C:\Users\jo_ht\OneDrive\Documents\neu\sept 22 report\tcrm\swiftph output csv"
columns_to_check = ["K", "L"]
designated_dir = r"C:\Users\jo_ht\OneDrive\Documents\neu\sept 22 report\tcrm\tcrm_edit data"

# --- Patterns ---
month_pattern = re.compile(r"_[A-Z][a-z]{2}\d{2}")   # e.g. _Jul23
day_pattern = re.compile(r"_Day\d+", re.IGNORECASE)  # e.g. _Day0

# --- Detect TC name + year from a valid CSV ---
example_file = None
for root, _, files in os.walk(input_base):
    for f in files:
        if f.lower().endswith(".csv") and month_pattern.search(f) and not day_pattern.search(f):
            example_file = f
            break
    if example_file:
        break

if example_file:
    parts = example_file.split("_")
    tc_name = parts[0]
    yy = parts[1][-2:]
    output_folder_name = f"{tc_name}_20{yy}_filtered"
else:
    output_folder_name = "_filtered"

# --- Create output root ---
output_base = os.path.join(designated_dir, output_folder_name)
os.makedirs(output_base, exist_ok=True)
print(f"Filtered CSVs will be saved to: {output_base}")

# --- Recursive processing ---
for root, _, files in os.walk(input_base):
    relative_path = os.path.relpath(root, input_base)
    out_subfolder = os.path.join(output_base, relative_path)
    os.makedirs(out_subfolder, exist_ok=True)

    for file in files:
        # Only CSV files
        if not file.lower().endswith(".csv"):
            continue

        # Skip "_DayN" CSVs
        if day_pattern.search(file):
            print(f"Skipping Day file: {file}")
            continue

        # Process only if filename contains "_MonDD"
        if not month_pattern.search(file):
            print(f"Skipping (no _MonDD): {file}")
            continue

        input_file = os.path.join(root, file)
        print(f"Processing: {input_file}")

        # Load CSV
        try:
            df = pd.read_csv(input_file)
        except Exception as e:
            print(f"Failed to read {input_file}: {e}")
            continue

        # Drop rows with missing K/L
        col_indices = [ord(c.upper()) - ord("A") for c in columns_to_check]
        valid_cols = [df.columns[i] for i in col_indices if i < len(df.columns)]
        df_filtered = df.dropna(subset=valid_cols)

        # Save filtered file
        base, ext = os.path.splitext(file)
        output_file = os.path.join(out_subfolder, f"{base}_filtered{ext}")
        try:
            df_filtered.to_csv(output_file, index=False)
            print(f"Saved: {output_file}")
        except Exception as e:
            print(f"Failed to save {output_file}: {e}")


# CELL 4: LIST FILTERED FILES
# Purpose: Verify all _filtered CSVs are created, especially useful for multiple TCs

for root, dirs, files in os.walk(input_base):
    for file in files:
        if file.endswith("_filtered.csv"):
            print(os.path.join(root, file))


# CELL 5: REORDERING TOOL
# -----------------------
# Purpose: Reorder rows of filtered CSVs based on specified columns (letters)
# Creates _reordered CSVs; empty CSVs are still processed

def reorder_all_csv(input_base, output_base, reorder_by_letters):
    import os
    import pandas as pd
    
    os.makedirs(output_base, exist_ok=True)

    for root, dirs, files in os.walk(input_base):
        csv_files = [f for f in files if f.lower().endswith(".csv")]
        if not csv_files:
            continue

        for file in csv_files:
            input_file = os.path.join(root, file)
            print(f"\nProcessing: {input_file}")

            try:
                df = pd.read_csv(input_file)
            except Exception as e:
                print(f"  ⚠ Failed to read {input_file}: {e}")
                continue

            if not df.empty:
                # Convert letters to column names
                col_indices = [ord(c.upper()) - ord("A") for c in reorder_by_letters]
                cols = [df.columns[i] for i in col_indices if 0 <= i < len(df.columns)]
                if cols:
                    df = df.sort_values(by=cols).reset_index(drop=True)

            base, ext = os.path.splitext(file)
            output_file = os.path.join(output_base, f"{base}_reordered{ext}")
            try:
                df.to_csv(output_file, index=False)
                print(f"  → Reordered file saved as {output_file}")
            except Exception as e:
                print(f"  ⚠ Failed to write {output_file}: {e}")


# CELL 6a: LOCATE _FILTERED FOLDER
import os

# 👇 EDIT if needed
main_folder = r"C:\Users\jo_ht\OneDrive\Documents\neu\sept 22 report\tcrm\tcrm_edit data"  # folder containing raw subfolders

# Automatically detect the _filtered folder
filtered_folder = None
for f in os.listdir(main_folder):
    full_path = os.path.join(main_folder, f)
    if os.path.isdir(full_path) and f.endswith("_filtered"):
        filtered_folder = full_path
        break

if not filtered_folder:
    raise FileNotFoundError("No _filtered folder found in main_folder!")



# CELL 6B: CREATE _REORDERED FOLDER
# 👇 Create _reordered folder using same TC name + year as _filtered
reordered_base = filtered_folder.replace("_filtered", "_reordered")
os.makedirs(reordered_base, exist_ok=True)

print(f"📂 Reordered files will be saved in: {reordered_base}")


# CELL 6c: REORDER CSV FILES (all subfolders, no duplication)
import pandas as pd
import numpy as np

# 👇 EDITABLE: columns to reorder by (letters)
reorder_by_letters = ["C", "E", "G", "K", "L"]

# Traverse all subfolders in _filtered
for root, dirs, files in os.walk(filtered_folder):
    rel_path = os.path.relpath(root, filtered_folder)
    output_subfolder = os.path.join(reordered_base, rel_path)
    os.makedirs(output_subfolder, exist_ok=True)

    for file in files:
        if file.lower().endswith(".csv"):
            input_file = os.path.join(root, file)
            df = pd.read_csv(input_file)

            if df.empty:
                print(f"⚠️ Empty file: {file} → still saved as _reordered")
            else:
                # 🔹 Rename Pro_Name → prov for consistency
                df = df.rename(columns={"Pro_Name": "prov"})

                # Convert letters to column names safely
                col_indices = [ord(c.upper()) - ord("A") for c in reorder_by_letters]
                cols = [df.columns[i] for i in col_indices if 0 <= i < len(df.columns)]

                if cols:
                    sort_orders = []
                    for col in cols:
                        if pd.api.types.is_numeric_dtype(df[col]):
                            sort_orders.append(False)  # descending for numbers
                        else:
                            sort_orders.append(True)   # ascending for text

                    try:
                        df = df.sort_values(by=cols, ascending=sort_orders, na_position="last").reset_index(drop=True)
                    except Exception as e:
                        print(f"⚠️ Could not reorder {file} by {cols}: {e}")

            # Save with "_reordered" suffix instead of "_filtered"
            output_file = os.path.join(
                output_subfolder, file.replace("_filtered", "_reordered")
            )
            df.to_csv(output_file, index=False)

# CELL 7: PROVINCE-LEVEL AGGREGATION (Fixed Output Path)
# ------------------------------------------------------
# Purpose: Aggregate municipality-level mean_ctrl and wtd_mean values
#          into province-level averages.
# Output:  Always saved under the fixed "_aggregated" folder:
#          C:\Users\jo_ht\OneDrive\Documents\neu\sept 22 report\tcrm\tcrm_edit data\_aggregated

import os
import pandas as pd

# Input = reordered folder from Cell 6
input_base = reordered_base  

# ✅ Fixed aggregated output path
aggregated_base = r"C:\Users\jo_ht\OneDrive\Documents\neu\sept 22 report\tcrm\tcrm_edit data\_aggregated"
os.makedirs(aggregated_base, exist_ok=True)

print(f"📂 Aggregated province-level files will be saved in: {aggregated_base}")

required_cols = {"prov", "mean_ctrl", "wtd_mean"}

for root, dirs, files in os.walk(input_base):
    rel_path = os.path.relpath(root, input_base)
    output_subfolder = os.path.join(aggregated_base, rel_path)
    os.makedirs(output_subfolder, exist_ok=True)

    for file in files:
        if not file.lower().endswith(".csv"):
            continue

        input_file = os.path.join(root, file)
        try:
            df = pd.read_csv(input_file)
        except Exception as e:
            print(f"⚠ Failed to read {input_file}: {e}")
            continue

        # Skip empty or incomplete files
        if df.empty or not required_cols.issubset(df.columns):
            continue

        # Province-level aggregation
        province_agg = (
            df.groupby("prov")[["mean_ctrl", "wtd_mean"]]
            .mean()
            .reset_index()
        )

        # Rename headers only in aggregated CSVs
        province_agg = province_agg.rename(
            columns={
                "mean_ctrl": "mean_ctrl (TCRM)",
                "wtd_mean": "wtd_mean (TCRM)"
            }
        )

        # Save to the fixed aggregated folder (preserving relative subfolder structure)
        output_file = os.path.join(output_subfolder, file.replace("_reordered", "_aggregated"))
        try:
            province_agg.to_csv(output_file, index=False)
            print(f"✅ Created aggregated file: {output_file}")
        except Exception as e:
            print(f"⚠ Failed to save {output_file}: {e}")
