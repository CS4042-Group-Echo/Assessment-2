import pandas as pd
import openpyxl
# import numpy as np
# import matplotlib.pyplot as plt

file_path_ADF = "InputData\AdfInputData.xlsx"
file_path_Pop = "InputData\PopulusInputData.xlsx"
file_path_Clean_ADF = "CleanData\AdfCleanData.xlsx"
file_path_Clean_Pop = "CleanData\PopulusCleanData.xlsx"
file_path_Output_ADF = "OutputData\AdfOutputData.xlsx"
file_path_Output_Pop = "OutputData\PopulusOutputData.xlsx"

i = 0
wb = openpyxl.load_workbook(file_path_Clean_ADF)
for sheet in wb.sheetnames:
    ws = wb[sheet]
    if i > 0:
        ws.delete_cols(5, 10)
    i += 1
wb.save(file_path_Output_ADF)

i = 0
wb = openpyxl.load_workbook(file_path_Clean_Pop)
for sheet in wb.sheetnames:
    ws = wb[sheet]
    if i > 0:
        ws.delete_cols(20, 1)
        ws.delete_cols(2, 4)
    i += 1
wb.save(file_path_Output_Pop)

