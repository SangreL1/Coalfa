import openpyxl
import json

def inspect_excel(file_path):
    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet = wb.active
        rows = list(sheet.iter_rows(values_only=True))
        return rows[:20]
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    file_path = "planilla de inventario 30-04-26.xlsx"
    result = inspect_excel(file_path)
    for i, row in enumerate(result):
        print(f"{i}: {row}")
