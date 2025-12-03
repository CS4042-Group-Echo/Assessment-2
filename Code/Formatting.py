import pandas as pd
import os
import re
import numpy as np

class AnalysisReadyStandardizer:
    def __init__(self, input_files):
        self.input_files = input_files

    def find_header_row_index(self, df):
        """Finds the row index containing 'Total' (The bottom of the header block)."""
        print("    [Debug] Scanning for 'Total' row...")
        for i, row in df.iterrows():
            # Convert row to string list for easier searching
            row_str = [str(x).lower().strip() for x in row if pd.notna(x)]
            
            # Check for 'total'
            if any('total' in x for x in row_str) and len(row_str) > 2:
                print(f"    [Debug] Found 'Total' at row index: {i}")
                return i
        
        print("    [Error] 'Total' row NOT found in this sheet.")
        return None

    def collect_header_block(self, df, main_idx):
        header_indices = [main_idx]
        
        for r in range(main_idx - 1, -1, -1):
            row_vals = df.iloc[r].values
            non_empty = [x for x in row_vals if pd.notna(x) and str(x).strip() != '']
            if not non_empty: break 
            if len(non_empty) == 1: break 
            header_indices.insert(0, r) 

        header_block = df.iloc[header_indices].astype(str).values
        
        final_header = []
        num_cols = header_block.shape[1]
        
        for c in range(num_cols):
            col_vals = header_block[:, c]
            clean_parts = []
            for val in col_vals:
                s_val = val.strip()
                if s_val.lower() == 'nan': continue
                if clean_parts and clean_parts[-1].lower() == s_val.lower(): continue
                clean_parts.append(s_val)
            
            merged = " ".join(clean_parts).strip()
            if not merged: merged = f"Unnamed: {c}"
            final_header.append(merged)
            
        return final_header

    def clean_column_names(self, df):
        new_cols = []
        total_cols = len(df.columns)
        
        for i, col in enumerate(df.columns):
            col_str = str(col)
            if i == total_cols - 1:
                new_cols.append("Total")
                continue

            col_clean = re.sub(r'\([a-z]\)', '', col_str)
            col_clean = col_clean.strip()
            new_cols.append(col_clean)
            
        df.columns = new_cols
        return df

    def detect_sex(self, row_vals):
        check_vals = [str(x).upper().strip() for x in row_vals[0:3] if pd.notna(x)]
        if 'MALES' in check_vals: return 'Males'
        if 'FEMALES' in check_vals: return 'Females'
        if 'PERSONS' in check_vals: return 'Persons'
        return None

    def clean_sheet(self, file_path, sheet_name):
        print(f"  Processing Sheet: {sheet_name}")
        try:
            df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        except Exception as e:
            print(f"  [Error Reading] {sheet_name}: {e}")
            return None
        
        main_idx = self.find_header_row_index(df_raw)
        if main_idx is None: 
            print("  [Skip] Could not determine header structure (missing 'Total').")
            return None

        final_header = self.collect_header_block(df_raw, main_idx)
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, skiprows=main_idx + 1)
        
        rows_to_keep = []
        current_sex = "Persons"
        data_arrays = df.values
        
        print(f"    [Debug] Raw data rows to scan: {len(data_arrays)}")

        for row_vals in data_arrays:
            # 1. Detect Sex
            detected = self.detect_sex(row_vals)
            if detected:
                current_sex = detected
                continue 
            
            # 2. Category Label
            cat_val = str(row_vals[0]).strip()
            if cat_val == 'nan' or cat_val == '':
                if len(row_vals) > 1:
                    cat_val = str(row_vals[1]).strip()

            # 3. Garbage Filter
            bad_starts = ('(', '©', 'This table', 'Small random', 'Please note', 'Released at', 'Inquiries')
            if (cat_val.startswith(bad_starts) or cat_val.lower() == 'nan' or cat_val == ''):
                continue
            
            # 4. Data Filter
            row_data_part = row_vals[1:]
            has_data = False
            for v in row_data_part:
                s_val = str(v).strip()
                if s_val and s_val.lower() != 'nan':
                    has_data = True
                    break
            if not has_data: continue 

            # 5. Construct Row
            data_part = list(row_vals[1:])
            target_len = len(final_header) - 1 
            data_part = data_part[:target_len] 

            clean_row = [current_sex, cat_val] + data_part
            rows_to_keep.append(clean_row)

        if not rows_to_keep: 
            print("  [Skip] No valid data rows found after filtering.")
            return None

        print(f"    [Success] Extracted {len(rows_to_keep)} clean rows.")

        final_columns = ['Sex', 'Category'] + final_header[1:]
        max_len = max(len(r) for r in rows_to_keep)
        if len(final_columns) > max_len:
            final_columns = final_columns[:max_len]
        
        clean_df = pd.DataFrame(rows_to_keep, columns=final_columns)

        # 6. Final Polish
        clean_df = clean_df.replace(r'^\s*\.\.\s*$', 0, regex=True)
        clean_df = clean_df.dropna(axis=1, how='all')
        clean_df = self.clean_column_names(clean_df)
        
        return clean_df

    def run(self):
        # Calculate output path relative to the script, just like we did for inputs
        script_pos = os.path.dirname(os.path.abspath(__file__))
        # Go up one level, then into FilePipeline/StandardisedData
        out_dir = os.path.join(os.path.dirname(script_pos), 'FilePipeline', 'StandardisedData')

        if not os.path.exists(out_dir): 
            os.makedirs(out_dir)
            print(f"[Info] Created directory: {out_dir}")

        for file_path in self.input_files:
            if not os.path.exists(file_path): 
                print(f"[Error] File not found: {file_path}")
                continue
            
            print(f"Standardizing {file_path}...")
            xls = pd.ExcelFile(file_path)
            for sheet in xls.sheet_names:
                if 'content' in sheet.lower(): continue
                df = self.clean_sheet(file_path, sheet)
                if df is not None:
                    # Use the safe 'out_dir' variable here
                    base_name = os.path.basename(file_path).replace('.xlsx','')
                    safe_name = f"{base_name}_{sheet.replace(' ','_')}.csv"
                    full_out_path = os.path.join(out_dir, safe_name)
                    
                    df.to_csv(full_out_path, index=False)
                    print(f"  -> Created {full_out_path}")
# --- EXECUTION ---

# 1. Get the folder where THIS script (dataPipeline.py) lives
script_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Go up one level to the project root (The parent of 'code/')
project_root = os.path.dirname(script_dir)

# 3. Construct the absolute paths dynamically
input_dir = os.path.join(project_root, 'FilePipeline', 'A_InputData')
output_dir = os.path.join(project_root, 'FilePipeline', 'StandardisedData')

# Define files using the safe paths
file_1 = os.path.join(input_dir, 'AdfInputData.xlsx')
file_2 = os.path.join(input_dir, 'PopulusInputData.xlsx')

files = [file_1, file_2]

# Update the class to use the safe output directory
# (You need to slightly modify your run method to accept this, or just rely on the inputs)
pipeline = AnalysisReadyStandardizer(files)

# NOTE: You need to update the run() method in your class to use 'output_dir' 
# if you want the output to be safe too. See below for the small class tweak.
pipeline.run()