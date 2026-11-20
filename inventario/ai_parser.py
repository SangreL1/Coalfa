"""
ai_parser.py — Análisis de facturas con Gemini Vision API (google-generativeai).
Extrae productos, cantidades, precios y categorías desde PDF o imagen de factura.
"""
import base64
import json
import logging
import os
import re
import tempfile

logger = logging.getLogger(__name__)

# ─── Categorías disponibles en el sistema ────────────────────────────────────
CATEGORIAS_VALIDAS = [
    "ABARROTES", "CARNES", "PESCADOS", "LACTEOS",
    "FRUTAS", "CONGELADOS", "BEBIDAS", "LIMPIEZA",
    "VESTUARIO", "EPP", "OTRO",
]
UNIDADES_VALIDAS = ["KG", "G", "L", "ML", "UN", "CAJA"]

PROMPT_FACTURA = """Eres un asistente experto en análisis de facturas de proveedores de alimentos y suministros para casinos y restaurantes en Chile.

Analiza la imagen/documento y extrae TODOS los productos/ítems con sus datos.

Responde ÚNICAMENTE con un JSON válido con esta estructura exacta (sin texto adicional):
{
  "proveedor": "Nombre del proveedor o empresa emisora",
  "numero_factura": "Número de factura o guía",
  "fecha": "YYYY-MM-DD o vacío si no está",
  "productos": [
    {
      "nombre": "Nombre completo del producto",
      "cantidad": 10.0,
      "unidad": "KG",
      "precio_unitario": 1500.0,
      "precio_total": 15000.0,
      "categoria": "ABARROTES",
      "fecha_vencimiento": "YYYY-MM-DD o vacío"
    }
  ]
}

Reglas importantes:
- "unidad" debe ser uno de: KG, G, L, ML, UN, CAJA
- "categoria" debe ser uno de: ABARROTES, CARNES, PESCADOS, LACTEOS, FRUTAS, CONGELADOS, BEBIDAS, LIMPIEZA, VESTUARIO, EPP, OTRO
- "precio_unitario" es el precio por unidad (sin IVA si aparece diferenciado)
- Si el precio está "con IVA", inclúyelo tal cual aparece en la factura
- Si no puedes determinar fecha_vencimiento, deja vacío ""
- Incluye TODOS los productos aunque falten algunos datos
- No inventes datos, usa 0 si no encuentras el valor numérico
- Para cantidades tipo "7 cajas de 2 bolsas de 5kg" → cantidad=70 y unidad="KG"
"""


def _get_gemini_api_key():
    """Obtiene la API key de Gemini desde settings o variable de entorno."""
    from django.conf import settings
    key = getattr(settings, "GEMINI_API_KEY", None) or os.environ.get("GEMINI_API_KEY", "")
    return key.strip()


def _pdf_a_imagen_base64(pdf_path):
    """Convierte primera(s) página(s) del PDF a base64 para enviar a Gemini."""
    imagenes_b64 = []
    try:
        # Intentar con pdf2image
        from pdf2image import convert_from_path
        import sys
        kwargs = {"dpi": 150, "first_page": 1, "last_page": 3}
        if sys.platform.startswith("win"):
            # Ruta poppler en Windows local
            poppler_win = r"C:\Users\Coalfa\AppData\Local\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-25.07.0\Library\bin"
            if os.path.exists(poppler_win):
                kwargs["poppler_path"] = poppler_win
        images = convert_from_path(pdf_path, **kwargs)
        for img in images:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                img.save(tmp.name, "JPEG", quality=85)
                with open(tmp.name, "rb") as f:
                    imagenes_b64.append(base64.b64encode(f.read()).decode("utf-8"))
                os.unlink(tmp.name)
    except Exception as e:
        logger.warning(f"pdf2image falló: {e}. Intentando con PyMuPDF...")
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            for page_num in range(min(3, len(doc))):
                page = doc[page_num]
                mat = fitz.Matrix(2, 2)  # 2x zoom = ~144 DPI
                pix = page.get_pixmap(matrix=mat)
                img_bytes = pix.tobytes("jpeg")
                imagenes_b64.append(base64.b64encode(img_bytes).decode("utf-8"))
            doc.close()
        except Exception as e2:
            logger.error(f"PyMuPDF también falló: {e2}")
    return imagenes_b64


