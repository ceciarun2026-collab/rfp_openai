"""
scorer.py
Scoring consistente con evaluator tipado.
Incluye comentario general por propuesta y recomendacion unificada.
"""

import json
from openai import OpenAI
from dotenv import load_dotenv
import os
from pathlib import Path

# Cargar .env con ruta absoluta para compatibilidad con Streamlit
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=_api_key)
MODEL = "gpt-4o-mini"


# ─────────────────────────────────────────────
# MAIN SCORING
# ─────────────────────────────────────────────

def score_proposals(evaluations: list, rfp_data: dict) -> list:
    criterios_cal = rfp_data.get("criterios_calificacion", [])
    puntaje_total_max = rfp_data.get("puntaje_total", 100)

    # 1. EXTRAER PRECIOS
    precios = {}
    for ev in evaluations:
        provider = ev["provider"]
        cal = ev.get("calificacion", {})
        econ = cal.get("propuesta_economica_detalle", {})
        valor = econ.get("valor_total_sin_iva")
        if not valor:
            for c in cal.get("criterios_calificacion", []):
                if "precio" in c.get("nombre", "").lower():
                    valor = c.get("valor_numerico")
                    break
        precios[provider] = valor

    precios_validos = {k: v for k, v in precios.items() if v and v > 0}
    precio_minimo = min(precios_validos.values()) if precios_validos else None

    # 2. SCORING
    scored = []
    for ev in evaluations:
        provider = ev["provider"]
        cal = ev.get("calificacion", {})
        habilitacion = ev.get("habilitacion", {})
        habilitado = habilitacion.get("habilitado", False)
        puntaje_total = 0.0
        desglose = []

        for criterio_rfp in criterios_cal:
            cid = criterio_rfp["id"]
            nombre = criterio_rfp["nombre"]
            max_pts = criterio_rfp.get("puntaje_maximo", 0) or 0
            criterio_eval = next(
                (c for c in cal.get("criterios_calificacion", []) if c.get("id") == cid), None
            )
            puntaje = 0.0
            metodo = "no evaluado"

            if criterio_eval:
                # PRECIO (regla de 3 inversa — el menor precio obtiene el maximo)
                if "precio" in nombre.lower() and precio_minimo:
                    precio_proveedor = precios_validos.get(provider)
                    if precio_proveedor:
                        puntaje = (max_pts * precio_minimo) / precio_proveedor
                        puntaje = round(min(puntaje, max_pts), 2)
                        metodo = "precio_regla_3"
                    else:
                        metodo = "precio_missing"

                # NUMÉRICO — valor extraído del documento, capped al máximo
                elif criterio_eval.get("tipo_dato") == "numero":
                    valor = criterio_eval.get("valor_numerico")
                    if valor is not None and valor > 0:
                        puntaje = min(float(valor), max_pts)
                        metodo = "numerico_directo"
                    else:
                        metodo = "numerico_null"

                # BOOLEANO — cumple = puntaje máximo, no cumple = 0
                elif criterio_eval.get("tipo_dato") == "booleano":
                    if criterio_eval.get("cumple_condicion") is True:
                        puntaje = max_pts
                        metodo = "booleano_ok"
                    else:
                        puntaje = 0.0
                        metodo = "booleano_fail"

            puntaje_total += puntaje
            desglose.append({
                "id": cid,
                "nombre": nombre,
                "puntaje_maximo": max_pts,
                "puntaje_obtenido": puntaje,
                "metodo": metodo,
                "evidencia": criterio_eval.get("evidencia", "") if criterio_eval else "",
                "descripcion_calificacion": criterio_eval.get("descripcion_calificacion", "") if criterio_eval else "",
            })

        # comentario_general from calificacion
        comentario_general = cal.get("comentario_general", "")

        scored.append({
            "provider": provider,
            "habilitado": habilitado,
            "puntaje_total": round(puntaje_total, 2),
            "puntaje_maximo_posible": puntaje_total_max,
            "porcentaje": round((puntaje_total / puntaje_total_max * 100) if puntaje_total_max else 0, 1),
            "precio_ofertado": precios.get(provider),
            "desglose_puntaje": desglose,
            "habilitacion_detalle": habilitacion,
            "calificacion_detalle": cal,
            "comentario_general": comentario_general,
        })

    # 3. ORDENAMIENTO
    scored.sort(key=lambda x: (x["habilitado"], x["puntaje_total"]), reverse=True)

    # 4. RANKING
    for i, item in enumerate(scored, 1):
        item["ranking"] = i

    return scored


