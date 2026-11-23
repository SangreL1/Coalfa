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
import time
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

CATEGORIAS_VALIDAS = [
    "ABARROTES", "CARNES", "PESCADOS", "LACTEOS",
    "FRUTAS", "CONGELADOS", "BEBIDAS", "LIMPIEZA",
    "VESTUARIO", "EPP", "OTRO",
]
UNIDADES_VALIDAS = ["KG", "G", "L", "ML", "UN", "CAJA"]

# Modelos ordenados por disponibilidad y resiliencia ante alta demanda
MODELOS_GEMINI = [
    "gemini-flash-lite-latest",
    "gemini-3.5-flash-lite",
    "gemini-3-flash-preview",
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


def _llamar_gemini_rest(api_key, imagenes_b64, mime_type, prompt, parser_func=None):
    if parser_func is None:
        parser_func = _parsear_respuesta_gemini

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
            "maxOutputTokens": 8192,
        }
    }).encode("utf-8")

    ultimo_error = None
    es_alta_demanda = False

    for modelo in MODELOS_GEMINI:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        # Hasta 2 intentos por modelo si hay saturación temporal (503 / 429)
        for intento in range(2):
            try:
                with urllib.request.urlopen(req, timeout=40) as resp:
                    data = json.loads(resp.read().decode("utf-8"))

                # Concatenar TODOS los fragmentos de texto (no solo parts[0])
                candidate = data.get("candidates", [{}])[0]
                content = candidate.get("content", {})
                parts_list = content.get("parts", [])
                raw_text = "".join(p.get("text", "") for p in parts_list if "text" in p).strip()

                if not raw_text:
                    logger.warning(f"Gemini {modelo} devolvió contenido vacío en partes")
                    continue

                logger.info(f"Análisis completado exitosamente con modelo {modelo} (intento {intento + 1}, len={len(raw_text)})")
                return parser_func(raw_text)
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8")
                logger.warning(f"Gemini {modelo} (intento {intento + 1}) HTTP {e.code}: {body[:150]}")
                ultimo_error = f"HTTP {e.code} en {modelo}"
                if e.code in (503, 429):
                    es_alta_demanda = True
                    time.sleep(1.2)  # Pausa breve antes de reintentar
                    continue
                break  # Otros códigos (400, 404) no se solucionan reintentando el mismo modelo
            except Exception as e:
                logger.warning(f"Gemini {modelo} error: {e}")
                ultimo_error = f"{modelo}: {str(e)}"
                break

    if es_alta_demanda:
        return {
            "exitoso": False,
            "error": "Google Gemini está experimentando alta demanda momentánea en sus servidores (HTTP 503). Por favor espera 5 segundos y vuelve a intentar."
        }

    return {"exitoso": False, "error": f"No se pudo contactar a Gemini ({ultimo_error})" }


def _extraer_o_reparar_json(raw_text):
    """Extrae el objeto JSON de la respuesta de Gemini de forma ultra tolerante ante truncamiento o markdown."""
    if not raw_text:
        return None

    # Quitar posibles fences ```json ... ```
    texto = re.sub(r'^```(?:json)?\s*', '', raw_text.strip(), flags=re.IGNORECASE)
    texto = re.sub(r'\s*```$', '', texto).strip()

    # Intento 1: json.loads directo
    try:
        return json.loads(texto)
    except Exception:
        pass

    # Intento 2: Buscar entre la primera '{' y la última '}'
    start = texto.find('{')
    end = texto.rfind('}')
    if start != -1 and end > start:
        try:
            return json.loads(texto[start:end + 1])
        except Exception:
            pass

    # Intento 3: Si falta la llave final '}' por corte de longitud, intentar cerrarla
    if start != -1:
        fragmento = texto[start:].strip()
        for suffix in ['}', ']}', '"}]}', '"]}', '}]}']:
            try:
                return json.loads(fragmento + suffix)
            except Exception:
                continue

    # Intento 4: Extraer objetos de productos por Regex si el JSON general quedó roto
    productos = []
    patron = r'\{\s*"nombre"\s*:\s*"([^"]+)"[^}]*\}'
    for match in re.finditer(patron, texto):
        try:
            p_obj = json.loads(match.group(0))
            productos.append(p_obj)
        except Exception:
            continue

    if productos:
        prov_m = re.search(r'"proveedor"\s*:\s*"([^"]+)"', texto)
        num_m = re.search(r'"numero_factura"\s*:\s*"([^"]+)"', texto)
        return {
            "proveedor": prov_m.group(1) if prov_m else "",
            "numero_factura": num_m.group(1) if num_m else "",
            "productos": productos,
        }

    return None


