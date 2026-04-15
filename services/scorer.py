"""
scorer.py
Calcula el puntaje de cada propuesta según las fórmulas del RFP
y genera el ranking final con recomendación.

Implementa la fórmula estándar de regla de tres inversa para precio:
  Puntaje_x = (Puntaje_máximo × Oferta_más_baja) / Oferta_x

Y aplica criterios booleanos (cumple = puntaje máximo, no cumple = 0).
"""

import json
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()
MODEL = "gpt-4o-mini"


def score_proposals(evaluations: list, rfp_data: dict) -> list:
    """
    Calcula el puntaje final de cada propuesta habilitada.
    Retorna lista ordenada por puntaje descendente.
    """
    criterios_cal = rfp_data.get("criterios_calificacion", [])
    puntaje_total_max = rfp_data.get("puntaje_total", 100)

    habilitados = []
    no_habilitados = []

    for ev in evaluations:
        hab = ev.get("habilitacion", {})
        if hab.get("habilitado", False):
            habilitados.append(ev)
        else:
            no_habilitados.append(ev)

    # Extraer precios de habilitados
    precios = {}
    for ev in habilitados:
        cal = ev.get("calificacion", {})
        prop_eco = cal.get("propuesta_economica_detalle", {})
        valor = prop_eco.get("valor_total_sin_iva", None)

        if valor is None:
            for c in cal.get("criterios_calificacion", []):
                if "precio" in c.get("nombre", "").lower():
                    try:
                        raw = str(c.get("valor_extraido", "0"))
                        valor = float(re.sub(r"[^\d.]", "", raw.replace(",", "")))
                    except (ValueError, TypeError):
                        valor = None
                    break

        precios[ev["provider"]] = valor

    precios_validos = {k: v for k, v in precios.items() if v and v > 0}
    precio_minimo = min(precios_validos.values()) if precios_validos else None

    scored = []
    for ev in habilitados:
        provider = ev["provider"]
        cal = ev.get("calificacion", {})
        desglose = []
        puntaje_total = 0.0

        for criterio_rfp in criterios_cal:
            cid = criterio_rfp["id"]
            nombre = criterio_rfp["nombre"]
            max_pts = criterio_rfp.get("puntaje_maximo", 0) or 0

            criterio_eval = next(
                (c for c in cal.get("criterios_calificacion", []) if c.get("id") == cid),
                None
            )

            puntaje_criterio = 0.0
            metodo = "no evaluado"

            if criterio_eval:
                if "precio" in nombre.lower() and precio_minimo:
                    precio_proveedor = precios_validos.get(provider)
                    if precio_proveedor and precio_proveedor > 0:
                        puntaje_criterio = (max_pts * precio_minimo) / precio_proveedor
                        puntaje_criterio = round(min(puntaje_criterio, max_pts), 2)
                        metodo = f"regla_3_inversa (precio: {precio_proveedor:,.0f}, mínimo: {precio_minimo:,.0f})"
                    else:
                        metodo = "precio no encontrado"
                elif criterio_eval.get("cumple_condicion") is True:
                    puntaje_criterio = max_pts
                    metodo = "booleano_cumple"
                else:
                    puntaje_criterio = 0.0
                    metodo = "booleano_no_cumple"

            desglose.append({
                "id": cid,
                "nombre": nombre,
                "puntaje_maximo": max_pts,
                "puntaje_obtenido": puntaje_criterio,
                "metodo": metodo,
                "evidencia": criterio_eval.get("evidencia", "") if criterio_eval else "",
            })
            puntaje_total += puntaje_criterio

        scored.append({
            "provider": provider,
            "habilitado": True,
            "puntaje_total": round(puntaje_total, 2),
            "puntaje_maximo_posible": puntaje_total_max,
            "porcentaje": round((puntaje_total / puntaje_total_max * 100) if puntaje_total_max else 0, 1),
            "precio_ofertado": precios.get(provider),
            "desglose_puntaje": desglose,
            "habilitacion_detalle": ev.get("habilitacion", {}),
            "calificacion_detalle": cal,
        })

    for ev in no_habilitados:
        scored.append({
            "provider": ev["provider"],
            "habilitado": False,
            "puntaje_total": 0,
            "puntaje_maximo_posible": puntaje_total_max,
            "porcentaje": 0,
            "precio_ofertado": None,
            "desglose_puntaje": [],
            "habilitacion_detalle": ev.get("habilitacion", {}),
            "calificacion_detalle": ev.get("calificacion", {}),
            "razon_no_habilitado": ev.get("habilitacion", {}).get(
                "resumen_habilitacion", "No cumple criterios habilitantes"
            ),
        })

    scored.sort(key=lambda x: (x["habilitado"], x["puntaje_total"]), reverse=True)

    pos = 1
    for item in scored:
        if item["habilitado"]:
            item["ranking"] = pos
            pos += 1
        else:
            item["ranking"] = None

    return scored


