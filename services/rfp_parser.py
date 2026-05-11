"""
rfp_parser.py
Analiza el texto del RFP con OpenAI y extrae:
  - Criterios habilitantes (requisitos de habilitación)
  - Criterios de calificación (con puntajes)
  - Datos generales del proceso
Salida: JSON estructurado y limpio.
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


PARSE_RFP_PROMPT = """Eres un experto en análisis de procesos de contratación y licitaciones.

Se te proporciona el texto completo de un RFP (Request for Proposal) o Invitación a Cotizar.

Tu tarea es extraer y estructurar toda la información relevante en un JSON con el siguiente esquema EXACTO:

{
  "proceso": {
    "titulo": "título o nombre del proceso de contratación",
    "entidad_contratante": "nombre de la entidad que contrata",
    "objeto": "descripción del objeto del contrato",
    "alcance": "descripción del alcance",
    "plazo_ejecucion": "duración del contrato",
    "forma_pago": "condiciones de pago",
    "fecha_cierre": "fecha límite para presentar propuestas"
  },
  "criterios_habilitantes": [
    {
      "id": "H1",
      "nombre": "nombre del criterio",
      "descripcion": "descripción completa del requisito",
      "tipo": "documental | financiero | tecnico | juridico",
      "es_obligatorio": true,
      "valor_minimo": "valor mínimo requerido si aplica, null si no",
      "documentos_requeridos": ["lista de documentos que debe presentar el proveedor"]
    }
  ],
  "criterios_calificacion": [
    {
      "id": "C1",
      "nombre": "nombre del criterio",
      "descripcion": "descripción completa",
      "puntaje_maximo": 0,
      "formula": "fórmula de cálculo si se especifica, null si no",
      "notas": "observaciones adicionales"
    }
  ],
  "propuesta_economica": {
    "items": [
      {
        "descripcion": "descripción del ítem",
        "cantidad": "cantidad o unidad",
        "valor_referencia": "valor de referencia si aplica, null si no"
      }
    ],
    "moneda": "COP | USD | EUR",
    "incluye_iva": false,
    "notas": "condiciones especiales sobre el precio"
  },
  "puntaje_total": 0
}

REGLAS:
- Extrae TODA la información disponible, no omitas criterios
- Si un campo no está en el documento, usa null
- Los puntajes deben ser números, no strings
- Sé preciso con las descripciones, son la base para evaluar propuestas
- Para criterios habilitantes, incluye todos los documentos que el proveedor debe presentar
- Responde ÚNICAMENTE con el JSON, sin texto adicional, sin markdown

TEXTO DEL RFP:
{rfp_text}
"""


def parse_rfp(rfp_text: str) -> dict:
    """
    Envía el texto del RFP a OpenAI y retorna el JSON estructurado con los criterios.
    """
    prompt = PARSE_RFP_PROMPT.replace("{rfp_text}", rfp_text[:50000])

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"OpenAI no retornó JSON válido: {e}\nRespuesta: {raw[:500]}")

    # Calcular puntaje total si no está en el JSON
    if not result.get("puntaje_total"):
        total = sum(
            c.get("puntaje_maximo", 0) or 0
            for c in result.get("criterios_calificacion", [])
        )
        result["puntaje_total"] = total

    return result


def summarize_criteria(rfp_data: dict) -> str:
    """
    Retorna un resumen legible de los criterios extraídos.
    Útil para logs y debugging.
    """
    lines = []
    proceso = rfp_data.get("proceso", {})
    lines.append(f"PROCESO: {proceso.get('titulo', 'N/D')}")
    lines.append(f"ENTIDAD: {proceso.get('entidad_contratante', 'N/D')}")
    objeto = proceso.get('objeto', 'N/D') or 'N/D'
    lines.append(f"OBJETO: {objeto[:100]}...")
    lines.append("")

    habilitantes = rfp_data.get("criterios_habilitantes", [])
    lines.append(f"CRITERIOS HABILITANTES ({len(habilitantes)}):")
    for c in habilitantes:
        lines.append(f"  [{c['id']}] {c['nombre']} — {c['tipo'].upper()}")
        if c.get("valor_minimo"):
            lines.append(f"       Valor mínimo: {c['valor_minimo']}")

    lines.append("")
    calificacion = rfp_data.get("criterios_calificacion", [])
    total = rfp_data.get("puntaje_total", 0)
    lines.append(f"CRITERIOS DE CALIFICACIÓN ({len(calificacion)}) — Total: {total} pts:")
    for c in calificacion:
        lines.append(f"  [{c['id']}] {c['nombre']}: {c['puntaje_maximo']} pts")

    return "\n".join(lines)