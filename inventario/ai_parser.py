"""
ai_parser.py — Análisis de facturas con Gemini Vision API (REST nativo).
Extrae productos, cantidades, precios y categorías desde PDF o imagen de factura.
"""
import base64
import json
import logging
import os
import re
import tempfile
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

CATEGORIAS_VALIDAS = [
    "ABARROTES", "CARNES", "PESCADOS", "LACTEOS",
    "FRUTAS", "CONGELADOS", "BEBIDAS", "LIMPIEZA",
    "VESTUARIO", "EPP", "OTRO",
]
UNIDADES_VALIDAS = ["KG", "G", "L", "ML", "UN", "CAJA"]

MODELOS_GEMINI = [
    "gemini-3.1-flash-lite",
    "gemini-2.5-pro",
    "gemini-3.8-flash",
    "gemini-flash-latest",
]

PROMPT_FACTURA = """Eres un asistente experto en análisis de facturas y guías de despacho de proveedores de alimentos y suministros en Chile.

Analiza el documento adjunto y extrae TODOS los productos con sus cantidades, unidades y precios.

Responde ÚNICAMENTE con un JSON válido con esta estructura exacta (sin texto previo ni posterior, sin markdown adicional):
{
  "proveedor": "Nombre del proveedor o emisor",
  "numero_factura": "Número de factura o guía",
  "fecha": "YYYY-MM-DD",
  "productos": [
    {
      "nombre": "Nombre completo y descriptivo del producto",
      "cantidad": 10.0,
      "unidad": "KG",
      "precio_unitario": 1500.0,
      "precio_total": 15000.0,
      "categoria": "ABARROTES",
      "fecha_vencimiento": "YYYY-MM-DD"
    }
  ]
}

Reglas importantes:
- "unidad" DEBE ser una de: KG, G, L, ML, UN, CAJA
- "categoria" DEBE ser una de: ABARROTES, CARNES, PESCADOS, LACTEOS, FRUTAS, CONGELADOS, BEBIDAS, LIMPIEZA, VESTUARIO, EPP, OTRO
- "precio_unitario" es el valor por unidad o kilo (precio final o con IVA si viene indicado así)
- Para empaques múltiples tipo "7 cajas de 2 bolsas de 5kg", la cantidad total es 70 y la unidad es "KG"
- Si la fecha de vencimiento no aparece, deja "" (cadena vacía)
- Extrae TODOS los productos de la lista
"""


def _get_gemini_api_key():
    from django.conf import settings
    key = getattr(settings, "GEMINI_API_KEY", None) or os.environ.get("GEMINI_API_KEY", "")
    return key.strip()


def _pdf_a_imagen_base64(pdf_path):
    imagenes_b64 = []
    try:
        from pdf2image import convert_from_path
        import sys
        kwargs = {"dpi": 140, "first_page": 1, "last_page": 3}
        if sys.platform.startswith("win"):
            poppler_win = r"C:\Users\Coalfa\AppData\Local\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-25.07.0\Library\bin"
            if os.path.exists(poppler_win):
                kwargs["poppler_path"] = poppler_win
        images = convert_from_path(pdf_path, **kwargs)
        for img in images:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                img.save(tmp.name, "JPEG", quality=85)
                with open(tmp.name, "rb") as f:
                    imagenes_b64.append(base64.b64encode(f.read()).decode("utf-8"))
                try:
                    os.unlink(tmp.name)
                except Exception:
                    pass
    except Exception as e:
        logger.warning(f"pdf2image falló: {e}. Intentando PyMuPDF...")
        try:
            import fitz
            doc = fitz.open(pdf_path)
            for page_num in range(min(3, len(doc))):
                pix = doc[page_num].get_pixmap(matrix=fitz.Matrix(2, 2))
                imagenes_b64.append(base64.b64encode(pix.tobytes("jpeg")).decode("utf-8"))
            doc.close()
        except Exception as e2:
            logger.error(f"PyMuPDF también falló: {e2}")
    return imagenes_b64


def _imagen_a_base64(imagen_path):
    with open(imagen_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _llamar_gemini_rest(api_key, imagenes_b64, mime_type):
    parts = [{"text": PROMPT_FACTURA}]
    for b64 in imagenes_b64:
        parts.append({
            "inlineData": {
                "mimeType": mime_type,
                "data": b64,
            }
        })

    payload = json.dumps({
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 4096,
        }
    }).encode("utf-8")

    ultimo_error = None
    for modelo in MODELOS_GEMINI:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            logger.info(f"Factura analizada exitosamente con modelo {modelo}")
            return _parsear_respuesta_gemini(raw_text)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            logger.warning(f"Gemini {modelo} HTTP {e.code}: {body[:150]}")
            ultimo_error = f"HTTP {e.code} en {modelo}"
            continue
        except Exception as e:
            logger.warning(f"Gemini {modelo} error: {e}")
            ultimo_error = f"{modelo}: {str(e)}"
            continue

    return {"exitoso": False, "error": f"No se pudo contactar a Gemini ({ultimo_error})"}


