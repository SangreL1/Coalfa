import openpyxl

wb = openpyxl.load_workbook('Planilla de inventario 31-05-26.xlsx', data_only=True)
sheet = wb['Hoja1']

concepts = set()
units = set()
total_rows = 0
valid_rows = 0
skus = set()

for r in range(7, sheet.max_row + 1):
    row_vals = [cell.value for cell in sheet[r]]
    if not row_vals or len(row_vals) < 6:
        continue
    concepto, articulo, sku, um, stock, costo_unit = row_vals[0], row_vals[1], row_vals[2], row_vals[3], row_vals[4], row_vals[5]
    if articulo is not None and str(articulo).strip() != "":
        total_rows += 1
        concepts.add(concepto)
        units.add(um)
        if sku:
            skus.add(sku)
        if stock is not None or costo_unit is not None:
            valid_rows += 1

print(f"Total rows with articles: {total_rows}")
print(f"Valid rows with stock/cost: {valid_rows}")
print("Unique concepts (Column A):", sorted([str(c) for c in concepts]))
print("Unique units (Column D):", sorted([str(u) for u in units]))
print(f"Unique SKUs count: {len(skus)}")
