import pandas as pd
import os
import shutil
import re
import numpy as np

# --- HELPERS ---

def clean_numeric_value(val):
    if pd.isna(val) or str(val).strip() == "": return np.nan
    s_val = str(val).strip()
    if s_val == '..': return 0
    cleaned = re.sub(r"[^\d.]", "", s_val)
    try:
        num = float(cleaned)
        if num.is_integer(): return int(num)
        return num
    except: return np.nan

# --- CLEANERS ---

def drop_subtotal_columns(df, filename):
    if len(df.columns) < 2: return df
    grand_total_col = df.columns[-1]
    cols_to_drop = []
    
    for col in df.columns:
        if str(col).strip().startswith("Total"):
            if col == grand_total_col: continue
            cols_to_drop.append(col)
            
    if cols_to_drop:
        df.drop(columns=cols_to_drop, inplace=True)
        # print(f"[{filename}] COLUMNS DROPPED: {cols_to_drop}")
    return df

def drop_subtotal_rows(df, filename):
    rows_to_drop = []
    for sex in ['MALES', 'FEMALES', 'PERSONS']:
        sex_mask = df.iloc[:, 0].str.upper() == sex
        if not sex_mask.any(): continue
        section_indices = df.index[sex_mask].tolist()
        
        total_candidates = []
        for idx in section_indices:
            cat_name = str(df.iloc[idx, 1]).strip()
            if cat_name.startswith("Total"):
                total_candidates.append(idx)
        
        if len(total_candidates) > 1:
            subtotals = total_candidates[:-1] 
            rows_to_drop.extend(subtotals)

    if rows_to_drop:
        df.drop(index=rows_to_drop, inplace=True)
        df.reset_index(drop=True, inplace=True)
    return df

# --- SOLVERS ---

def solve_hierarchy(df, filename):
    """ Strategy 1: Persons = Males + Females """
    changes = 0
    try:
        map_m = {str(df.at[r, 'Category']).strip(): r for r in df.index[df['Sex'].str.upper() == 'MALES']}
        map_f = {str(df.at[r, 'Category']).strip(): r for r in df.index[df['Sex'].str.upper() == 'FEMALES']}
        map_p = {str(df.at[r, 'Category']).strip(): r for r in df.index[df['Sex'].str.upper() == 'PERSONS']}
    except KeyError: return 0

    data_cols = [c for c in df.columns if c not in ['Sex', 'Category']]

    for cat, m_idx in map_m.items():
        if cat not in map_f or cat not in map_p: continue
        f_idx, p_idx = map_f[cat], map_p[cat]
        
        for col in data_cols:
            if col not in df.columns: continue
            vm, vf, vp = df.at[m_idx, col], df.at[f_idx, col], df.at[p_idx, col]
            
            # Fill missing MALE
            if pd.isna(vm) and pd.notna(vf) and pd.notna(vp):
                res = vp - vf
                if res >= 0: 
                    df.at[m_idx, col] = res
                    changes += 1
                    print(f"[{filename}] HIERARCHY FIX: Row '{cat}' (Male) | Col '{col}' -> {res:.0f}")
            
            # Fill missing FEMALE
            elif pd.isna(vf) and pd.notna(vm) and pd.notna(vp):
                res = vp - vm
                if res >= 0: 
                    df.at[f_idx, col] = res
                    changes += 1
                    print(f"[{filename}] HIERARCHY FIX: Row '{cat}' (Female) | Col '{col}' -> {res:.0f}")
            
            # Fill missing PERSONS
            elif pd.isna(vp) and pd.notna(vm) and pd.notna(vf):
                res = vm + vf
                if res >= 0: 
                    df.at[p_idx, col] = res
                    changes += 1
                    print(f"[{filename}] HIERARCHY FIX: Row '{cat}' (Persons) | Col '{col}' -> {res:.0f}")
    return changes