def _parsear_respuesta_gemini(raw_text):
    match = re.search(r'\{[\s\S]*\}', raw_text)
    if not match:
        return {"exitoso": False, "error": f"Respuesta no reconocida de Gemini: {raw_text[:200]}"}

    try:
        data = json.loads(match.group())
    except json.JSONDecodeError as e:
        return {"exitoso": False, "error": f"JSON no válido de Gemini: {e}"}

    productos = []
    mapeo_unidades = {
        "KILOGRAMO": "KG", "KILOS": "KG", "KILO": "KG",
        "LITRO": "L", "LITROS": "L", "MILILITROS": "ML",
        "GRAMOS": "G", "GRAMO": "G", "UNIDAD": "UN",
        "CAJAS": "CAJA", "BOTELLA": "UN", "PAQUETE": "UN",
    }

    for p in data.get("productos", []):
        nombre = str(p.get("nombre", "")).strip()
        if not nombre:
            continue

        u = str(p.get("unidad", "UN")).upper().strip()
        unidad = mapeo_unidades.get(u, u if u in UNIDADES_VALIDAS else "UN")

        cat = str(p.get("categoria", "OTRO")).upper().strip()
        categoria = cat if cat in CATEGORIAS_VALIDAS else "OTRO"

        try:
            cant_clean = re.sub(r'[^\d.,]', '', str(p.get("cantidad", 0)))
            cantidad = float(cant_clean.replace(",", ".")) if cant_clean else 0.0
        except Exception:
            cantidad = 0.0

        try:
            pu_clean = re.sub(r'[^\d.,]', '', str(p.get("precio_unitario", 0)))
            precio_u = float(pu_clean.replace(",", ".")) if pu_clean else 0.0
        except Exception:
            precio_u = 0.0

        try:
            pt_clean = re.sub(r'[^\d.,]', '', str(p.get("precio_total", 0)))
            precio_t = float(pt_clean.replace(",", ".")) if pt_clean else 0.0
        except Exception:
            precio_t = 0.0

        if precio_u == 0 and precio_t > 0 and cantidad > 0:
            precio_u = precio_t / cantidad

        venc = str(p.get("fecha_vencimiento", "") or "").strip()
        if venc and not re.match(r'^\d{4}-\d{2}-\d{2}$', venc):
            venc = ""

        productos.append({
            "nombre": nombre,
            "cantidad": round(cantidad, 2),
            "unidad": unidad,
            "precio_unitario": round(precio_u, 2),
            "precio_total": round(precio_t, 2),
            "categoria": categoria,
            "fecha_vencimiento": venc,
        })

    return {
        "exitoso": True,
        "proveedor": str(data.get("proveedor", "") or ""),
        "numero_factura": str(data.get("numero_factura", "") or ""),
        "fecha": str(data.get("fecha", "") or ""),
        "productos": productos,
        "total_productos": len(productos),
    }


def analizar_factura_con_ia(archivo_path):
    """
    Analiza una factura (PDF, JPG, PNG) enviándola directamente a Gemini Vision.
    Soporta PDF de forma nativa sin requerir poppler, pdf2image ni OCR externo.
    """
    api_key = _get_gemini_api_key()
    if not api_key:
        return {"exitoso": False, "error": "No hay GEMINI_API_KEY configurada en .env o settings"}

    ext = os.path.splitext(archivo_path)[1].lower()

    if ext == ".pdf":
        try:
            with open(archivo_path, "rb") as f:
                pdf_bytes = f.read()
            imagenes_b64 = [base64.b64encode(pdf_bytes).decode("utf-8")]
            mime_type = "application/pdf"
        except Exception as e:
            return {"exitoso": False, "error": f"Error leyendo archivo PDF: {str(e)}"}
    elif ext in (".jpg", ".jpeg"):
        try:
            imagenes_b64 = [_imagen_a_base64(archivo_path)]
            mime_type = "image/jpeg"
        except Exception as e:
            return {"exitoso": False, "error": f"Error leyendo imagen: {str(e)}"}
    elif ext == ".png":
        try:
            imagenes_b64 = [_imagen_a_base64(archivo_path)]
            mime_type = "image/png"
        except Exception as e:
            return {"exitoso": False, "error": f"Error leyendo imagen: {str(e)}"}
    else:
        return {"exitoso": False, "error": f"Formato no soportado: {ext}. Solo PDF, JPG o PNG."}

    if not imagenes_b64:
        return {"exitoso": False, "error": "El archivo está vacío o no se pudo leer."}

    return _llamar_gemini_rest(api_key, imagenes_b64, mime_type)
