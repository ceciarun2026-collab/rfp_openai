"""
evaluator.py
Evalúa cada propuesta contra los criterios del RFP usando OpenAI.
Produce un JSON de cumplimiento por criterio para cada proveedor.
"""

import json
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()
MODEL = "gpt-4o-mini"


EVALUATE_HABILITANTE_PROMPT = """Eres un evaluador experto en procesos de contratación pública y privada.

Se te proporcionan:
1. Los criterios HABILITANTES de un proceso de contratación
2. La documentación completa presentada por un proveedor

Tu tarea es determinar si el proveedor CUMPLE o NO CUMPLE cada criterio habilitante,
basándote ÚNICAMENTE en la evidencia presente en los documentos del proveedor.

Retorna un JSON con el siguiente esquema EXACTO:

{
  "proveedor": "nombre del proveedor",
  "habilitado": true,
  "criterios_habilitantes": [
    {
      "id": "H1",
      "nombre": "nombre del criterio",
      "cumple": true,
      "evidencia": "texto o descripción exacta del documento que acredita el cumplimiento",
      "documento_fuente": "nombre del archivo o sección donde se encontró la evidencia",
      "observaciones": "notas adicionales o razón de incumplimiento si aplica"
    }
  ],
  "resumen_habilitacion": "texto breve explicando si el proveedor está habilitado y por qué"
}

REGLAS ESTRICTAS:
- "cumple" es true SOLO si hay evidencia CLARA Y EXPLÍCITA en los documentos
- Si hay duda, marca cumple: false con observaciones explicando qué falta
- "habilitado" es true SOLO si TODOS los criterios habilitantes tienen cumple: true
- Sé específico en "evidencia": cita datos concretos (fechas, valores, nombres)
- No inferir ni asumir información que no está en los documentos
- Responde ÚNICAMENTE con el JSON, sin texto adicional, sin markdown

CRITERIOS HABILITANTES DEL RFP:
{criterios_habilitantes}

DOCUMENTOS DEL PROVEEDOR:
{proposal_text}
"""


EVALUATE_CALIFICACION_PROMPT = """Eres un evaluador experto en procesos de contratación.

Se te proporcionan:
1. Los criterios de CALIFICACIÓN con sus puntajes máximos
2. La propuesta económica y documentos del proveedor

Tu tarea es extraer la información relevante de cada criterio de calificación
para poder asignar puntajes posteriormente.

Retorna un JSON con el siguiente esquema EXACTO:

{
  "proveedor": "nombre del proveedor",
  "criterios_calificacion": [
    {
      "id": "C1",
      "nombre": "nombre del criterio",
      "puntaje_maximo": 0,
      "valor_extraido": "valor numérico o dato extraído de la propuesta (precio, porcentaje, etc.)",
      "cumple_condicion": true,
      "evidencia": "texto exacto de la propuesta que soporta el valor extraído",
      "observaciones": "notas relevantes"
    }
  ],
  "propuesta_economica_detalle": {
    "valor_total_sin_iva": 0,
    "items": [
      {
        "descripcion": "descripción del ítem",
        "cantidad": "cantidad",
        "valor_unitario": 0,
        "valor_total": 0
      }
    ],
    "moneda": "COP",
    "notas_economicas": "condiciones especiales mencionadas"
  }
}

REGLAS:
- Para criterio de PRECIO: extrae el valor numérico exacto antes de IVA
- Para criterios booleanos (cumple/no cumple): marca cumple_condicion apropiadamente
- Si no encuentras información para un criterio, valor_extraido = null, cumple_condicion = false
- Responde ÚNICAMENTE con el JSON, sin texto adicional, sin markdown

CRITERIOS DE CALIFICACIÓN:
{criterios_calificacion}

PROPUESTA ECONÓMICA DEL RFP (valores de referencia):
{propuesta_economica_rfp}

DOCUMENTOS DEL PROVEEDOR:
{proposal_text}
"""


def evaluate_proposal(provider_name: str, proposal_text: str, rfp_data: dict) -> dict:
    """
    Evalúa una propuesta completa contra el RFP.
    Retorna dict con evaluación de habilitantes + calificación.
    """
    print(f"  → Evaluando habilitantes: {provider_name}")
    habilitacion = _eval_habilitantes(provider_name, proposal_text, rfp_data)

    print(f"  → Evaluando calificación: {provider_name}")
    calificacion = _eval_calificacion(provider_name, proposal_text, rfp_data)

    return {
        "provider": provider_name,
        "habilitacion": habilitacion,
        "calificacion": calificacion,
    }


def _eval_habilitantes(provider_name: str, proposal_text: str, rfp_data: dict) -> dict:
    """Evalúa criterios habilitantes."""
    criterios = json.dumps(
        rfp_data.get("criterios_habilitantes", []),
        ensure_ascii=False,
        indent=2
    )

    prompt = (EVALUATE_HABILITANTE_PROMPT
              .replace("{criterios_habilitantes}", criterios)
              .replace("{proposal_text}", proposal_text[:40000]))
    prompt = prompt.replace('"nombre del proveedor"', f'"{provider_name}"')

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
        temperature=0,
    )

    return _parse_json_response(response.choices[0].message.content, provider_name)


def _eval_calificacion(provider_name: str, proposal_text: str, rfp_data: dict) -> dict:
    """Evalúa criterios de calificación y extrae datos económicos."""
    criterios = json.dumps(
        rfp_data.get("criterios_calificacion", []),
        ensure_ascii=False,
        indent=2
    )
    propuesta_rfp = json.dumps(
        rfp_data.get("propuesta_economica", {}),
        ensure_ascii=False,
        indent=2
    )

    prompt = (EVALUATE_CALIFICACION_PROMPT
              .replace("{criterios_calificacion}", criterios)
              .replace("{propuesta_economica_rfp}", propuesta_rfp)
              .replace("{proposal_text}", proposal_text[:40000]))
    prompt = prompt.replace('"nombre del proveedor"', f'"{provider_name}"')

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
        temperature=0,
    )

    return _parse_json_response(response.choices[0].message.content, provider_name)


def _parse_json_response(raw: str, provider_name: str) -> dict:
    """Limpia y parsea la respuesta JSON de OpenAI."""
    raw = raw.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  [ERROR] JSON inválido para {provider_name}: {e}")
        return {
            "proveedor": provider_name,
            "error": str(e),
            "raw_response": raw[:500]
        }
