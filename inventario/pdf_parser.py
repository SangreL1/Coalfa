import sys
import os
import re
import traceback
import shutil
import pdfplumber
import pytesseract
from pdf2image import convert_from_path

# Determinar si estamos en Windows
IS_WINDOWS = sys.platform.startswith('win')

if IS_WINDOWS:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    POPPLER_PATH = r"C:\Users\Coalfa\AppData\Local\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-25.07.0\Library\bin"
    TESSERACT_AVAILABLE = os.path.exists(pytesseract.pytesseract.tesseract_cmd)
else:
    # En Linux / PythonAnywhere, dejamos que busque 'tesseract' y 'pdftoppm' en el PATH del sistema
    POPPLER_PATH = None
    TESSERACT_AVAILABLE = shutil.which('tesseract') is not None


def extraer_datos_factura(pdf_path):
    """
    Extrae productos desde una factura PDF.
    Estrategia 1: pdfplumber (PDF con texto nativo)
    Estrategia 2: OCR con Tesseract (PDF escaneado)
    """
    resultado = _extraer_con_pdfplumber(pdf_path)
    if not resultado:
        if TESSERACT_AVAILABLE:
            print(f"[pdf_parser] pdfplumber no detectó productos en {pdf_path}. Ejecutando OCR de respaldo...")
            resultado = _extraer_con_ocr(pdf_path)
        else:
            print(f"[pdf_parser] pdfplumber no detectó productos en {pdf_path} y OCR (Tesseract) no está disponible en este entorno. Omitiendo OCR.")
    return resultado


def _extraer_con_pdfplumber(pdf_path):
    """Extrae datos de PDF con texto real (no escaneado)."""
    productos = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                for strategy in [
                    {"vertical_strategy": "lines", "horizontal_strategy": "lines"},
                    {"vertical_strategy": "text", "horizontal_strategy": "text"},
                ]:
                    try:
                        table = page.extract_table(strategy)
                        if table and len(table) > 1:
                            p = _parsear_tabla(table)
                            if p:
                                productos.extend(p)
                                break
                    except Exception as ex:
                        print(f"[pdfplumber] Error al parsear tabla: {ex}")
                        traceback.print_exc()
                        continue

                if not productos:
                    text = page.extract_text()
                    if text:
                        productos.extend(_parsear_texto_generico(text))
    except Exception as e:
        print(f"[pdfplumber] Error en {pdf_path}: {e}")
        traceback.print_exc()
    return productos


def _extraer_con_ocr(pdf_path):
    """Convierte el PDF a imagen y aplica OCR con Tesseract."""
    productos = []
    try:
        # Usamos 150 DPI en lugar de 300 para duplicar la velocidad de conversión y reducir consumo de memoria
        if POPPLER_PATH:
            images = convert_from_path(pdf_path, dpi=150, poppler_path=POPPLER_PATH)
        else:
            images = convert_from_path(pdf_path, dpi=150)
            
        if not images:
            return []

        texto_completo = ""
        for img in images:
            config = "--oem 3 --psm 6 -l spa+eng"
            texto = pytesseract.image_to_string(img, config=config)
            texto_completo += texto + "\n"

        if texto_completo.strip():
            # Primero intentar el parser específico (facturas con código de producto)
            productos = _parsear_factura_con_codigo(texto_completo)
            # Si no encontró nada, usar el parser genérico
            if not productos:
                productos = _parsear_texto_generico(texto_completo)

    except Exception as e:
        print(f"[OCR] Error en {pdf_path}: {e}")
        traceback.print_exc()
    return productos


