import pandas as pd
import os
import re
import numpy as np

def clean_numeric_value(val):
    """
    Mimics the cleaning script's logic to identify what IS missing vs what is just 0.
    """
    if pd.isna(val) or str(val).strip() == "":
        return np.nan
    s_val = str(val).strip()
    if s_val == '..': return 0 # '..' is 0, not missing
    return val

def count_missing(folder_path, convert_numeric=False):
    file_stats = {}
    total_missing = 0
    
    if not os.path.exists(folder_path):
        return None, None

    for root, _, files in os.walk(folder_path):
        for file in files:
            if not file.endswith('.csv'): continue
            
            path = os.path.join(root, file)
            try:
                df = pd.read_csv(path)
                
                # Focus on Data Columns (Skip Sex/Category if they exist)
                if 'Sex' in df.columns and 'Category' in df.columns:
                    data_df = df.iloc[:, 2:].copy()
                else:
                    data_df = df.copy()

                # For the 'Before' folder, we need to be strict:
                # '..' should NOT count as empty. Empty strings SHOULD count.
                if convert_numeric:
                    # Apply basic cleaner to ensure we catch strings that mean "empty"
                    for col in data_df.columns:
                        data_df[col] = data_df[col].apply(clean_numeric_value)
                
                # Count NaNs
                count = data_df.isna().sum().sum()
                
                file_stats[file] = count
                total_missing += count
                
            except Exception as e:
                print(f"Error reading {file}: {e}")
                
    return total_missing, file_stats

def run_audit(dir_before, dir_after):
    print(f"--- AUDITING CLEANING PROCESS ---")
    print(f"Before: {dir_before}")
    print(f"After:  {dir_after}\n")

    # Count Before (applying numeric conversion to catch garbage as NaN)
    tot_before, files_before = count_missing(dir_before, convert_numeric=True)
    
    # Count After (files are already numeric)
    tot_after, files_after = count_missing(dir_after, convert_numeric=False)

    if tot_before is None or tot_after is None:
        print("Error: One of the directories does not exist.")
        return

    # Print Comparison Table
    print(f"{'FILENAME':<60} | {'BEFORE':<10} | {'AFTER':<10} | {'FIXED':<10}")
    print("-" * 100)

    # Get list of all files
    all_files = sorted(list(set(files_before.keys()) | set(files_after.keys())))

    for f in all_files:
        b = files_before.get(f, "N/A")
        a = files_after.get(f, "N/A")
        
        diff = "N/A"
        if isinstance(b, int) and isinstance(a, int):
            diff = b - a
            # If 0 missing before and after, don't clutter output, unless you want to see everything
            if b == 0 and a == 0:
                continue

        print(f"{f:<60} | {str(b):<10} | {str(a):<10} | {str(diff):<10}")

    print("-" * 100)
    print(f"{'TOTAL':<60} | {str(tot_before):<10} | {str(tot_after):<10} | {str(tot_before - tot_after):<10}")

if __name__ == "__main__":
    # Update these to your actual paths
    BEFORE_DIR = "FilePipeline/B_FormattedData"
    AFTER_DIR  = "FilePipeline/C_CleanData"
    
    run_audit(BEFORE_DIR, AFTER_DIR)