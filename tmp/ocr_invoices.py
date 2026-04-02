import pypdfium2 as pdfium
import pytesseract
from PIL import Image
import os
import io

# Configurar ruta de tesseract si es necesario
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

invoice_dir = r"C:\Users\Coalfa\Desktop\RRHHBG\Gestios_Citas_IS\FACTURAS INVENTARIO"
pdfs = [f for f in os.listdir(invoice_dir) if f.endswith('.pdf')]

for pdf_file in sorted(pdfs):
    path = os.path.join(invoice_dir, pdf_file)
    print(f"\n{'='*60}")
    print(f"ARCHIVO: {pdf_file}")
    print('='*60)
    
    try:
        doc = pdfium.PdfDocument(path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Render at 300 DPI for good OCR quality
            bitmap = page.render(scale=300/72)
            pil_image = bitmap.to_pil()
            
            print(f"\n--- Página {page_num+1} ---")
            # OCR with Spanish language
            try:
                text = pytesseract.image_to_string(pil_image, lang='spa')
                print(text)
            except Exception as e:
                # Fallback to default language
                text = pytesseract.image_to_string(pil_image)
                print(text)
    except Exception as e:
        print(f"Error procesando {pdf_file}: {e}")
