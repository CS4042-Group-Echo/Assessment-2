from openpyxl.chart import (
    LineChart,
    Reference,
)
import openpyxl
import csv
import os

def Load(csv_path):
    wb = openpyxl.Workbook()
    ws = wb.active

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=',')

        for row in reader:
            ws.append(row)
    
    for row in ws.iter_rows():
        for x in row:
            try:
                x.value = int(x.value)
            except:
                x.value = x.value
    return wb

def LineChartGen(wb, title, x_axis, y_axis):
    ws = wb.active
    c1 = LineChart()
    c1.title = title
    c1.style = 2
    c1.y_axis.title = y_axis
    c1.x_axis.title = x_axis
    data = Reference(ws, min_col=1, min_row=1, max_col=ws.max_column, max_row=(ws.max_row - 3))
    c1.add_data(data, titles_from_data=True)
    cats = Reference(ws, min_col=1, min_row=1, max_row=ws.max_row)
    c1.set_categories(cats)
    c1.x_axis.delete = False
    c1.y_axis.delete = False
    ws.add_chart(c1, "A19")
    return wb
    
    
def Analysis(csv_path, output_path):
    
    os.makedirs(output_path, exist_ok=True)
    
    wb = Load(csv_path)
    wb = LineChartGen(wb, "Test", "X", "Y")
    wb.save(os.path.join(output_path, "15-19_years.xlsx"))
    