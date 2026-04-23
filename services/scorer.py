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
    Calcula el puntaje final de cada propuesta.
    TODAS participan en ranking, pero la habilitación se respeta.
    """

    criterios_cal = rfp_data.get("criterios_calificacion", [])
    puntaje_total_max = rfp_data.get("puntaje_total", 100)

    todos = evaluations

    # -----------------------------
    # 1. EXTRAER PRECIOS
    # -----------------------------
    precios = {}
    for ev in todos:
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

    # -----------------------------
    # 2. SCORING
    # -----------------------------
    scored = []

    for ev in todos:
        provider = ev["provider"]
        cal = ev.get("calificacion", {})
        desglose = []
        puntaje_total = 0.0
        
        # 🔹 HABILITACIÓN REAL
        habilitacion = ev.get("habilitacion", {})
        habilitado = habilitacion.get("habilitado", False)

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
            "habilitado": habilitado,
            "puntaje_total": round(puntaje_total, 2),
            "puntaje_maximo_posible": puntaje_total_max,
            "porcentaje": round((puntaje_total / puntaje_total_max * 100) if puntaje_total_max else 0, 1),
            "precio_ofertado": precios.get(provider),
            "desglose_puntaje": desglose,
            "habilitacion_detalle": habilitacion,
            "calificacion_detalle": cal,
        })

    # -----------------------------
    # 3. ORDENAMIENTO
    # -----------------------------
    scored.sort(
        key=lambda x: (x["habilitado"], x["puntaje_total"]),
        reverse=True
    )

    # -----------------------------
    # 4. RANKING (TODOS)
    # -----------------------------
    for i, item in enumerate(scored, 1):
        item["ranking"] = i

    return scored


def generate_recommendation(scored_proposals: list, rfp_data: dict) -> dict:
    """
    Genera recomendación SOLO con habilitados
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

Proceso:
- Objeto: {proceso.get('objeto', 'N/D')}
- Entidad: {proceso.get('entidad_contratante', 'N/D')}

Ranking habilitados:
{json.dumps(resumen, ensure_ascii=False, indent=2)}

Devuelve JSON con:
ganador_sugerido, justificacion, analisis_comparativo, alertas, recomendacion_final
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
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
    """Resumen tabular"""
    lines = [
        f"{'#':<4} {'Proveedor':<30} {'Puntaje':<10} {'%':<8} {'Precio':>15} {'Estado'}",
        "-" * 80,
    ]

    for p in scored_proposals:
        precio = f"${p['precio_ofertado']:,.0f}" if p.get("precio_ofertado") else "N/D"
        estado = "HABILITADO" if p["habilitado"] else "NO HABILITADO"

        lines.append(
            f"{p['ranking']:<4} {p['provider'][:28]:<30} {p['puntaje_total']:<10.2f} "
            f"{p['porcentaje']:<8.1f} {precio:>15} {estado}"
        )

    return "\n".join(lines)