def _parsear_factura_con_codigo(text):
    """
    Parser específico para facturas con código de producto al inicio de línea.
    Detecta líneas como: '123614 | Coca Cola 350cc  4  8.332  33.328  ...'
    Formato Andina/Coca-Cola y similares.
    """
    productos = []

    # Palabras que indican que NO es una línea de producto
    palabras_ignorar = [
        "total", "subtotal", "iva", "neto", "factura", "rut", "fecha",
        "cliente", "proveedor", "precio", "cantidad", "unidad", "descripcion",
        "detalle", "glosa", "valor", "monto", "neto", "telefono", "fono",
        "direccion", "email", "giro", "ciudad", "comuna", "references",
        "referencias", "orden", "compra", "transporte", "nota", "nombre",
        "codigo", "tasa", "monto", "impto", "bruto", "dcto", "descuento",
        "casino", "sucursal", "timbre", "electronico", "resoluc",
    ]

    lineas = text.split("\n")

    for linea in lineas:
        linea_strip = linea.strip()
        if not linea_strip or len(linea_strip) < 10:
            continue

        # Verificar que no sea una línea de cabecera o total
        linea_lower = linea_strip.lower()
        if any(p in linea_lower for p in palabras_ignorar):
            continue

        # PATRÓN 1: Línea que comienza con código numérico (5-6 dígitos) + separador
        # Ej: "123614 | Andif Pina Personal 200cc x 6"4    8.332   33.328"
        #     "120145] Coca Cola LT350cc pack x 1"6   4.281  577.935"
        m = re.match(r'^(\d{4,7})\s*[|\]]\s+(.+)', linea_strip)
        if m:
            nombre_raw = m.group(2)
            nums = _extraer_numeros(nombre_raw)

            if len(nums) >= 2:
                nombre_limpio = _limpiar_nombre_producto(nombre_raw)
                if len(nombre_limpio) < 3:
                    continue

                # Identificar cantidad y precio usando relación: precio × cant ≈ total
                cant, precio = _identificar_cant_precio(nums)

                if cant > 0:
                    productos.append({
                        "producto": nombre_limpio,
                        "cantidad": cant,
                        "precio": precio
                    })
            continue  # siguiente línea

        # PATRÓN 2: Líneas sin código pero con texto + números (genérico)
        # Solo si la línea tiene texto descriptivo + al menos 2 números al final
        m2 = re.match(
            r'^([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñÁÉÍÓÚÑ\s\.\-\/0-9]{4,50}?)\s+'
            r'(\d[\d.,]*)\s+(\d[\d.,]+)\s*$',
            linea_strip, re.IGNORECASE
        )
        if m2:
            desc = m2.group(1).strip()
            if len(desc) > 4:
                try:
                    cant = _to_float(m2.group(2))
                    precio = _to_float(m2.group(3))
                    if cant > 0:
                        productos.append({"producto": desc, "cantidad": cant, "precio": precio})
                except Exception:
                    pass

    return productos


def _extraer_numeros(texto):
    """Extrae todos los números (con puntos/comas) de un texto."""
    patron = r'\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?\b|\b\d+(?:[.,]\d+)?\b'
    matches = re.findall(patron, texto)
    numeros = []
    for m in matches:
        try:
            n = _to_float(m)
            if n > 0:
                numeros.append(n)
        except Exception:
            continue
    return numeros


def _limpiar_nombre_producto(texto):
    """
    Extrae el nombre del producto quitando códigos y números de precios.
    """
    # Quitar lo que está después de múltiples espacios seguidos de números
    nombre = re.split(r'\s{2,}\d', texto)[0]
    # Quitar caracteres raros al inicio/final
    nombre = re.sub(r'^[^A-Z0-9]+', '', nombre, flags=re.IGNORECASE)
    # Si termina en algo como "x 1 6" o similar (ruido de OCR en packs), limpiarlo
    nombre = re.sub(r'\s+x\s+\d+\s*\d*$', '', nombre)
    return nombre.strip()


def _identificar_cant_precio(nums):
    """
    Dada una lista de números extraídos, busca la relación cant * precio = total.
    """
    if not nums: return (1, 0)
    if len(nums) == 1: return (nums[0], 0)

    # Ordenar números de mayor a menor para encontrar el "total"
    nums_sorted = sorted(nums, reverse=True)
    
    # Intentar encontrar i, j tal que i * j ≈ total
    for total in nums_sorted[:3]: # Probar los 3 números más grandes como posibles totales
        for i in range(len(nums)):
            for j in range(len(nums)):
                if i == j: continue
                val_i, val_j = nums[i], nums[j]
                if val_i == total or val_j == total: continue
                
                if abs((val_i * val_j) - total) / max(total, 1) < 0.02:
                    # Encontrado! El menor suele ser cantidad, el mayor precio (si es unitario)
                    # Pero en estas facturas a veces el unitario es mayor que la cantidad
                    # Usualmente la cantidad es un entero "bonito"
                    if val_i.is_integer(): return (val_i, val_j)
                    if val_j.is_integer(): return (val_j, val_i)
                    return (min(val_i, val_j), max(val_i, val_j))

    # Si no hay relación clara, buscar el primer número > 1 (evitar ruidos de OCR como '1')
    candidatos = [n for n in nums if n > 1]
    if len(candidatos) >= 2:
        # Heurística para Andina: Cantidad suele ser el primero, Precio el segundo
        return (candidatos[0], candidatos[1])
    
    return (nums[0], nums[1] if len(nums) > 1 else 0)


