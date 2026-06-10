import openpyxl

wb = openpyxl.load_workbook(r"c:\Users\Coalfa\Desktop\RRHHBG\Gestios_Citas_IS\Planilla de invntario Marzo 26.xlsx", data_only=True)
sheet = wb.active
print(f"Sheet name: {sheet.title}")

for i, row in enumerate(sheet.iter_rows(values_only=True)):
    print(row)
    if i > 5:
        break
