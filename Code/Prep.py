import os
import pandas as pd
import shutil

def PrepFile(input_dir, output_dir):

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # table 1 paths (originals in cleaned dir)
    adf_path = os.path.join(input_dir, "AdfInputData_Table_1.csv")
    pop_path = os.path.join(input_dir, "PopulusInputData_Table_1.csv")

    # make prepped table 1 in output dir
    prepped_path = os.path.join(output_dir, "AdfInputData_Table_1_Prepped.csv")
    shutil.copy(adf_path, prepped_path)

    adf = pd.read_csv(prepped_path)
    populus = pd.read_csv(pop_path)

    # totals row from Populus
    populus_totals_row = populus.iloc[41]
    populus_values = populus_totals_row.iloc[5:20]

    # remove last 4 cols from ADF
    if adf.shape[1] >= 4:
        adf = adf.iloc[:, :-4]
    else:
        raise ValueError("ADF table has fewer than 4 columns.")

    # new column
    new_col_name = "PopulationHealthTotal"
    adf[new_col_name] = pd.NA

    # fill Persons block
    start_idx = 32
    for i, value in enumerate(populus_values):
        row_idx = start_idx + i
        if row_idx < len(adf):
            adf.loc[row_idx, new_col_name] = value

    # drop separator rows
    adf = adf.drop([15, 31, 47], errors="ignore")

    adf.to_csv(prepped_path, index=False)

    # copy all other csvs from input to output
    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(".csv"):
            continue
        if filename == "AdfInputData_Table_1.csv":
            continue  # handled above
        src = os.path.join(input_dir, filename)
        dst = os.path.join(output_dir, filename)
        shutil.copy(src, dst)

    # drop last 3 cols from all other ADF tables in output dir
    for filename in os.listdir(output_dir):
        if not filename.lower().endswith(".csv"):
            continue
        if not filename.startswith("Adf"):
            continue
        if filename == "AdfInputData_Table_1_Prepped.csv":
            continue  # keep full prepped table 1

        path = os.path.join(output_dir, filename)
        df = pd.read_csv(path)
        if df.shape[1] > 3:
            df = df.iloc[:, :-3]
        df.to_csv(path, index=False)
