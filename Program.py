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

wb = openpyxl.load_workbook(file_path_ADF)
wb.save(file_path_Clean_ADF)
wb = openpyxl.load_workbook(file_path_Pop)
wb.save(file_path_Clean_Pop)

i = 0
wb = openpyxl.load_workbook(file_path_Clean_Pop)
for sheet in wb.sheetnames:
    ws = wb[sheet]
    if i > 0:
        ws.delete_cols(20, 1)
        ws.delete_cols(2, 4)
    i += 1
    cellsum = 0
    ws.cell(row=14, column=ws.max_column + 1).value = "Average"
    for row in ws.iter_rows(min_row=15,min_col=2, max_col=ws.max_column, max_row=ws.max_row):
        for cell in row:
            if cell.value != None and isinstance(cell.value, (int, float)):
                cellsum += cell.value
                print("test")
        ws.cell(row=row[0].row, column=ws.max_column + 1).value = cellsum/(ws.max_column -1)
wb.save(file_path_Clean_Pop)

i = 0
wb = openpyxl.load_workbook(file_path_Clean_ADF)
for sheet in wb.sheetnames:
    ws = wb[sheet]
    if i > 0:
        ws.delete_cols(5, 10)
    i += 1
wb.save(file_path_Output_ADF)
