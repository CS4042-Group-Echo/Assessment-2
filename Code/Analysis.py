import openpyxl
import csv
import os
import shutil

from openpyxl.chart import (
    LineChart,
    Reference,
)


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
                x.value = float(x.value)
            except:
                pass
    return wb

def LineChartGen(wb, title, x_axis, y_axis):
    ws = wb.active
    c1 = LineChart()
    c1.title = title
    c1.style = 2
    c1.y_axis.title = y_axis
    c1.x_axis.title = x_axis
    data = Reference(ws, min_col=2, max_col=ws.max_column, min_row=1, max_row=ws.max_row)
    c1.add_data(data, titles_from_data=True)
    cats = Reference(ws, min_col=1, max_col=1, min_row=2, max_row=ws.max_row)
    c1.set_categories(cats)
    c1.x_axis.delete = False
    c1.y_axis.delete = False
    ws.add_chart(c1, "A19")
    return wb
    
    
def Analysis(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # clone folder structure and analyse csv files into excels
    for dirpath, dirnames, filenames in os.walk(input_dir):
        rel = os.path.relpath(dirpath, input_dir)
        target_dir = os.path.join(output_dir, rel) if rel != "." else output_dir
        os.makedirs(target_dir, exist_ok=True)

        for name in filenames:
            if not name.lower().endswith(".csv"):
                continue

            src_csv = os.path.join(dirpath, name)
            dst_csv = os.path.join(target_dir, name)
            shutil.copy2(src_csv, dst_csv)

            # make excel file
            wb = Load(dst_csv)
            wb = LineChartGen(wb, title=name, x_axis="X", y_axis="Y")

            xlsx_path = os.path.splitext(dst_csv)[0] + ".xlsx"
            wb.save(xlsx_path)

            # delete analysed csv
            os.remove(dst_csv)
    