import pandas as pd
import os

class AnalysisReadyStandardizer:
    def __init__(self, input_files):
        self.input_files = input_files

    def find_header_row(self, df):
        """Finds the row containing 'Total' to define column names."""
        for i, row in df.iterrows():
            row_str = [str(x).lower().strip() for x in row if pd.notna(x)]
            # We look for a row that has 'total' and at least 3 columns of data
            if any('total' in x for x in row_str) and len(row_str) > 2:
                return i
        return None

    def detect_sex(self, row):
        """
        Scans the first 3 columns to find 'MALES', 'FEMALES', or 'PERSONS'.
        Returns the found sex, or None if not found.
        """
        # Look at the first 3 columns (handling indentation)
        check_vals = [str(x).upper().strip() for x in row.iloc[0:3] if pd.notna(x)]
        
        if 'MALES' in check_vals: return 'Males'
        if 'FEMALES' in check_vals: return 'Females'
        if 'PERSONS' in check_vals: return 'Persons'
        return None

    def clean_sheet(self, file_path, sheet_name):
        try:
            df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        except:
            return None
        
        header_idx = self.find_header_row(df_raw)
        if header_idx is None: return None

        df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_idx)
        df.columns = [str(c).strip() for c in df.columns]
        df.rename(columns={df.columns[0]: 'Category'}, inplace=True)

        rows_to_keep = []
        current_sex = "Persons"
        
        for idx, row in df.iterrows():
            # 1. Detect Sex
            detected = self.detect_sex(row)
            if detected:
                current_sex = detected
                continue 
            
            # 2. Grab Category Label (Column A or B)
            cat_val = str(row.iloc[0]).strip()
            if cat_val == 'nan' or cat_val == '':
                cat_val = str(row.iloc[1]).strip()

            # --- IMPROVED GARBAGE FILTER ---
            # Catches standard ABS footer text
            bad_starts = ('(', '©', 'This table', 'Small random', 'Please note', 'Released at', 'Inquiries', '.. Not applicable')
            
            if (cat_val.startswith(bad_starts) or 
                cat_val.lower() == 'nan' or cat_val == ''):
                continue
            # -------------------------------
            
            clean_row = row.copy()
            clean_row['Category'] = cat_val 
            clean_row['Sex'] = current_sex
            rows_to_keep.append(clean_row)

        if not rows_to_keep: return None

        clean_df = pd.DataFrame(rows_to_keep)
        cols = ['Sex', 'Category'] + [c for c in clean_df.columns if c not in ['Sex', 'Category']]
        return clean_df[cols]

    def run(self):
        if not os.path.exists("StandardisedData"): os.makedirs("StandardisedData")
        
        for file_path in self.input_files:
            if not os.path.exists(file_path): continue
            print(f"Standardizing {file_path}...")
            xls = pd.ExcelFile(file_path)
            
            for sheet in xls.sheet_names:
                if 'content' in sheet.lower(): continue
                
                df = self.clean_sheet(file_path, sheet)
                if df is not None:
                    name = f"StandardisedData/{os.path.basename(file_path).replace('.xlsx','')}_{sheet.replace(' ','_')}.csv"
                    df.to_csv(name, index=False)
                    print(f"  -> Created {name}")

# Run
files = ['BrokenData/AdfBrokenData.xlsx', 'BrokenData/PopulusBrokenData.xlsx']
Standardizer = AnalysisReadyStandardizer(files)
Standardizer.run()