def _parsear_respuesta_gemini(raw_text):
    data = _extraer_o_reparar_json(raw_text)
    if not data or not isinstance(data, dict):
        return {"exitoso": False, "error": f"Respuesta no reconocida de Gemini: {raw_text[:200]}"}

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


def _construir_prompt_solicitud(productos_disponibles, areas_disponibles):
    prompt = """Eres un asistente de bodega y control de insumos de casinos de alimentación institucional en Chile (COALFA).
Tu tarea es leer una SOLICITUD DE INSUMOS ESCRITA A MANO EN PAPEL (comanda, libreta o vale de insumos) y cruzarla contra el inventario real que TIENE STOCK disponible en la bodega.

DESAFÍO DE LECTURA DE MANUSCRITOS Y JERGA DE COCINA CHILENA:
- La letra puede ser manuscrita, apresurada, con trazos difíciles o abreviaturas clásicas de cocina en Chile:
  * "k", "kg", "kilos", "kl" -> Kilogramos (KG)
  * "u", "un", "und", "unid" -> Unidades (UN)
  * "bot", "btll", "bt" -> Botellas (UN)
  * "cja", "caja" -> Cajas
  * "pqte", "paq", "bolsa" -> Paquete / Bolsa (UN)
  * "posta", "lomo", "choclillo", "carne", "vacuno" -> Carne vacuno
  * "pechuga", "trutro", "ala", "pollo" -> Pollo
  * "ceb", "cebolla" -> Cebolla
  * "zan", "zanahoria" -> Zanahoria
  * "tom", "tomate" -> Tomate
  * "aceit" -> Aceite
  * "lech", "lact" -> Leche
  * "mayo" -> Mayonesa
- Detecta si en el papel se indica el ÁREA o DESTINO que pide las cosas (ej: "Cocina caliente", "Casino", "Repostería", "Línea", "Cuarto frío", "Desayuno", etc.).

ÁREAS DE DESTINO REGISTRADAS EN EL SISTEMA:
"""
    for key, label in areas_disponibles:
        prompt += f'- Clave: "{key}" (Área: {label})\n'

    prompt += """
CATÁLOGO DE PRODUCTOS EN BODEGA CON STOCK DISPONIBLE (Usa EXCLUSIVAMENTE estos IDs y Nombres):
"""
    for p in productos_disponibles:
        prompt += f"- ID: {p.get('id')} | Nombre: \"{p.get('nombre')}\" | Stock: {p.get('stock')} {p.get('unidad')}\n"

    prompt += """
REGLAS ESTRICTAS DE COINCIDENCIA:
1. Solo agrega a "items" aquellos productos del papel que correspondan claramente a un producto del catálogo con stock disponible.
2. Si un insumo del papel está en el catálogo, usa su ID numérico exacto y su nombre oficial.
3. Si la unidad en el catálogo es 'UN' y piden 'huevos' en bandejas (ej: 2 bandejas = 60 huevos), convierte la cantidad a la unidad del catálogo.
4. Si un insumo escrito en el papel NO está en el catálogo o no tiene stock disponible, NO inventes IDs ni agregues productos que no coincidan. Agrégalo a "no_encontrados" con el texto leído tal cual y el motivo.
5. Si el papel especifica o da a entender el área solicitante, asígnala en "area_sugerida" con su Clave exacta. Si no se puede determinar, deja "area_sugerida": "".

Responde ÚNICAMENTE con un JSON válido con esta estructura exacta (sin texto previo ni posterior):
{
  "area_sugerida": "CLAVE_DEL_AREA",
  "items": [
    {
      "id": 1,
      "nombre": "Nombre exacto del producto en catálogo",
      "cantidad": 10.0,
      "unidad": "KG"
    }
  ],
  "no_encontrados": [
    {
      "texto_leido": "harina de fuerza 5k",
      "motivo": "No existe en el catálogo con stock disponible"
    }
  ]
}
"""
    return prompt