# ─────────────────────────────────────────────
# RECOMENDACIÓN — general sobre todas las propuestas
# ─────────────────────────────────────────────

def generate_recommendation(scored_proposals: list, rfp_data: dict) -> dict:
    proceso = rfp_data.get("proceso", {})
    habilitados = [p for p in scored_proposals if p["habilitado"]]

    if not habilitados:
        return {
            "recomendacion": "No hay propuestas habilitadas",
            "ganador_sugerido": None,
            "justificacion": "Ninguna propuesta cumple los criterios habilitantes requeridos.",
            "analisis_comparativo": "",
            "recomendacion_final": "Se recomienda declarar desierto el proceso o ampliar la convocatoria.",
        }

    resumen = [
        {
            "proveedor": p["provider"],
            "ranking": p["ranking"],
            "puntaje_total": p["puntaje_total"],
            "puntaje_maximo": p["puntaje_maximo_posible"],
            "porcentaje": p["porcentaje"],
            "precio": p["precio_ofertado"],
            "comentario_evaluacion": p.get("comentario_general", ""),
        }
        for p in scored_proposals
    ]

    prompt = f"""Eres un asesor experto en contratación y evaluación de propuestas.

Se te presentan los resultados de evaluación de un proceso de contratación. Tu tarea es generar una recomendación GENERAL que analice TODAS las propuestas en conjunto.

Proceso:
{json.dumps(proceso, ensure_ascii=False, indent=2)}

Resultados de evaluación (todas las propuestas):
{json.dumps(resumen, ensure_ascii=False, indent=2)}

Genera una recomendación objetiva, técnica y sustentada. Debes:
1. Identificar al ganador con el mayor puntaje entre los habilitados
2. Explicar por qué es la mejor opción comparando con las demás
3. Señalar aspectos relevantes de las otras propuestas (fortalezas y debilidades)
4. Incluir alertas si alguna propuesta tiene riesgos o inconsistencias
5. Dar una recomendación ejecutiva clara y accionable

Retorna SOLO JSON:
{{
  "ganador_sugerido": "nombre del proveedor recomendado",
  "justificacion": "Explicación detallada de 4-6 líneas de por qué es el ganador",
  "analisis_comparativo": "Análisis de 4-6 líneas comparando TODAS las propuestas evaluadas, señalando diferencias clave entre ellas",
  "alertas": ["lista de alertas o riesgos identificados en cualquier propuesta"],
  "recomendacion_final": "Recomendación ejecutiva concreta de 2-3 líneas para el tomador de decisión"
}}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=2000,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json","").replace("```","").strip()
    try:
        return json.loads(raw)
    except:
        return {"raw": raw, "ganador_sugerido": None, "justificacion": raw, "analisis_comparativo": "", "alertas": [], "recomendacion_final": ""}


# ─────────────────────────────────────────────
# RESUMEN (DEBUG)
# ─────────────────────────────────────────────

def build_ranking_summary(scored_proposals: list) -> str:
    lines = [
        f"{'#':<4} {'Proveedor':<30} {'Puntaje':<10} {'%':<8} {'Precio':>15} {'Estado'}",
        "-" * 90,
    ]
    for p in scored_proposals:
        precio = f"${p['precio_ofertado']:,.0f}" if p.get("precio_ofertado") else "N/D"
        estado = "HABILITADO" if p["habilitado"] else "NO HABILITADO"
        lines.append(
            f"{p['ranking']:<4} {p['provider'][:28]:<30} {p['puntaje_total']:<10.2f} "
            f"{p['porcentaje']:<8.1f} {precio:>15} {estado}"
        )
    return "\n".join(lines)