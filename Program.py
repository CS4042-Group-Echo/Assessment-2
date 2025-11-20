import pandas as pd
# import openpyxl
# import numpy as np
# import matplotlib.pyplot as plt

file_path_ADF = "Input Data\ADF Input Data.xlsx"
file_path_Pop = "Input Data\Populus Data Input.xlsx"

df_ADF = pd.read_excel(file_path_ADF, sheet_name="Data")
df_ADF_str = df_ADF.astype(str)

df_Pop = pd.read_excel(file_path_Pop, sheet_name="Data")
df_Pop_str = df_Pop.astype(str)