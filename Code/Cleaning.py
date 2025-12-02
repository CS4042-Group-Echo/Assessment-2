import os
import csv
import shutil
import re

def CleanFile(broken_dir, clean_dir):
    
    os.makedirs(clean_dir, exist_ok=True)

    # Copy folder from C to D
    shutil.copytree(broken_dir, clean_dir, dirs_exist_ok=True)

    # Loop through all CSVs in D_CleanData
    for root, _, files in os.walk(clean_dir):
        for file in files:
            if not file.endswith(".csv"):
                continue

            csv_path = os.path.join(root, file)

            with open(csv_path, "r", encoding="utf-8") as f:
                rows = list(csv.reader(f))

            if not rows:
                continue
            
            #avoid rows we havent messed with 
            header = rows[0]      # preserved
            data = rows[1:]       # fix only these rows

            for row in data:
                for i in range(len(row)):

                    # Skip column A 
                    if i == 0:
                        continue

                    cell = row[i]
                    # If blank cell
                    if cell in ("", None):
                        row[i] = "0"
                        continue

                    value = str(cell).strip()

                    # If it's already a number (string or int)
                    if value.isdigit():
                        row[i] = int(value)
                        continue

                    # Contains digits + letters remove non-digits
                    if re.search(r"\d", value):
                        cleaned = re.sub(r"[^\d]", "", value)
                        if cleaned.isdigit():
                            row[i] = int(cleaned)
                            continue

                    # If still not numeric after cleaning, leave it
                    row[i] = value

            # Save cleaned CSV
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(data)

