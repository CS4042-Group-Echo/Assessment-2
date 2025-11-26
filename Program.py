import pandas as pd
# import openpyxl
# import numpy as np
# import matplotlib.pyplot as plt

file_path_ADF = "InputData\AdfInputData.xlsx"
file_path_Pop = "InputData\PopulusInputData.xlsx"

df_ADF = pd.read_excel(file_path_ADF, sheet_name="Table 2")
df_ADF_str = df_ADF.astype(str)

df_Pop = pd.read_excel(file_path_Pop, sheet_name="Table 1")
df_Pop_str = df_Pop.astype(str)


print("ADF DataFrame (as strings):")
print(df_Pop_str)