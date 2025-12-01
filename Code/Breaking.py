import os
import csv
import random
import shutil


def BreakFile(formatted_dir, broken_dir):

    # clone full folder structure from B to C
    os.makedirs(broken_dir, exist_ok=True)
    shutil.copytree(formatted_dir, broken_dir, dirs_exist_ok=True)

    # loop through every CSV in C_BrokenData and apply corruption
    for root, _, files in os.walk(broken_dir):
        for file in files:
            if not file.endswith(".csv"):
                continue

            csv_path = os.path.join(root, file)

            with open(csv_path, "r", encoding="utf-8") as f:
                rows = list(csv.reader(f))

            if not rows:
                continue
                
            #dont modifiy row or column headers
            header = rows[0]    
            data = rows[1:]

            for row in data:
                if not row:
                    continue

                # randomly choose a corruption to apply
                corruption = random.choice(["delete", "stringify", "typo"])

                # delete random cell entry (set blank)
                if corruption == "delete":
                    idx = random.randint(0, len(row) - 1)
                    row[idx] = ""

                # convert number to string
                elif corruption == "stringify":
                    idx = random.randint(0, len(row) - 1)
                    value = row[idx]
                    if isinstance(value, (int, float)) or (isinstance(value, str) and value.isdigit()):
                        row[idx] = str(value)  # convert to string

                # typo corruption: inject a random character into the value
                elif corruption == "typo":
                    idx = random.randint(0, len(row) - 1)
                    value = str(row[idx])
                    if value not in ("", None):
                        insert_at = random.randint(0, len(value))
                        typo_char = random.choice(["0", "1", "4", "x", "?"])
                        row[idx] = value[:insert_at] + typo_char + value[insert_at:]

            # write corrupted CSV back
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(data)
