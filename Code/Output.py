import pandas as pd
import os
import shutil

def BuildOutput(input_dir, output_dir):
    i = 0
    output_filename = os.path.join(output_dir, "Output.xlsx")
    os.makedirs(output_dir, exist_ok=True)
    writer = pd.ExcelWriter(output_filename, engine='openpyxl')
    for dirpath, dirnames, filenames in os.walk(input_dir):
        rel = os.path.relpath(dirpath, input_dir)
        for name in filenames:
            i += 1
            if not name.lower().endswith(".xlsx"):
                continue

            src_xlsx = os.path.join(dirpath, name)
            df = pd.read_excel(src_xlsx, sheet_name=None)

            for sheet_name, data in df.items():
                sheet_rel = os.path.join(rel, name + "_" + sheet_name)
                data.to_excel(writer, sheet_name="Sheet_" + str(i), index=False)