def _parsear_respuesta_solicitud(raw_text):
    data = _extraer_o_reparar_json(raw_text)
    if not data or not isinstance(data, dict):
        return {"exitoso": False, "error": f"Respuesta no reconocida de Gemini: {raw_text[:200]}"}

    area_sugerida = str(data.get("area_sugerida", "") or "").strip()
    items = []
    for item in data.get("items", []):
        try:
            prod_id = int(item.get("id"))
            nombre = str(item.get("nombre", "")).strip()
            cant_clean = re.sub(r'[^\d.,]', '', str(item.get("cantidad", 0)))
            cantidad = float(cant_clean.replace(",", ".")) if cant_clean else 0.0
            unidad = str(item.get("unidad", "")).strip()
            if prod_id and cantidad > 0:
                items.append({
                    "id": prod_id,
                    "nombre": nombre,
                    "cantidad": round(cantidad, 2),
                    "unidad": unidad,
                })
        except Exception:
            continue

    no_encontrados = []
    for ne in data.get("no_encontrados", []):
        if isinstance(ne, dict):
            texto = str(ne.get("texto_leido", "")).strip()
            motivo = str(ne.get("motivo", "")).strip()
            if texto:
                no_encontrados.append({"texto_leido": texto, "motivo": motivo or "No disponible en bodega"})
        elif isinstance(ne, str) and ne.strip():
            no_encontrados.append({"texto_leido": ne.strip(), "motivo": "No disponible en bodega"})

    return {
        "exitoso": True,
        "area_sugerida": area_sugerida,
        "items": items,
        "no_encontrados": no_encontrados,
        "total_items": len(items),
    }


def analizar_solicitud_papel_ia(archivo_path, productos_disponibles, areas_disponibles):
    """
    Analiza una foto o escaneo de una comanda o solicitud de insumos en papel manuscrita.
    Cruza la lectura con los productos que realmente tienen stock en bodega y detecta el área de destino.
    """
    api_key = _get_gemini_api_key()
    if not api_key:
        return {"exitoso": False, "error": "No hay GEMINI_API_KEY configurada en el servidor."}

    ext = os.path.splitext(archivo_path)[1].lower()

    if ext == ".pdf":
        try:
            with open(archivo_path, "rb") as f:
                pdf_bytes = f.read()
            imagenes_b64 = [base64.b64encode(pdf_bytes).decode("utf-8")]
            mime_type = "application/pdf"
        except Exception as e:
            return {"exitoso": False, "error": f"Error leyendo PDF: {str(e)}"}
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
    elif ext == ".webp":
        try:
            imagenes_b64 = [_imagen_a_base64(archivo_path)]
            mime_type = "image/webp"
        except Exception as e:
            return {"exitoso": False, "error": f"Error leyendo imagen: {str(e)}"}
    else:
        return {"exitoso": False, "error": f"Formato no soportado: {ext}. Usa fotos JPG, PNG o PDF."}

    if not imagenes_b64:
        return {"exitoso": False, "error": "El archivo de imagen está vacío o dañado."}

    prompt = _construir_prompt_solicitud(productos_disponibles, areas_disponibles)
    return _llamar_gemini_rest(api_key, imagenes_b64, mime_type, prompt=prompt, parser_func=_parsear_respuesta_solicitud)
