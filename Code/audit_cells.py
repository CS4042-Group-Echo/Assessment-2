import pandas as pd
import os
import numpy as np

def normalize_val(val):
    """
    Standardizes values for fair comparison.
    - Handles '..' vs 0
    - Handles 100 vs 100.0
    - Handles NaNs vs Empty Strings
    """
    if pd.isna(val) or str(val).strip() == "":
        return None
    
    s_val = str(val).strip()
    
    # Treat '..' as 0
    if s_val == '..': return 0
    
    # Try to convert to float/int
    try:
        f = float(s_val.replace(',', '').replace('$', ''))
        if f.is_integer():
            return int(f)
        return f
    except:
        return s_val

def compare_files(path_actual, path_expected):
    filename = os.path.basename(path_actual)
    print(f"Checking: {filename}...")

    try:
        df_act = pd.read_csv(path_actual)
        df_exp = pd.read_csv(path_expected)
    except Exception as e:
        print(f"  [ERROR] Could not read files: {e}")
        return

    # 1. ALIGNMENT
    # We try to align by 'Sex' and 'Category' if they exist
    if 'Sex' in df_act.columns and 'Category' in df_act.columns:
        if 'Sex' in df_exp.columns and 'Category' in df_exp.columns:
            df_act = df_act.set_index(['Sex', 'Category'])
            df_exp = df_exp.set_index(['Sex', 'Category'])
    
    # 2. FIND COMMON STRUCTURE
    # We only compare columns/rows that exist in BOTH files
    common_cols = list(set(df_act.columns).intersection(df_exp.columns))
    common_rows = list(set(df_act.index).intersection(df_exp.index))
    
    if not common_cols:
        print("  [SKIP] No common columns found.")
        return

    # 3. COMPARE VALUES
    diffs = 0
    
    # Sort for deterministic output
    common_rows.sort()
    common_cols.sort()
    
    for idx in common_rows:
        for col in common_cols:
            val_act = normalize_val(df_act.at[idx, col])
            val_exp = normalize_val(df_exp.at[idx, col])
            
            # Check for inequality
            # (We handle None==None explicitly)
            is_diff = False
            if val_act is None and val_exp is not None: is_diff = True
            elif val_act is not None and val_exp is None: is_diff = True
            elif val_act != val_exp:
                # Float tolerance check
                if isinstance(val_act, float) and isinstance(val_exp, float):
                    if abs(val_act - val_exp) > 0.01:
                        is_diff = True
                else:
                    is_diff = True
            
            if is_diff:
                diffs += 1
                if diffs <= 5: # Only print first 5 errors per file
                    print(f"  [MISMATCH] Row: {idx} | Col: {col}")
                    print(f"     My Output: {val_act}")
                    print(f"     Expected:  {val_exp}")

    if diffs == 0:
        print("  [PASS] Matches perfectly.")
    else:
        print(f"  [FAIL] Found {diffs} differences.")
    print("-" * 50)

def main(dir_actual, dir_expected):
    print("--- GROUND TRUTH COMPARISON ---")
    print(f"My Output: {dir_actual}")
    print(f"Ground Truth: {dir_expected}\n")

    if not os.path.exists(dir_expected):
        print(f"Error: Ground Truth folder not found at {dir_expected}")
        return

    files_act = set(f for f in os.listdir(dir_actual) if f.endswith('.csv'))
    files_exp = set(f for f in os.listdir(dir_expected) if f.endswith('.csv'))
    
    common = sorted(list(files_act.intersection(files_exp)))
    missing = sorted(list(files_exp - files_act))

    if missing:
        print(f"[WARNING] Missing files in output: {missing}\n")

    for f in common:
        p_act = os.path.join(dir_actual, f)
        p_exp = os.path.join(dir_expected, f)
        compare_files(p_act, p_exp)

if __name__ == "__main__":
    # UPDATE THESE PATHS
    MY_OUTPUT_DIR = "FilePipeline/C_CleanData"
    GROUND_TRUTH_DIR = "FilePipeline/StandardisedCleanData" # Put your known good files here
    
    main(MY_OUTPUT_DIR, GROUND_TRUTH_DIR)