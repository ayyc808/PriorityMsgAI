"""
Combines all 26 CrisisLexT26 labeled CSV files into one file
"""

import pandas as pd
import os
import glob
import sys

# Added dataset path from command line args so each teammate can pass their own local path when running script
# Path to the CrisisLexT26 folder
if len(sys.argv) < 2:
    print("Usage: python3 data/combine_crisislex.py /path/to/CrisisLexT26")
    print("Example: python3 data/combine_crisislex.py ~/Downloads/CrisisLexT26")
    sys.exit(1)

CRISISLEX_PATH = os.path.expanduser(sys.argv[1])

if not os.path.exists(CRISISLEX_PATH):
    print(f"Error: Path not found: {CRISISLEX_PATH}")
    sys.exit(1)

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