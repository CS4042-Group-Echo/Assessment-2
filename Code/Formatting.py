import pandas as pd
import os
import re
import numpy as np

class AnalysisReadyStandardizer:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir): os.makedirs(self.output_dir)

    def find_header_row_index(self, df):
        """
        Finds the Main Header Row.
        RULE: The row must contain 'Total' in its LAST non-empty column.
        This prevents falsely matching 'Total family household' (which is in the middle).
        """
        print("    [Debug] Scanning for 'Total' row...")
        
        for i, row in df.iterrows():
            # Get list of text values in this row (skipping blanks)
            vals = [str(x).strip() for x in row if pd.notna(x) and str(x).strip() != '']
            
            # A valid header must have at least 3 columns to be safe
            if len(vals) < 3: 
                continue
            
            # CRITICAL CHECK: Is 'Total' in the LAST column?
            # This distinguishes the real header from section titles or intermediate totals.
            last_val = vals[-1].lower()
            if 'total' in last_val:
                print(f"    [Debug] Found Header at Row {i} (Last col: '{vals[-1]}')")
                return i
                
        print("    [Error] Could not find a valid 'Total' header row.")
        return None

    def collect_header_block(self, df, main_idx):
        """
        Collects header rows upwards from the main row.
        - Keeps: Valid multi-line headers (e.g. 'Does not have need for')
        - Skips: Table Titles, and 'Summary Labels' (rows with only 1 value starting with Total)
        """
        header_indices = [main_idx]
        
        for r in range(main_idx - 1, -1, -1):
            row_vals = df.iloc[r].values
            non_empty = [str(x).strip() for x in row_vals if pd.notna(x) and str(x).strip() != '']
            
            # STOP 1: Row is empty
            if not non_empty: break 
            
            first_val = non_empty[0].lower()

            # STOP 2: Row is a Table Title ("Table 6...", "Census...", "Released at...")
            if first_val.startswith("table") or first_val.startswith("census") or first_val.startswith("released"):
                break

            # STOP 3: Row is a Summary Label (Special case for Table 6)
            # If the row has ONLY 1 value, and that value starts with "Total", assume it's a label we don't want.
            # (e.g. "Total personal income (weekly)")
            if len(non_empty) == 1 and first_val.startswith("total"):
                break

            # Otherwise, keep it (e.g. "Age", "Sex", "Does not have need for")
            header_indices.insert(0, r) 

        # Merge the collected rows
        header_block = df.iloc[header_indices].astype(str).values
        final_header = []
        num_cols = header_block.shape[1]
        
        for c in range(num_cols):
            col_vals = header_block[:, c]
            clean_parts = []
            for val in col_vals:
                s_val = val.strip()
                if s_val.lower() == 'nan': continue
                # Deduplicate (avoid "Sex Sex")
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
            # Force last col to be 'Total' (Standardizes Total(c) -> Total)
            if i == total_cols - 1:
                new_cols.append("Total")
                continue
            # Remove (a), (b) footnotes
            col_clean = re.sub(r'\([a-z]\)', '', col_str).strip()
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
        
        # 1. Find Header
        main_idx = self.find_header_row_index(df_raw)
        if main_idx is None: return None

        # 2. Collect Header (With smart stops)
        final_header = self.collect_header_block(df_raw, main_idx)

        # 3. Read Data
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, skiprows=main_idx + 1)
        
        rows_to_keep = []
        current_sex = "Persons"
        data_arrays = df.values
        
        for row_vals in data_arrays:
            # Detect Sex
            detected = self.detect_sex(row_vals)
            if detected:
                current_sex = detected
                continue 
            
            # Get Category (Handle indentation in Col B)
            cat_val = str(row_vals[0]).strip()
            if cat_val == 'nan' or cat_val == '':
                if len(row_vals) > 1: cat_val = str(row_vals[1]).strip()

            # Filter Garbage
            bad_starts = ('(', '©', 'This table', 'Small random', 'Please note', 'Released at', 'Inquiries')
            if (cat_val.startswith(bad_starts) or cat_val.lower() == 'nan' or cat_val == ''):
                continue
            
            # Filter Empty Data Rows (Headers found inside data)
            # We check if the row has any numbers or '..'
            row_data_part = row_vals[1:]
            has_data = False
            for v in row_data_part:
                s_val = str(v).strip()
                if s_val and s_val.lower() != 'nan':
                    has_data = True; break
            if not has_data: continue 

            # Construct Row
            # Ensure data length matches header length
            data_part = list(row_vals[1:])
            target_len = len(final_header) - 1 # -1 because we add Category
            data_part = data_part[:target_len] 

            clean_row = [current_sex, cat_val] + data_part
            rows_to_keep.append(clean_row)

        if not rows_to_keep: return None

        final_columns = ['Sex', 'Category'] + final_header[1:]
        
        # Safe dataframe creation
        max_len = max(len(r) for r in rows_to_keep)
        if len(final_columns) > max_len: final_columns = final_columns[:max_len]
        
        clean_df = pd.DataFrame(rows_to_keep, columns=final_columns)
        clean_df = clean_df.replace(r'^\s*\.\.\s*$', 0, regex=True)
        clean_df = clean_df.dropna(axis=1, how='all')
        clean_df = self.clean_column_names(clean_df)
        
        return clean_df

    def run(self):
        if not os.path.exists(self.input_dir):
            print(f"Directory not found: {self.input_dir}"); return
        
        files = [f for f in os.listdir(self.input_dir) if f.lower().endswith('.xlsx')]
        for filename in files:
            file_path = os.path.join(self.input_dir, filename)
            print(f"\nStandardizing {filename}...")
            
            try:
                xls = pd.ExcelFile(file_path)
                for sheet in xls.sheet_names:
                    if 'content' in sheet.lower(): continue
                    df = self.clean_sheet(file_path, sheet)
                    if df is not None:
                        base_name = os.path.splitext(filename)[0]
                        safe_sheet = sheet.replace(' ', '_')
                        out_name = f"{base_name}_{safe_sheet}.csv"
                        df.to_csv(os.path.join(self.output_dir, out_name), index=False)
                        print(f"  -> Created {out_name}")
            except Exception as e:
                print(f"[Error] {filename}: {e}")

# --- BRIDGE FUNCTION ---
def FormatFile(input_dir, output_dir):
    print("--- Starting File Formatting ---")
    standardizer = AnalysisReadyStandardizer(input_dir, output_dir)
    standardizer.run()
    print("--- Formatting Complete ---")

if __name__ == "__main__":
    INPUT = "FilePipeline/A_InputData"
    OUTPUT = "FilePipeline/B_FormattedData"
    FormatFile(INPUT, OUTPUT)