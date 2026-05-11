"""
evaluator.py
Evalúa cada propuesta contra los criterios del RFP usando OpenAI.
Produce un JSON estructurado para scoring confiable.
"""

import json
import re
from openai import OpenAI
from dotenv import load_dotenv
import os
from pathlib import Path

# Cargar .env con ruta absoluta para compatibilidad con Streamlit
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=_api_key)
MODEL = "gpt-4o-mini"


# ─────────────────────────────────────────────────────────────
# PROMPTS
# ─────────────────────────────────────────────────────────────

EVALUATE_HABILITANTE_PROMPT = """Eres un evaluador experto en procesos de contratación pública y privada.

Tu tarea es verificar si la propuesta del proveedor cumple cada criterio habilitante (requisitos de admisibilidad).

REGLAS DE EVALUACIÓN:
- "cumple": SOLO true si hay evidencia EXPLÍCITA y VERIFICABLE en el documento
- Si el documento no menciona el requisito: false
- Si el documento menciona el requisito parcialmente pero no lo acredita: false
- Si hay ambigüedad o duda: false (principio de prudencia)
- "habilitado" = true ÚNICAMENTE si TODOS los criterios cumplen = true
- Cita la evidencia exacta y la página/sección donde se encontró

Retorna ÚNICAMENTE JSON válido:

{
  "proveedor": "string",
  "habilitado": true,
  "criterios_habilitantes": [
    {
      "id": "H1",
      "nombre": "string",
      "cumple": true,
      "evidencia": "Cita textual o descripción exacta de donde se acredita el requisito",
      "documento_fuente": "nombre del archivo o sección",
      "observaciones": "Por qué cumple o no cumple, con criterio técnico"
    }
  ],
  "resumen_habilitacion": "Párrafo de 2-3 líneas explicando el resultado global de habilitación"
}

CRITERIOS A EVALUAR:
{criterios_habilitantes}

DOCUMENTOS DE LA PROPUESTA:
{proposal_text}
"""


EVALUATE_CALIFICACION_PROMPT = """Eres un evaluador técnico especializado en contratación y licitaciones.

Tu tarea es calificar la propuesta según los criterios de calificación del RFP.

REGLAS DE CALIFICACIÓN:
- Evalúa con criterio técnico objetivo, no sigas ciegamente los valores del documento
- Para criterios NUMÉRICOS (años de experiencia, cantidad de proyectos, capacidad financiera, etc.):
  * Extrae el valor numérico real del documento
  * Si el valor parece inflado o sin soporte, usa null y explica en observaciones
  * No asumas valores no declarados explícitamente
- Para criterios BOOLEANOS (certificaciones, requisitos si/no):
  * cumple_condicion = true SOLO si el documento acredita el requisito de forma clara
  * Una mención sin acreditación = false
- Para criterios de PRECIO:
  * Extrae el valor total final SIN IVA en número entero
  * Si hay rangos, usa el valor total más probable
- "evidencia": cita la sección/párrafo donde encontraste el dato
- "descripcion_calificacion": explica brevemente POR QUÉ asignaste ese valor (2-3 líneas)
- NO inventes datos que no estén en el documento
- Si hay datos contradictorios, usa null y explica

Retorna SOLO JSON:

{
  "proveedor": "string",
  "criterios_calificacion": [
    {
      "id": "C1",
      "nombre": "string",
      "puntaje_maximo": number,
      "tipo_dato": "numero | booleano",
      "valor_numerico": number | null,
      "cumple_condicion": true | false | null,
      "evidencia": "Cita o referencia exacta del documento",
      "descripcion_calificacion": "Explicación técnica de por qué este valor/calificación",
      "observaciones": "Notas adicionales, inconsistencias o dudas encontradas"
    }
  ],
  "propuesta_economica_detalle": {
    "valor_total_sin_iva": number | null,
    "moneda": "string",
    "notas_economicas": "Condiciones especiales de precio, descuentos, etc."
  },
  "comentario_general": "Párrafo de 3-4 líneas con una evaluación global de la propuesta: fortalezas, debilidades y aspectos a considerar para la toma de decisión"
}

CRITERIOS DE CALIFICACIÓN:
{criterios_calificacion}

CONTEXTO ECONÓMICO DEL RFP:
{propuesta_economica_rfp}

DOCUMENTOS DE LA PROPUESTA:
{proposal_text}
"""


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def evaluate_proposal(provider_name: str, proposal_text: str, rfp_data: dict) -> dict:
    print(f"-> Evaluando: {provider_name}")
    habilitacion = _eval_habilitantes(provider_name, proposal_text, rfp_data)
    calificacion = _eval_calificacion(provider_name, proposal_text, rfp_data)
    return {
        "provider": provider_name,
        "habilitacion": habilitacion,
        "calificacion": calificacion,
    }


