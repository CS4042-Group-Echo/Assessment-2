import pandas as pd
import os
import shutil

def BuildOutput(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    dirpath, dirnames, filenames = next(os.walk(input_dir))
    for dirpath, dirnames, filenames in os.walk(input_dir):
        rel = os.path.relpath(dirpath, input_dir)
        target_dir = os.path.join(output_dir, rel) if rel != "." else output_dir
        os.makedirs(target_dir, exist_ok=True)
        for name in filenames:
            if not name.lower().endswith(".xlsx"):
                continue

            src_xlsx = os.path.join(dirpath, name)
            dst_xlsx = os.path.join(target_dir, name)
            shutil.copy2(src_xlsx, dst_xlsx)