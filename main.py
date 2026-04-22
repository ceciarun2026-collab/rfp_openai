import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# IMPORTS AJUSTADOS A TU ESTRUCTURA
from utils.extractor import load_rfp, load_proposals
from services.rfp_parser import parse_rfp, summarize_criteria
from utils.evaluator import evaluate_proposal
from services.scorer import score_proposals, generate_recommendation, build_ranking_summary
from services.report_generator import generate_report


def save_json(data, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  → Guardado: {path}")


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def run_pipeline(rfp_dir, proposals_dir, output_dir):
    t_start = time.time()

    # ── ETAPA 1: Extracción de texto ──────────────────────────────
    log("═" * 60)
    log("ETAPA 1: Extracción de texto")
    log("═" * 60)

    log(f"Cargando RFP desde: {rfp_dir}")
    rfp_raw = load_rfp(rfp_dir)
    log(f"  RFP: {rfp_raw['filename']} ({len(rfp_raw['text'])} caracteres)")

    log(f"Cargando propuestas desde: {proposals_dir}")
    proposals_raw = load_proposals(proposals_dir)
    log(f"  Propuestas encontradas: {len(proposals_raw)}")

    for p in proposals_raw:
        archivos = len(p["files"])
        log(f"  · {p['provider']} ({archivos} archivo{'s' if archivos > 1 else ''})")

    save_json({
        "rfp_filename": rfp_raw["filename"],
        "rfp_text_preview": rfp_raw["text"][:500] + "...",
        "proposals": [
    {
        "provider": p["provider"],
        "num_files": len(p["files"]),
        "files": [f["filename"] for f in p["files"]],
    }
    for p in proposals_raw
]
    }, f"{output_dir}/01_extraccion.json")

    # ── ETAPA 2: Parsing del RFP ──────────────────────────────────
    log("")
    log("═" * 60)
    log("ETAPA 2: Análisis del RFP con IA")
    log("═" * 60)

    rfp_data = parse_rfp(rfp_raw["text"])
    save_json(rfp_data, f"{output_dir}/02_rfp_criterios.json")

    log("Criterios extraídos:")
    log(summarize_criteria(rfp_data))

    # ── ETAPA 3: Evaluación de propuestas ─────────────────────────
    log("")
    log("═" * 60)
    log(f"ETAPA 3: Evaluación de {len(proposals_raw)} propuestas")
    log("═" * 60)

    if not proposals_raw:
        log("[AVISO] No hay propuestas en input/proposals/")
        sys.exit(0)

    evaluations = []

    for i, proposal in enumerate(proposals_raw, 1):
        log(f"[{i}/{len(proposals_raw)}] Evaluando: {proposal['provider']}")

        ev = evaluate_proposal(
            provider_name=proposal["provider"],
            proposal_text=proposal["full_text"],
            rfp_data=rfp_data,
        )

        evaluations.append(ev)

        safe_name = proposal["provider"].replace(" ", "_").replace("/", "_")
        save_json(ev, f"{output_dir}/03_eval_{safe_name}.json")

    save_json(evaluations, f"{output_dir}/03_evaluaciones_todas.json")

    # ── ETAPA 4: Scoring y ranking ────────────────────────────────
    log("")
    log("═" * 60)
    log("ETAPA 4: Scoring y ranking")
    log("═" * 60)

    scored = score_proposals(evaluations, rfp_data)
    save_json(scored, f"{output_dir}/04_ranking.json")

    log("\nRANKING FINAL:")
    log(build_ranking_summary(scored))

    # ── ETAPA 5: Recomendación ────────────────────────────────────
    log("")
    log("═" * 60)
    log("ETAPA 5: Generando recomendación con IA")
    log("═" * 60)

    recommendation = generate_recommendation(scored, rfp_data)
    save_json(recommendation, f"{output_dir}/05_recomendacion.json")

    log(f"Ganador sugerido: {recommendation.get('ganador_sugerido', 'N/D')}")

    # ── ETAPA 6: Reporte Word ─────────────────────────────────────
    log("")
    log("═" * 60)
    log("ETAPA 6: Generando reporte Word")
    log("═" * 60)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    report_path = f"{output_dir}/reporte_evaluacion_{timestamp}.docx"

    generate_report(
        rfp_data=rfp_data,
        scored_proposals=scored,
        recommendation=recommendation,
        output_path=report_path,
    )

    # ── RESUMEN ───────────────────────────────────────────────────
    elapsed = round(time.time() - t_start, 1)

    log("")
    log("═" * 60)
    log(f"PIPELINE COMPLETADO en {elapsed}s")
    log(f"Archivos generados en: {output_dir}/")
    log(f"Reporte: {Path(report_path).name}")
    log("═" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluador de propuestas RFP con OpenAI")
    parser.add_argument("--rfp", default="input/rfp")
    parser.add_argument("--proposals", default="input/proposals")
    parser.add_argument("--output", default="output")

    args = parser.parse_args()

    if not Path(args.rfp).exists():
        print(f"ERROR: No existe: {args.rfp}")
        sys.exit(1)

    if not Path(args.proposals).exists():
        print(f"ERROR: No existe: {args.proposals}")
        sys.exit(1)

    run_pipeline(args.rfp, args.proposals, args.output)