def generate_recommendation(scored_proposals: list, rfp_data: dict) -> dict:
    """
    Usa OpenAI para generar una recomendación narrativa de adjudicación.
    """
    proceso = rfp_data.get("proceso", {})
    habilitados = [p for p in scored_proposals if p["habilitado"]]

    if not habilitados:
        return {
            "recomendacion": "No se encontraron propuestas habilitadas.",
            "ganador_sugerido": None,
            "justificacion": "Ninguna propuesta cumplió los criterios habilitantes.",
        }

    resumen = []
    for p in habilitados:
        resumen.append({
            "proveedor": p["provider"],
            "ranking": p["ranking"],
            "puntaje": p["puntaje_total"],
            "porcentaje": p["porcentaje"],
            "precio": p["precio_ofertado"],
            "desglose": [
                {"criterio": d["nombre"], "puntos": d["puntaje_obtenido"], "max": d["puntaje_maximo"]}
                for d in p["desglose_puntaje"]
            ],
        })

    prompt = f"""Eres un asesor experto en contratación.

Se te presenta el resultado de la evaluación de propuestas para el siguiente proceso:
- Objeto: {proceso.get('objeto', 'N/D')}
- Entidad: {proceso.get('entidad_contratante', 'N/D')}

RANKING DE PROPUESTAS HABILITADAS:
{json.dumps(resumen, ensure_ascii=False, indent=2)}

Genera una recomendación de adjudicación con:
1. Ganador sugerido y justificación técnica
2. Análisis comparativo breve entre los primeros puestos
3. Alertas o consideraciones relevantes

Responde en JSON con este esquema:
{{
  "ganador_sugerido": "nombre del proveedor recomendado",
  "justificacion": "justificación técnica de 2-3 párrafos",
  "analisis_comparativo": "análisis breve comparando los primeros puestos",
  "alertas": ["lista de alertas o consideraciones importantes"],
  "recomendacion_final": "texto ejecutivo de 1 párrafo para decisores"
}}

Responde ÚNICAMENTE con el JSON, sin markdown."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw)
    except Exception:
        return {"recomendacion_raw": raw, "ganador_sugerido": None}


def build_ranking_summary(scored_proposals: list) -> str:
    """Resumen tabular del ranking para logs."""
    lines = [
        f"{'#':<4} {'Proveedor':<30} {'Puntaje':<10} {'%':<8} {'Precio':>15} {'Estado'}",
        "-" * 80,
    ]
    for p in scored_proposals:
        rank = str(p["ranking"]) if p["ranking"] else "N/H"
        precio = f"${p['precio_ofertado']:,.0f}" if p.get("precio_ofertado") else "N/D"
        estado = "HABILITADO" if p["habilitado"] else "NO HABILITADO"
        lines.append(
            f"{rank:<4} {p['provider'][:28]:<30} {p['puntaje_total']:<10.2f} "
            f"{p['porcentaje']:<8.1f} {precio:>15} {estado}"
        )
    return "\n".join(lines)