# ─────────────────────────────────────────────────────────────
# EVALUACIONES
# ─────────────────────────────────────────────────────────────

def _eval_habilitantes(provider_name, proposal_text, rfp_data):
    criterios = json.dumps(rfp_data.get("criterios_habilitantes", []), ensure_ascii=False, indent=2)
    prompt = (EVALUATE_HABILITANTE_PROMPT
              .replace("{criterios_habilitantes}", criterios)
              .replace("{proposal_text}", proposal_text[:40000]))
    raw = _call_openai(prompt)
    parsed = _parse_json_response(raw, provider_name)
    return _normalize_habilitacion(parsed, provider_name)


def _eval_calificacion(provider_name, proposal_text, rfp_data):
    criterios = json.dumps(rfp_data.get("criterios_calificacion", []), ensure_ascii=False, indent=2)
    propuesta = json.dumps(rfp_data.get("propuesta_economica", {}), ensure_ascii=False, indent=2)
    prompt = (EVALUATE_CALIFICACION_PROMPT
              .replace("{criterios_calificacion}", criterios)
              .replace("{propuesta_economica_rfp}", propuesta)
              .replace("{proposal_text}", proposal_text[:40000]))
    raw = _call_openai(prompt)
    parsed = _parse_json_response(raw, provider_name)
    return _normalize_calificacion(parsed)


# ─────────────────────────────────────────────────────────────
# OPENAI CALL
# ─────────────────────────────────────────────────────────────

def _call_openai(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=4096,
    )
    return response.choices[0].message.content


# ─────────────────────────────────────────────────────────────
# NORMALIZADORES
# ─────────────────────────────────────────────────────────────

def _normalize_habilitacion(data: dict, provider: str) -> dict:
    if not isinstance(data, dict):
        return {"proveedor": provider, "error": "invalid_json"}
    for c in data.get("criterios_habilitantes", []):
        c["cumple"] = bool(c.get("cumple", False))
    data["habilitado"] = all(c["cumple"] for c in data.get("criterios_habilitantes", []))
    return data


def _normalize_calificacion(data: dict) -> dict:
    if not isinstance(data, dict):
        return {"error": "invalid_json"}
    for c in data.get("criterios_calificacion", []):
        c["valor_numerico"] = _safe_number(c.get("valor_numerico"))
        val = c.get("cumple_condicion")
        if isinstance(val, str):
            c["cumple_condicion"] = val.lower() == "true"
        elif val is None:
            c["cumple_condicion"] = None
        else:
            c["cumple_condicion"] = bool(val)
    econ = data.get("propuesta_economica_detalle", {})
    econ["valor_total_sin_iva"] = _safe_number(econ.get("valor_total_sin_iva"))
    return data


def _safe_number(value):
    if value is None: return None
    if isinstance(value, (int, float)): return float(value)
    if isinstance(value, str):
        value = value.replace(",","").replace("$","").strip()
        try: return float(value)
        except: return None
    return None


# ─────────────────────────────────────────────────────────────
# JSON PARSER
# ─────────────────────────────────────────────────────────────

def _parse_json_response(raw: str, provider_name: str) -> dict:
    raw = raw.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    try:
        return json.loads(raw)
    except Exception as e:
        print(f"[ERROR] JSON invalido ({provider_name}): {e}")
        return {"proveedor": provider_name, "error": str(e), "raw": raw[:500]}