def _imagen_a_base64(imagen_path):
    """Convierte una imagen directamente a base64."""
    with open(imagen_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def analizar_factura_con_ia(archivo_path):
    """
    Función principal. Recibe la ruta a un PDF o imagen de factura.
    Devuelve dict con:
      {
        "exitoso": True/False,
        "proveedor": str,
        "numero_factura": str,
        "fecha": str,
        "productos": [ {"nombre", "cantidad", "unidad", "precio_unitario", "precio_total", "categoria", "fecha_vencimiento"}, ... ],
        "error": str (solo si exitoso=False)
      }
    """
    api_key = _get_gemini_api_key()
    if not api_key:
        return {"exitoso": False, "error": "No hay GEMINI_API_KEY configurada en settings.py"}

    ext = os.path.splitext(archivo_path)[1].lower()

    # ── Preparar imágenes base64 ──────────────────────────────────────────────
    if ext == ".pdf":
        imagenes_b64 = _pdf_a_imagen_base64(archivo_path)
        mime_type = "image/jpeg"
    elif ext in (".jpg", ".jpeg"):
        imagenes_b64 = [_imagen_a_base64(archivo_path)]
        mime_type = "image/jpeg"
    elif ext == ".png":
        imagenes_b64 = [_imagen_a_base64(archivo_path)]
        mime_type = "image/png"
    else:
        return {"exitoso": False, "error": f"Formato no soportado: {ext}"}

    if not imagenes_b64:
        return {"exitoso": False, "error": "No se pudo convertir el archivo a imagen para análisis."}

    # ── Llamar a Gemini Vision API ────────────────────────────────────────────
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Construir contenido multimodal (texto + imágenes)
        content_parts = [PROMPT_FACTURA]
        for b64 in imagenes_b64:
            content_parts.append({
                "mime_type": mime_type,
                "data": b64,
            })

        response = model.generate_content(content_parts)
        raw_text = response.text.strip()

    except ImportError:
        return _llamar_gemini_rest(api_key, imagenes_b64, mime_type)
    except Exception as e:
        logger.error(f"Error llamando a Gemini: {e}")
        return {"exitoso": False, "error": f"Error de API: {str(e)}"}

    return _parsear_respuesta_gemini(raw_text)


def _llamar_gemini_rest(api_key, imagenes_b64, mime_type):
    """Fallback: llama a Gemini mediante REST (urllib) sin librería google-generativeai."""
    import urllib.request
    import urllib.error

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

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

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        return _parsear_respuesta_gemini(raw_text)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        logger.error(f"Gemini REST HTTP {e.code}: {body}")
        return {"exitoso": False, "error": f"HTTP {e.code}: {body[:200]}"}
    except Exception as e:
        logger.error(f"Gemini REST error: {e}")
        return {"exitoso": False, "error": str(e)}


def _parsear_respuesta_gemini(raw_text):
    """Parsea el JSON devuelto por Gemini y lo valida/normaliza."""
    # Extraer JSON limpio (Gemini a veces lo envuelve en ```json ... ```)
    match = re.search(r'\{[\s\S]*\}', raw_text)
    if not match:
        return {"exitoso": False, "error": f"Gemini no devolvió JSON válido. Respuesta: {raw_text[:300]}"}

    try:
        data = json.loads(match.group())
    except json.JSONDecodeError as e:
        return {"exitoso": False, "error": f"JSON inválido de Gemini: {e}. Raw: {raw_text[:300]}"}

    productos_raw = data.get("productos", [])
    productos = []
    for p in productos_raw:
        nombre = str(p.get("nombre", "")).strip()
        if not nombre:
            continue

        unidad = str(p.get("unidad", "UN")).upper().strip()
        if unidad not in UNIDADES_VALIDAS:
            # Intentar mapear unidades comunes
            mapeo = {"KILOGRAMO": "KG", "KILOS": "KG", "KILO": "KG",
                     "LITRO": "L", "LITROS": "L", "MILILITROS": "ML",
                     "GRAMOS": "G", "GRAMO": "G", "UNIDAD": "UN",
                     "CAJAS": "CAJA", "BOT": "UN", "BOTELLA": "UN"}
            unidad = mapeo.get(unidad, "UN")

        categoria = str(p.get("categoria", "OTRO")).upper().strip()
        if categoria not in CATEGORIAS_VALIDAS:
            categoria = "OTRO"

        try:
            cantidad = float(str(p.get("cantidad", 0)).replace(",", ".") or 0)
        except (ValueError, TypeError):
            cantidad = 0.0

        try:
            precio_u = float(str(p.get("precio_unitario", 0)).replace(",", ".").replace("$", "").replace(".", "").replace(",", ".") or 0)
        except (ValueError, TypeError):
            # Intentar limpiar más agresivamente
            try:
                raw_p = re.sub(r'[^\d.,]', '', str(p.get("precio_unitario", 0)))
                precio_u = float(raw_p.replace(",", ".")) if raw_p else 0.0
            except Exception:
                precio_u = 0.0

        try:
            precio_t = float(str(p.get("precio_total", 0)).replace(",", ".").replace("$", "").replace(".", "").replace(",", ".") or 0)
        except (ValueError, TypeError):
            precio_t = precio_u * cantidad if precio_u and cantidad else 0.0

        # Si precio_unitario es 0 pero tenemos total y cantidad, calcularlo
        if precio_u == 0 and precio_t > 0 and cantidad > 0:
            precio_u = precio_t / cantidad

        productos.append({
            "nombre": nombre,
            "cantidad": cantidad,
            "unidad": unidad,
            "precio_unitario": round(precio_u, 2),
            "precio_total": round(precio_t, 2),
            "categoria": categoria,
            "fecha_vencimiento": str(p.get("fecha_vencimiento", "") or ""),
        })

    return {
        "exitoso": True,
        "proveedor": str(data.get("proveedor", "") or ""),
        "numero_factura": str(data.get("numero_factura", "") or ""),
        "fecha": str(data.get("fecha", "") or ""),
        "productos": productos,
        "total_productos": len(productos),
    }
