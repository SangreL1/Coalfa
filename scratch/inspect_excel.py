import openpyxl

wb = openpyxl.load_workbook('Planilla de inventario 31-05-26.xlsx', data_only=True)
print("Sheets found:", wb.sheetnames)
sheet = wb.active
print("Active sheet title:", sheet.title)

# Print first 20 rows
for r in range(1, 25):
    row_vals = [cell.value for cell in sheet[r]]
    if any(row_vals is not None for row_vals in row_vals):
        print(f"Row {r}: {row_vals[:12]}")

