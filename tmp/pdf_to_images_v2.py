import pypdfium2 as pdfium
import os

invoice_dir = r"C:\Users\Coalfa\Desktop\RRHHBG\Gestios_Citas_IS\FACTURAS INVENTARIO"
output_dir = r"C:\Users\Coalfa\Desktop\RRHHBG\Gestios_Citas_IS\tmp\invoice_images_v2"
os.makedirs(output_dir, exist_ok=True)

pdfs = [f for f in os.listdir(invoice_dir) if f.endswith('.pdf')]

for pdf_file in sorted(pdfs):
    path = os.path.join(invoice_dir, pdf_file)
    base_name = os.path.splitext(pdf_file)[0]
    
    print(f"Opening: {pdf_file}")
    doc = pdfium.PdfDocument(path)
    print(f"Total pages: {len(doc)}")
    for page_num in range(len(doc)):
        page = doc[page_num]
        # 300 DPI - better quality
        bitmap = page.render(scale=300/72)
        pil_image = bitmap.to_pil()
        
        out_path = os.path.join(output_dir, f"{base_name}_p{page_num+1}.png")
        pil_image.save(out_path)
        print(f"  Saved: {out_path}")

print("Extraction complete.")
