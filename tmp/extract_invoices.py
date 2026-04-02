import pdfplumber
import os

invoice_dir = r"C:\Users\Coalfa\Desktop\RRHHBG\Gestios_Citas_IS\FACTURAS INVENTARIO"
pdfs = [f for f in os.listdir(invoice_dir) if f.endswith('.pdf')]

for pdf_file in sorted(pdfs):
    path = os.path.join(invoice_dir, pdf_file)
    print(f"\n{'='*60}")
    print(f"ARCHIVO: {pdf_file}")
    print('='*60)
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            print(f"\n--- Página {i+1} ---")
            text = page.extract_text()
            if text:
                print(text)
            # Also try to extract tables
            tables = page.extract_tables()
            if tables:
                print("\n[TABLA DETECTADA]")
                for t, table in enumerate(tables):
                    print(f"Tabla {t+1}:")
                    for row in table:
                        print(" | ".join(str(c) if c else "" for c in row))
