"""
Combines all 26 CrisisLexT26 labeled CSV files into one file
"""

import pandas as pd
import os
import glob

# Path to the CrisisLexT26 folder
CRISISLEX_PATH = "/Users/spiderman/Desktop/SJSU/CMPE 189-03/datasets/CrisisLexT26"

# Output file
OUTPUT_FILE = "data/crisislex_combined.csv"

# Find all labeled CSV files across all 26 event folders
labeled_files = glob.glob(os.path.join(CRISISLEX_PATH, "**/*labeled*.csv"), recursive=True)

print(f"Found {len(labeled_files)} labeled CSV files")

dfs = []
for f in labeled_files:
    try:
        df = pd.read_csv(f, encoding="utf-8")
        # Keep only Tweet Text and Informativeness columns
        # Strip whitespace from column names first
        df.columns = df.columns.str.strip()
        if "Tweet Text" in df.columns and "Informativeness" in df.columns:
            df = df[["Tweet Text", "Informativeness"]]  
        
            df.columns = ["text", "label"]
            # Keep only labeled rows (filter out "Not labeled")
            df = df[df["label"] != "Not labeled"]
            dfs.append(df)
    except Exception as e:
        print(f"Skipping {f}: {e}")

# Combine all into one dataframe
combined = pd.concat(dfs, ignore_index=True)

print(f"Total labeled tweets: {len(combined)}")
print(f"Label distribution:\n{combined['label'].value_counts()}")

# Save to backend/data/
combined.to_csv(OUTPUT_FILE, index=False)
print(f"\nSaved to {OUTPUT_FILE}")