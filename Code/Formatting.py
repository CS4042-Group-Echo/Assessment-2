import os
import shutil
import openpyxl


def IsDividerRow(Sheet, RowNumber):
    MaxColumn = Sheet.max_column
    Values = []
    for ColumnNumber in range(1, MaxColumn + 1):
        Value = Sheet.cell(row=RowNumber, column=ColumnNumber).value
        if Value not in (None, ""):
            Values.append(str(Value).strip())

    if len(Values) != 1:
        return False

    Text = Values[0]
    return Text.isupper() and any(ch.isalpha() for ch in Text)


def FormatFile(input_dir, formatted_dir):
    os.makedirs(formatted_dir, exist_ok=True)  # make sure B_FormattedData exists

    # Loop through each file in the input folder
    for filename in os.listdir(input_dir):
        if filename.endswith(".xlsx"):
            Source = os.path.join(input_dir, filename)

            # Clone into Formatted folder rename to "A_(CurrentFileName)"
            NewName = "A_" + filename
            Destination = os.path.join(formatted_dir, NewName)
            shutil.copy(Source, Destination)

            # Open the copied workbook and start formatting
            Workbook = openpyxl.load_workbook(Destination)

            # Apply formatting to sheet 2 and onwards (skip the first sheet)
            for Index, SheetName in enumerate(Workbook.sheetnames):
                if Index == 0:
                    continue  # skip sheet 1 (usually 'Contents')

                Sheet = Workbook[SheetName]

                # Delete the first 7 rows
                Sheet.delete_rows(1, 7)

                # Delete any completely empty rows (scan bottom → top)
                for RowNumber in range(Sheet.max_row, 0, -1):
                    if all(
                        Sheet.cell(row=RowNumber, column=ColumnNumber).value in (None, "")
                        for ColumnNumber in range(1, Sheet.max_column + 1)
                    ):
                        Sheet.delete_rows(RowNumber)

                # Find the first data row in column A
                FirstDataRow = None
                for RowNumber in range(1, Sheet.max_row + 1):
                    CellValue = Sheet.cell(row=RowNumber, column=1).value
                    if CellValue is None or str(CellValue).strip() == "":
                        continue
                    # if this row is a divider, it's not data
                    if IsDividerRow(Sheet, RowNumber):
                        continue
                    FirstDataRow = RowNumber
                    break

                if FirstDataRow is None or FirstDataRow <= 1:
                    continue

                # Header rows are everything above the first data row
                HeaderRows = list(range(1, FirstDataRow))  # e.g. [1,2] or [1,2,3]

                # Keep divider rows, but don't merge them into headers
                NonDividerHeaderRows = [r for r in HeaderRows if not IsDividerRow(Sheet, r)]

                if not NonDividerHeaderRows:
                    continue

                MaxColumn = Sheet.max_column

                # Build combined header text for each column
                CombinedHeaders = {}
                for ColumnNumber in range(1, MaxColumn + 1):
                    Parts = []
                    for RowNumber in NonDividerHeaderRows:
                        Value = Sheet.cell(row=RowNumber, column=ColumnNumber).value
                        if Value is not None and str(Value).strip() != "":
                            Parts.append(str(Value).strip())
                    CombinedHeaders[ColumnNumber] = " ".join(Parts) if Parts else None

                # Insert a new header row at the very top
                Sheet.insert_rows(1)

                # Write the combined headers into the new row 1
                for ColumnNumber in range(1, MaxColumn + 1):
                    HeaderText = CombinedHeaders.get(ColumnNumber)
                    if HeaderText is not None:
                        Sheet.cell(row=1, column=ColumnNumber, value=HeaderText)

                #  Delete the old non-divider header rows
                RowsToDelete = [r + 1 for r in NonDividerHeaderRows]
                for RowNumber in sorted(RowsToDelete, reverse=True):
                    Sheet.delete_rows(RowNumber, 1)


            Workbook.save(Destination)
            print(f"[FormatFile] Saved formatted workbook: {Destination}")
