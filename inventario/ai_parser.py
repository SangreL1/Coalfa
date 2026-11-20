"""
ai_parser.py — Análisis inteligente de facturas para casinos y bodegas con Gemini Vision.
Convierte formatos de proveedores (cajas, paquetes, bidones) a unidades operativas reales:
- Huevos: siempre en UNIDADES ('UN') calculando el total de huevos por caja (ej: 180 UN).
- Carnes/Aves/Pescados: siempre en KILOGRAMOS ('KG') con precio por kilo.
- Pastas/Lasañas/Platos preparados: en UNIDADES ('UN') por porción o bandeja.
- Granel/Abarrotes: en 'KG'.
- Soporta instrucciones interactivas del usuario para correcciones inmediatas.
"""
import base64
import json
import logging
import os
import re
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


def _construir_prompt(instrucciones_usuario="", catalogo=None):
    prompt = """Eres un asistente experto en auditoría de facturas y control de existencias de casinos de alimentación institucional en Chile (COALFA).

Tu tarea es analizar el documento adjunto (factura o guía) y extraer TODOS los productos convirtiéndolos a las UNIDADES OPERATIVAS DE BODEGA reales para su consumo en cocina:

REGLAS DE CONVERSIÓN OBLIGATORIAS POR TIPO DE ALIMENTO:

1. HUEVOS:
   - Se controlan SIEMPRE en UNIDADES ('UN'). Nunca registres 'caja' de huevo si puedes saber las unidades.
   - Si la factura indica cajas o bandejas, calcula el TOTAL DE HUEVOS (en Chile una caja estándar trae 180 huevos = 6 bandejas de 30, o 360 si es doble). Si la descripción dice ej: 'Huevo bandeja 30un' o 'Caja huevo 180un', multiplica cantidad de cajas * unidades por caja.
   - Cantidad = Total de huevos (ej: 5 cajas de 180 = 900 UN).
   - Precio unitario = Precio por cada huevo individual (Precio total neto o con IVA / Cantidad de huevos).

2. CARNES, POLLOS, PAVO, CERDO, VACUNO, PESCADOS Y CECINAS:
   - Se controlan SIEMPRE en KILOGRAMOS ('KG').
   - Cantidad = Kilos netos totales despachados (revisa el pesaje o kilos reales indicados).
   - Precio unitario = Valor por KILO ($/KG).

3. PASTAS RELLENAS, LASAÑAS, PIZZAS, EMPANADAS Y PLATOS PREPARADOS CONGELADOS:
   - Se controlan en UNIDADES ('UN') individuales para costeo por porción (ej: por bandeja de lasaña, por unidad de pizza o empanada).
   - Si la factura dice 'Caja Lasaña 12 unidades', Cantidad = 12 UN, y Precio unitario = Precio total / 12.
   - Si es pasta seca tradicional (fideos, espagueti en bolsa), va en 'KG' sumando el peso total.

4. ABARROTES A GRANEL (Arroz, Fideos, Harina, Legumbres, Sal, Azúcar):
   - Se controlan en 'KG'. Multiplica bultos por peso (ej: '4 cajas de 10 bolsas de 1kg' = 40 KG).

5. LÍQUIDOS, BEBIDAS Y ACEITES:
   - Botellas o latas individuales: en 'UN'.
   - Aceite a granel/bidón, vinagre, salsa en balde: en 'L' (litros).

6. CONSISTENCIA MATEMÁTICA:
   - Siempre: Precio Total = Cantidad * Precio Unitario.
   - Si la factura trae precio con IVA, puedes mantener los precios finales.
"""

    if catalogo and len(catalogo) > 0:
        prompt += "\nCATÁLOGO CONOCIDO EN EL SISTEMA (Usa estas unidades preferentes si coinciden):\n"
        for prod in catalogo[:50]:
            prompt += f"- {prod.get('nombre')}: Unidad '{prod.get('unidad_medida')}', Categoría '{prod.get('categoria')}'\n"

    if instrucciones_usuario and instrucciones_usuario.strip():
        prompt += f"\n⚠️ INSTRUCCIONES / CORRECCIONES DEL USUARIO (MÁXIMA PRIORIDAD):\n{instrucciones_usuario.strip()}\n"
        prompt += "Aplica obligatoriamente estas correcciones sobre los productos que correspondan.\n"

    prompt += """
Responde ÚNICAMENTE con un JSON válido con esta estructura exacta (sin texto previo ni posterior):
{
  "proveedor": "Nombre del proveedor o emisor",
  "numero_factura": "Número de factura o guía",
  "fecha": "YYYY-MM-DD",
  "productos": [
    {
      "nombre": "Nombre descriptivo del producto",
      "cantidad": 100.0,
      "unidad": "UN",
      "precio_unitario": 150.0,
      "precio_total": 15000.0,
      "categoria": "LACTEOS",
      "fecha_vencimiento": "YYYY-MM-DD"
    }
  ]
}

- 'unidad' debe ser una de: KG, G, L, ML, UN, CAJA
- 'categoria' debe ser una de: ABARROTES, CARNES, PESCADOS, LACTEOS, FRUTAS, CONGELADOS, BEBIDAS, LIMPIEZA, VESTUARIO, EPP, OTRO
- Si la fecha de vencimiento no aparece, deja "" (cadena vacía)
- Extrae TODOS los productos de la lista
"""
    return prompt


def _get_gemini_api_key():
    from django.conf import settings
    key = getattr(settings, "GEMINI_API_KEY", None) or os.environ.get("GEMINI_API_KEY", "")
    return key.strip()


def _imagen_a_base64(imagen_path):
    with open(imagen_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _llamar_gemini_rest(api_key, imagenes_b64, mime_type, prompt):
    parts = [{"text": prompt}]
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
        "GRAMOS": "G", "GRAMO": "G", "UNIDAD": "UN", "UNIDADES": "UN",
        "BANDEJA": "UN", "CAJAS": "CAJA", "BOTELLA": "UN", "PAQUETE": "UN",
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


def analizar_factura_con_ia(archivo_path, instrucciones="", catalogo=None):
    """
    Punto de entrada: analiza una factura aplicando reglas de conversión gastronómicas,
    catálogo de productos del casino e instrucciones interactivas del usuario.
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

    prompt = _construir_prompt(instrucciones_usuario=instrucciones, catalogo=catalogo)
    return _llamar_gemini_rest(api_key, imagenes_b64, mime_type, prompt=prompt)
