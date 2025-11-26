import pandas as pd
import openpyxl
# import numpy as np
# import matplotlib.pyplot as plt

file_path_ADF = "InputData\AdfInputData.xlsx"
file_path_Pop = "InputData\PopulusInputData.xlsx"
file_path_Clean_ADF = "CleanData\AdfCleanData.xlsx"
file_path_Clean_Pop = "CleanData\PopulusCleanData.xlsx"
file_path_Output = "OutputData\OutputData.xlsx"

wb = openpyxl.load_workbook(file_path_ADF)
wb.save(file_path_Clean_ADF)
wb = openpyxl.load_workbook(file_path_Pop)
wb.save(file_path_Clean_Pop)

i = 0
column = 0
wb = openpyxl.load_workbook(file_path_Clean_Pop)
for sheet in wb.sheetnames:
    ws = wb[sheet]
    if i > 0:
        for row in ws.iter_rows(min_row=10, min_col=2, max_col=ws.max_column, max_row=12):
            for cell in row:
                if cell.value is not None and ("Total") in str(cell.value):
                    column = cell.column
                    cell.value = "Average"
        # for cell in ws.iter_cols(min_col=column, max_col=column, min_row=13, max_row=ws.max_row):
            # cell.value = cell.value / (ws.max_row - 1) #not working due to merged cells 'male' and 'female', solution is to reformat subtitles into row headings
    i += 1
wb.save(file_path_Clean_Pop)

i = 0
wb = openpyxl.load_workbook(file_path_Clean_ADF)
for sheet in wb.sheetnames:
    ws = wb[sheet]
    if i > 0:
        ws.delete_cols(5, 10)
    i += 1
wb.save(file_path_Output)
