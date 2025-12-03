import os
import pandas as pd
import shutil

def MergePopulusIntoAdf():
    # base path and data folder
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, "..", "filepipeline", "StandardisedCleanData")
    adf_path = os.path.join(data_dir, "AdfInputData_Table_1.csv")
    pop_path = os.path.join(data_dir, "PopulusInputData_Table_1.csv")

    # clone the adf csv before editing
    prepped_path = os.path.join(data_dir, "AdfInputData_Table_1_Prepped.csv")
    shutil.copy(adf_path, prepped_path)
    adf = pd.read_csv(prepped_path)
    populus = pd.read_csv(pop_path)

    #get totals row from Populus
    populus_totals_row = populus.iloc[41]
    populus_values = populus_totals_row.iloc[5:20]

    # remove last 4 columns from ADF
    if adf.shape[1] >= 4:
        adf = adf.iloc[:, :-4]
    else:
        raise ValueError("ADF table has fewer than 4 columns.")

    #add new column for population totals
    new_col_name = "PopulationHealthTotal"
    adf[new_col_name] = pd.NA

    #put the values in the Persons section
    start_idx = 32
    for i, value in enumerate(populus_values):
        row_idx = start_idx + i
        if row_idx < len(adf):
            adf.loc[row_idx, new_col_name] = value

    adf = adf.drop([15, 31, 47], errors="ignore")

    #save updated prepped file
    adf.to_csv(prepped_path, index=False)


MergePopulusIntoAdf()