def solve_sums(df, filename):
    """ Strategy 2 & 3: Vertical and Horizontal Sums """
    changes = 0
    data_cols = [c for c in df.columns if c not in ['Sex', 'Category']]
    
    # VERTICAL: Section Total = Sum(Rows)
    for sex in ['MALES', 'FEMALES', 'PERSONS']:
        sex_mask = df.iloc[:, 0].str.upper() == sex
        if not sex_mask.any(): continue
        indices = df.index[sex_mask].tolist()
        
        total_rows = [i for i in indices if str(df.iloc[i, 1]).strip().startswith('Total')]
        if not total_rows: continue
        t_idx = total_rows[0]
        comp_indices = [i for i in indices if i != t_idx]
        
        for col in data_cols:
            total_val = df.at[t_idx, col]
            comps = df.loc[comp_indices, col]
            
            nans = comps.isna().sum()
            known = comps.sum(skipna=True)
            
            if pd.notna(total_val) and nans == 1:
                missing_idx = comps[comps.isna()].index[0]
                res = total_val - known
                if res >= 0: 
                    df.at[missing_idx, col] = res
                    changes += 1
                    cat = df.at[missing_idx, 'Category']
                    print(f"[{filename}] VERTICAL FIX:  Row '{cat}' | Col '{col}' -> {res:.0f}")

            elif pd.isna(total_val) and nans == 0:
                df.at[t_idx, col] = known
                changes += 1
                cat = df.at[t_idx, 'Category']
                print(f"[{filename}] VERTICAL FIX:  Restored Total '{cat}' | Col '{col}' -> {known:.0f}")

    # HORIZONTAL: Grand Total = Sum(Cols)
    if len(df.columns) > 3:
        comp_cols = df.columns[2:-1]
        total_col = df.columns[-1]
        
        for idx in df.index:
            total_val = df.at[idx, total_col]
            comps = df.loc[idx, comp_cols]
            
            nans = comps.isna().sum()
            known = comps.sum(skipna=True)
            
            if pd.notna(total_val) and nans == 1:
                missing_col = comps[comps.isna()].index[0]
                res = total_val - known
                if res >= 0: 
                    df.at[idx, missing_col] = res
                    changes += 1
                    cat = df.at[idx, 'Category']
                    print(f"[{filename}] HORIZONTAL FIX: Row '{cat}' | Col '{missing_col}' -> {res:.0f}")

            elif pd.isna(total_val) and nans == 0:
                df.at[idx, total_col] = known
                changes += 1
                cat = df.at[idx, 'Category']
                print(f"[{filename}] HORIZONTAL FIX: Restored Row Total '{cat}' -> {known:.0f}")

    return changes

def fix_wrong_totals(df, filename):
    """ Final Pass: Overwrite Totals """
    changes = 0
    comp_cols = df.columns[2:-1]
    total_col = df.columns[-1]
    
    for idx in df.index:
        comps = df.loc[idx, comp_cols]
        total_val = df.at[idx, total_col]
        
        if comps.isna().sum() == 0:
            calc_sum = comps.sum()
            # Tolerance check (0.1) for float precision
            if pd.isna(total_val) or abs(total_val - calc_sum) > 0.1:
                df.at[idx, total_col] = calc_sum
                changes += 1
                cat = df.at[idx, 'Category']
                old = f"{total_val:.0f}" if pd.notna(total_val) else "NaN"
                print(f"[{filename}] WRONG TOTAL:    Row '{cat}' | Col '{total_col}' -> {calc_sum:.0f} (Was {old})")
    return changes

# --- EXECUTION ---

def CleanFile(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    print("--- Starting Repair Pipeline ---\n")
    
    for root, _, files in os.walk(input_dir):
        for file in files:
            if not file.endswith(".csv"): continue
            
            in_path = os.path.join(root, file)
            out_path = os.path.join(output_dir, file)
            
            try:
                df = pd.read_csv(in_path)
                if 'Sex' not in df.columns: continue

                # 1. DELETE BAD DATA
                df = drop_subtotal_columns(df, file)
                df = drop_subtotal_rows(df, file) 

                # 2. STANDARDIZE NUMBERS
                for col in df.columns[2:]:
                    df[col] = df[col].apply(clean_numeric_value)

                # 3. FILL MISSING DATA
                for i in range(10): 
                    c1 = solve_hierarchy(df, file)
                    c2 = solve_sums(df, file)
                    if c1 + c2 == 0: break
                
                # 4. FIX WRONG TOTALS
                fix_wrong_totals(df, file)
                
                # 5. SAVE
                df.to_csv(out_path, index=False, float_format='%.0f')
                
            except Exception as e:
                print(f"[Error] {file}: {e}")
                
    print("\n--- Complete ---")

