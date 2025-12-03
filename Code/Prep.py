import os
import pandas as pd
import shutil

def PrepFile(input_dir, output_dir):

    # make sure output folder exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # paths to ADF + Populus CSVs inside the cleaned directory
    adf_path = os.path.join(input_dir, "AdfInputData_Table_1.csv")
    pop_path = os.path.join(input_dir, "PopulusInputData_Table_1.csv")

    # clone ADF file into prepped folder
    prepped_path = os.path.join(output_dir, "AdfInputData_Table_1_Prepped.csv")
    shutil.copy(adf_path, prepped_path)

    # load both files
    adf = pd.read_csv(prepped_path)
    populus = pd.read_csv(pop_path)

    # pull totals row from Populus (row 42)
    populus_totals_row = populus.iloc[41]
    populus_values = populus_totals_row.iloc[5:20]   # 15–19 to 85+

    # remove last 4 columns from ADF
    if adf.shape[1] >= 4:
        adf = adf.iloc[:, :-4]
    else:
        raise ValueError("ADF table has fewer than 4 columns.")

    # add new column
    new_col_name = "PopulationHealthTotal"
    adf[new_col_name] = pd.NA

    # put Populus age values into ADF Persons block
    start_idx = 32
    for i, value in enumerate(populus_values):
        row_idx = start_idx + i
        if row_idx < len(adf):
            adf.loc[row_idx, new_col_name] = value

    # delete unwanted empty/separator rows
    adf = adf.drop([15, 31, 47], errors="ignore")

    # save final prepped output
    adf.to_csv(prepped_path, index=False)
    print(f"[PrepFile] Created prepped file: {prepped_path}")
