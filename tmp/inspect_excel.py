import pandas as pd
import json

df = pd.read_excel('Planilla de invntario Marzo 26.xlsx')
# Clean names
df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]

# Find the main data (Producto, Cantidad, Precio, Total)
# Usually starts where "NOMBRE PRODUCTO" is found
records = []
for i, row in df.iterrows():
    if pd.isna(row.iloc[1]): continue
    # Try to identify columns by context if headers are messy
    # Based on previous output, col 1 is Name, col 2 is Brand/Details? col 3 is Category?
    # Let's just dump the first few rows to see
    records.append(row.to_dict())
    if len(records) > 50: break

print(json.dumps(records, indent=2, default=str))