def _parsear_tabla(table):
    """Extrae productos de una tabla estructurada detectada por pdfplumber."""
    productos = []
    if not table or len(table) < 2:
        return []

    headers = [str(h).lower().strip() if h else "" for h in table[0]]
    keywords_desc   = ["descrip", "detalle", "producto", "articulo", "nombre", "item", "glosa"]
    keywords_cant   = ["cant", "unid", "cantidad", "ctad", "qty", "kilo", "caja"]
    keywords_precio = ["precio", "unit", "p/caja", "valor", "monto", "neto", "costo"]

    idx_desc, idx_cant, idx_precio = -1, -1, -1
    for i, h in enumerate(headers):
        if idx_desc == -1 and any(k in h for k in keywords_desc):   idx_desc = i
        elif idx_cant == -1 and any(k in h for k in keywords_cant): idx_cant = i
        elif idx_precio == -1 and any(k in h for k in keywords_precio): idx_precio = i

    if idx_desc == -1:
        idx_desc, idx_cant, idx_precio = 0, 1, 2

    ignorar = ["total", "subtotal", "iva", "glosa", "descripcion", "neto"]

    for row in table[1:]:
        if not row or len(row) <= idx_desc or not row[idx_desc]:
            continue
        desc = str(row[idx_desc]).strip().replace("\n", " ")
        if len(desc) < 3:
            continue
        if any(k in desc.lower() for k in ignorar):
            continue
        try:
            cant_raw = str(row[idx_cant]) if idx_cant < len(row) and row[idx_cant] else "1"
            cant = _to_float(cant_raw)
            precio = 0
            if idx_precio != -1 and idx_precio < len(row) and row[idx_precio]:
                precio = _to_float(str(row[idx_precio]))
            if cant > 0:
                productos.append({"producto": desc, "cantidad": cant, "precio": precio})
        except Exception:
            continue
    return productos


def _parsear_texto_generico(text):
    """
    Parser universal que busca patrones de productos en texto libre.
    Busca: Descripción ... [Números]
    """
    productos = []
    palabras_ignorar = [
        "total", "subtotal", "iva", "neto", "factura", "rut", "r.u.t", "fecha",
        "cliente", "proveedor", "telefono", "fono", "direccion", "email", 
        "giro", "ciudad", "comuna", "cond. venta", "observaciones", "pago",
        "senor(es)", "señor(es)", "atencion", "atención"
    ]

    for linea in text.split("\n"):
        linea_strip = linea.strip()
        if len(linea_strip) < 10: continue
        
        linea_lower = linea_strip.lower()
        if any(k in linea_lower for k in palabras_ignorar):
            # Excepción: Si dice "total" pero tiene mucha descripción, podría ser un producto
            if not ("lata" in linea_lower or "unid" in linea_lower or "pack" in linea_lower):
                continue

        # Extraer todos los números potenciales de la línea
        linea_limpia = re.sub(r'(\d+)([A-Z]{2,})', r'\1 \2', linea_strip)
        nums = _extraer_numeros(linea_limpia)
        
        if len(nums) >= 2:
            # Buscamos el último bloque de texto antes de la secuencia de números
            # Generalmente el nombre termina antes de los números que representan Qty y Precio
            # En formatos como 'BEBIDA ... 120 UN 496.5333'
            # Vamos a buscar el primer número que parece ser Cantidad o Precio
            match_nums = list(re.finditer(r'\b\d[\d.,]*\b', linea_strip))
            if match_nums:
                # El nombre suele terminar antes del primer número que NO es parte de un código pequeño
                # Pero en OCR el nombre puede tener números (350 CC). 
                # Una mejor técnica: El nombre es todo hasta que empiezan los campos de la tabla (múltiples espacios)
                partes = re.split(r'\s{2,}', linea_strip)
                if len(partes) > 1:
                    nombre_raw = partes[0].strip()
                    # Si el nombre es muy corto o solo números, probar con la siguiente parte
                    if len(nombre_raw) < 5 or nombre_raw.isdigit():
                        nombre_raw = (partes[0] + " " + partes[1]).strip()
                else:
                    nombre_raw = linea_strip
                
                # Limpiar el nombre de los números que ya extrajimos para cantidad/precio si quedaron al final
                nombre_limpio = _limpiar_nombre_producto(nombre_raw)
                
                if len(nombre_limpio) > 4:
                    cant, precio = _identificar_cant_precio(nums)
                    if cant > 0:
                        productos.append({
                            "producto": nombre_limpio,
                            "cantidad": cant,
                            "precio": precio
                        })
    return productos


def _to_float(s):
    """Convierte string de número chileno/europeo a float."""
    s = str(s).strip()
    s = re.sub(r'[^0-9.,]', '', s)
    if not s:
        return 0.0
    # Punto Y coma → punto es miles, coma es decimal
    if "." in s and "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        partes = s.split(",")
        if len(partes[-1]) == 3:   # coma como separador de miles
            s = s.replace(",", "")
        else:                       # coma como decimal
            s = s.replace(",", ".")
    elif "." in s:
        partes = s.split(".")
        if all(len(p) == 3 for p in partes[1:]):  # todos los bloques post-punto son de 3 dígitos → miles
            s = s.replace(".", "")
    return float(s) if s else 0.0
