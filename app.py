"""
app.py - Frontend Streamlit para el Evaluador RFP con IA
Ejecutar con: streamlit run app.py
"""

import streamlit as st
import json
import os
import shutil
import tempfile
import time
from pathlib import Path
from datetime import datetime

# ── Configuración de página ────────────────────────────────────────
st.set_page_config(
    page_title="Evaluador RFP · IA",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personalizado ──────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid #334155;
  }
    /* Labels del radio (Una empresa / Varias empresas) */
    [data-testid="stSidebar"] .stRadio label {
    color: #ffffff !important;
  }

/* Texto interno del radio (por si Streamlit cambia estructura) */
[data-testid="stSidebar"] .stRadio div {
  color: #ffffff !important;
}
            

  [data-testid="stSidebar"] { color: #0f172a; /* ← EL COLOR QUE QUIERES */}
  [data-testid="stSidebar"] .stButton > button {
    width: 100%;
    text-align: left;
    background: transparent;
    border: none;
    color: #94a3b8 !important;
    padding: 10px 16px;
    border-radius: 8px;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
  }
  [data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(99,102,241,0.15) !important;
    color: #e2e8f0 !important;
  }

  /* Main area */
  .main .block-container { padding: 2rem 2.5rem; max-width: 1400px; }

  /* Cards */
  .card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  }
  .card-dark {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 24px;
    color: #e2e8f0;
  }

  /* Metric tiles */
  .metric-tile {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    border-radius: 12px;
    padding: 20px;
    color: white;
    text-align: center;
  }
  .metric-tile .value { font-size: 2.2rem; font-weight: 700; }
  .metric-tile .label { font-size: 0.8rem; opacity: 0.85; margin-top: 4px; }

  /* Rank badge */
  .rank-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px; height: 36px;
    border-radius: 50%;
    font-weight: 700;
    font-size: 15px;
    color: white;
  }
  .rank-1 { background: linear-gradient(135deg, #f59e0b, #d97706); }
  .rank-2 { background: linear-gradient(135deg, #94a3b8, #64748b); }
  .rank-3 { background: linear-gradient(135deg, #b45309, #92400e); }
  .rank-n { background: #ef4444; }

  /* Status pill */
  .pill-green { background:#dcfce7; color:#166534; padding:3px 10px; border-radius:999px; font-size:12px; font-weight:600; }
  .pill-red   { background:#fee2e2; color:#991b1b; padding:3px 10px; border-radius:999px; font-size:12px; font-weight:600; }
  .pill-blue  { background:#dbeafe; color:#1e40af; padding:3px 10px; border-radius:999px; font-size:12px; font-weight:600; }

  /* Progress bar */
  .prog-wrap { background:#e2e8f0; border-radius:999px; height:10px; overflow:hidden; }
  .prog-fill  { height:100%; border-radius:999px; transition:width 0.6s ease; }

  /* Section header */
  .section-header {
    font-size: 1.4rem;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 2px solid #6366f1;
    padding-bottom: 8px;
    margin-bottom: 20px;
  }

  /* Tab buttons active */
  .tab-active {
    background: #6366f1 !important;
    color: white !important;
    border-color: #6366f1 !important;
  }

  /* Upload area */
  [data-testid="stFileUploader"] {
    border: 2px dashed #c7d2fe;
    border-radius: 12px;
    padding: 12px;
    background: #f5f3ff;
  }

  /* Hide default streamlit menu for clean look */
  #MainMenu, footer { visibility: hidden; }

  /* Log box */
  .log-box {
    background: #0f172a;
    color: #4ade80;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    padding: 16px;
    border-radius: 8px;
    height: 300px;
    overflow-y: auto;
    line-height: 1.6;
  }

  /* Evidence box */
  .evidence-box {
    background: #f8fafc;
    border-left: 3px solid #6366f1;
    padding: 10px 14px;
    border-radius: 0 8px 8px 0;
    font-size: 13px;
    color: #475569;
    margin-top: 6px;
  }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "RFP"
if "companies" not in st.session_state:
    st.session_state.companies = ["Empresa 1"]
if "active_company" not in st.session_state:
    st.session_state.active_company = "Empresa 1"
if "pipeline_results" not in st.session_state:
    st.session_state.pipeline_results = {}
if "rfp_file" not in st.session_state:
    st.session_state.rfp_file = None
if "run_log" not in st.session_state:
    st.session_state.run_log = []
if "mode" not in st.session_state:
    st.session_state.mode = "single"   # "single" | "multi"
if "company_files" not in st.session_state:
    st.session_state.company_files = {}  # empresa -> lista de archivos (BytesIO)
if "rfp_criteria" not in st.session_state:
    st.session_state.rfp_criteria = {}

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:20px 0 8px 0;'>
      <div style='font-size:22px;font-weight:700;color:#e2e8f0;letter-spacing:-0.5px;'>📋 RFP Evaluator</div>
    </div>
    <hr style='border-color:#1e293b;margin:12px 0 20px 0;'>
    """, unsafe_allow_html=True)

    # Navigation
    nav_items = [
        ("RFP",               "📄  RFP & Criterios"),
        ("Propuestas",        "📂  Propuestas"),
        ("Resultados",        "📊  Resultados Globales"),
    ]
    for key, label in nav_items:
        active_style = "background:rgba(99,102,241,0.25)!important;color:#a5b4fc!important;font-weight:600!important;" if st.session_state.page == key else ""
        if st.button(label, key=f"nav_{key}",
                     use_container_width=True,
                     help=label):
            st.session_state.page = key
            st.rerun()

    st.markdown("<hr style='border-color:#1e293b;margin:20px 0;'>", unsafe_allow_html=True)

    # Mode selector
    st.markdown("<div style='font-size:12px;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;'>MODO DE EVALUACIÓN</div>", unsafe_allow_html=True)
    mode = st.radio("", ["Una empresa", "Varias empresas"], index=0 if st.session_state.mode == "single" else 1,
                    label_visibility="collapsed")
    st.session_state.mode = "single" if mode == "Una empresa" else "multi"

    st.markdown("<hr style='border-color:#1e293b;margin:16px 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:11px;color:#ffffff;text-align:center;'>RFP Evaluator v1.0</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────

def color_for_pct(pct: float) -> str:
    if pct >= 70:   return "#22c55e"
    elif pct >= 40: return "#f59e0b"
    return "#ef4444"

def render_progress_bar(pct: float, color: str = "#6366f1"):
    st.markdown(f"""
    <div class='prog-wrap'>
      <div class='prog-fill' style='width:{min(pct,100):.1f}%;background:{color};'></div>
    </div>
    <div style='font-size:12px;color:#64748b;text-align:right;margin-top:2px;'>{pct:.1f}%</div>
    """, unsafe_allow_html=True)

def format_currency(val, currency=""):
    if val is None:
        return "N/D"
    try:
        return f"{currency} {float(val):,.0f}".strip()
    except Exception:
        return str(val)

def run_pipeline_for(rfp_bytes, rfp_name, company_name, proposal_files):
    """Run the backend pipeline and return result dict."""
    import sys
    tmp = tempfile.mkdtemp()
    try:
        rfp_dir = os.path.join(tmp, "rfp")
        proposals_dir = os.path.join(tmp, "proposals", company_name)
        output_dir = os.path.join(tmp, "output")
        os.makedirs(rfp_dir); os.makedirs(proposals_dir); os.makedirs(output_dir)

        # Write RFP
        with open(os.path.join(rfp_dir, rfp_name), "wb") as f:
            f.write(rfp_bytes)

        # Write proposals
        for pf in proposal_files:
            pf.seek(0)
            with open(os.path.join(proposals_dir, pf.name), "wb") as f:
                f.write(pf.read())

        # Import & run pipeline
        orig_dir = os.getcwd()
        try:
            # Temporarily add project to path if needed
            from utils.extractor import load_rfp, load_proposals
            from services.rfp_parser import parse_rfp
            from utils.evaluator import evaluate_proposal
            from services.scorer import score_proposals, generate_recommendation
            from services.report_generator import generate_report

            rfp_raw = load_rfp(rfp_dir)
            proposals_raw = load_proposals(os.path.join(tmp, "proposals"))
            rfp_data = parse_rfp(rfp_raw["text"])
            evaluations = []
            for p in proposals_raw:
                ev = evaluate_proposal(p["provider"], p["full_text"], rfp_data)
                evaluations.append(ev)
            scored = score_proposals(evaluations, rfp_data)
            recommendation = generate_recommendation(scored, rfp_data)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            report_path = os.path.join(output_dir, f"reporte_{timestamp}.docx")
            generate_report(rfp_data, scored, recommendation, report_path)
            report_bytes = open(report_path, "rb").read() if os.path.exists(report_path) else None
            return {"rfp_data": rfp_data, "scored": scored,
                    "recommendation": recommendation, "report_bytes": report_bytes,
                    "report_name": f"reporte_{timestamp}.docx", "error": None}
        finally:
            os.chdir(orig_dir)
    except Exception as e:
        return {"error": str(e)}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

# ─────────────────────────────────────────────────────────────────
# PAGE: RFP
# ─────────────────────────────────────────────────────────────────
def page_rfp():
    st.markdown("<div class='section-header'>📄 RFP — Documento Evaluativo</div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("#### Subir archivo RFP")
        st.markdown("El RFP es el documento base con el que se comparan todas las propuestas.")
        uploaded_rfp = st.file_uploader(
            "Arrastra o selecciona el RFP (PDF o DOCX)",
            type=["pdf", "docx"],
            key="rfp_uploader",
        )
        if uploaded_rfp:
            st.session_state.rfp_file = uploaded_rfp
            st.success(f"✅ **{uploaded_rfp.name}** cargado correctamente")
            st.markdown(f"""
            <div class='card' style='margin-top:12px;'>
              <div style='font-size:13px;color:#64748b;margin-bottom:6px;'>ARCHIVO CARGADO</div>
              <div style='font-weight:600;color:#0f172a;'>{uploaded_rfp.name}</div>
              <div style='font-size:13px;color:#64748b;margin-top:4px;'>{uploaded_rfp.size / 1024:.1f} KB</div>
            </div>
            """, unsafe_allow_html=True)
        elif st.session_state.rfp_file:
            st.info(f"📎 Ya tienes cargado: **{st.session_state.rfp_file.name}**")

    with col_right:
        st.markdown("#### Criterios del RFP")
        if st.session_state.rfp_criteria:
            rc = st.session_state.rfp_criteria
            proc = rc.get("proceso", {})
            st.markdown(f"""
            <div class='card'>
              <div style='font-size:13px;color:#6366f1;font-weight:600;margin-bottom:10px;'>PROCESO DETECTADO</div>
              <div><b>Objeto:</b> {proc.get('objeto','N/D')}</div>
              <div style='margin-top:6px;'><b>Entidad:</b> {proc.get('entidad_contratante','N/D')}</div>
              <div style='margin-top:6px;'><b>Puntaje total:</b> {rc.get('puntaje_total', 100)} pts</div>
            </div>
            """, unsafe_allow_html=True)

            ch = rc.get("criterios_habilitantes", [])
            cc = rc.get("criterios_calificacion", [])

            if ch:
                st.markdown("**Criterios habilitantes**")
                for c in ch:
                    st.markdown(f"- `{c.get('id','')}` {c.get('nombre','')}")
            if cc:
                st.markdown("**Criterios de calificación**")
                for c in cc:
                    st.markdown(f"- `{c.get('id','')}` {c.get('nombre','')} · **{c.get('puntaje_maximo',0)} pts**")
        else:
            st.markdown("""
            <div class='card' style='border:2px dashed #c7d2fe;background:#f5f3ff;text-align:center;padding:40px 20px;color:#8b5cf6;'>
              <div style='font-size:2rem;margin-bottom:10px;'>🔍</div>
              <div style='font-weight:600;'>Sube el RFP para ver los criterios extraídos automáticamente</div>
              <div style='font-size:13px;margin-top:6px;color:#a78bfa;'>La IA analizará el documento y extraerá criterios habilitantes y de calificación</div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# PAGE: Propuestas
# ─────────────────────────────────────────────────────────────────
def page_propuestas():
    st.markdown("<div class='section-header'>📂 Propuestas de Empresas</div>", unsafe_allow_html=True)

    # Company tabs management
    if st.session_state.mode == "multi":
        col_mgmt1, col_mgmt2 = st.columns([3, 1])
        with col_mgmt1:
            st.markdown("**Gestionar empresas**")
        with col_mgmt2:
            if st.button("➕ Agregar empresa"):
                n = len(st.session_state.companies) + 1
                new_name = f"Empresa {n}"
                st.session_state.companies.append(new_name)
                st.session_state.active_company = new_name
                st.rerun()

    companies = st.session_state.companies if st.session_state.mode == "multi" else ["Empresa 1"]

    # Company selector tabs
    if len(companies) > 1:
        tab_cols = st.columns(len(companies))
        for i, company in enumerate(companies):
            with tab_cols[i]:
                is_active = st.session_state.active_company == company
                style = "background:#6366f1;color:white;border-color:#6366f1;" if is_active else ""
                if st.button(company, key=f"tab_{company}", use_container_width=True):
                    st.session_state.active_company = company
                    st.rerun()
    else:
        st.session_state.active_company = companies[0]

    active = st.session_state.active_company
    st.markdown(f"---")

    col_upload, col_result = st.columns([1, 1], gap="large")

    with col_upload:
        # Optionally rename the company
        if st.session_state.mode == "multi":
            new_name = st.text_input("Nombre de la empresa", value=active, key=f"name_{active}")
            if new_name != active and new_name.strip():
                idx = st.session_state.companies.index(active)
                st.session_state.companies[idx] = new_name
                if active in st.session_state.company_files:
                    st.session_state.company_files[new_name] = st.session_state.company_files.pop(active)
                st.session_state.active_company = new_name
                st.rerun()

        st.markdown("#### 📁 Subir archivos de propuesta")
        st.markdown("Puedes subir uno o varios archivos (PDF, DOCX). Corresponden a los documentos de esta empresa.")
        uploaded = st.file_uploader(
            f"Archivos para {active}",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            key=f"upload_{active}",
        )
        if uploaded:
            st.session_state.company_files[active] = uploaded

        files = st.session_state.company_files.get(active, [])
        if files:
            st.markdown(f"**{len(files)} archivo(s) cargado(s):**")
            for f in files:
                st.markdown(f"- 📄 `{f.name}` ({f.size/1024:.1f} KB)")

    with col_result:
        st.markdown("#### 📊 Resultado de evaluación")

        result = st.session_state.pipeline_results.get(active)
        if result and not result.get("error"):
            scored = result.get("scored", [])
            for p in scored:
                pct = p.get("porcentaje", 0)
                color = color_for_pct(pct)
                hab = p.get("habilitado", False)
                rank = p.get("ranking")

                st.markdown(f"""
                <div class='card'>
                  <div style='display:flex;justify-content:space-between;align-items:center;'>
                    <div style='font-weight:700;color:#0f172a;font-size:15px;'>{p['provider'][:40]}</div>
                    <span class='{"pill-green" if hab else "pill-red"}'>{'HABILITADO' if hab else 'NO HABILITADO'}</span>
                  </div>
                  <div style='margin-top:12px;'>
                    <div style='font-size:13px;color:#64748b;margin-bottom:4px;'>Puntaje total: <b style='color:#0f172a;'>{p['puntaje_total']} / {p['puntaje_maximo_posible']} pts</b></div>
                """, unsafe_allow_html=True)
                render_progress_bar(pct, color)
                st.markdown("</div></div>", unsafe_allow_html=True)

                # Breakdown
                with st.expander("Ver desglose de criterios"):
                    desglose = p.get("desglose_puntaje", [])
                    for d in desglose:
                        pts = d.get("puntaje_obtenido", 0)
                        max_pts = d.get("puntaje_maximo", 0)
                        c2 = color_for_pct((pts / max_pts * 100) if max_pts else 0)
                        st.markdown(f"**{d.get('id','')} — {d.get('nombre','')}**")
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            render_progress_bar((pts/max_pts*100) if max_pts else 0, c2)
                        with col2:
                            st.markdown(f"**{pts:.1f}** / {max_pts} pts")
                        if d.get("evidencia"):
                            st.markdown(f"<div class='evidence-box'>💬 {d['evidencia']}</div>", unsafe_allow_html=True)

        elif result and result.get("error"):
            st.error(f"❌ Error: {result['error']}")
        else:
            st.markdown("""
            <div class='card' style='border:2px dashed #e2e8f0;text-align:center;padding:40px 20px;color:#94a3b8;'>
              <div style='font-size:2rem;'>⏳</div>
              <div style='margin-top:8px;font-weight:600;'>Pendiente de evaluación</div>
              <div style='font-size:13px;margin-top:4px;'>Ejecuta la evaluación desde el botón inferior</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Run button ─────────────────────────────────────────────────
    st.markdown("---")
    col_btn, col_status = st.columns([1, 2])
    with col_btn:
        rfp_ready = st.session_state.rfp_file is not None
        files_ready = len(st.session_state.company_files.get(active, [])) > 0

        if not rfp_ready:
            st.warning("⚠️ Primero sube el RFP en la pestaña **RFP & Criterios**")
        elif not files_ready:
            st.warning("⚠️ Sube al menos un archivo de propuesta")
        else:
            if st.button(f"🚀 Evaluar propuesta de **{active}**", type="primary", use_container_width=True):
                with st.spinner(f"Evaluando {active}... esto puede tardar 1-3 minutos"):
                    rfp_file = st.session_state.rfp_file
                    rfp_file.seek(0)
                    result = run_pipeline_for(
                        rfp_bytes=rfp_file.read(),
                        rfp_name=rfp_file.name,
                        company_name=active,
                        proposal_files=st.session_state.company_files.get(active, []),
                    )
                    st.session_state.pipeline_results[active] = result
                    if result.get("rfp_data"):
                        st.session_state.rfp_criteria = result["rfp_data"]
                    st.success("✅ Evaluación completada")
                    st.rerun()

    with col_status:
        result = st.session_state.pipeline_results.get(active)
        if result and not result.get("error") and result.get("report_bytes"):
            st.download_button(
                "⬇️ Descargar reporte Word",
                data=result["report_bytes"],
                file_name=result.get("report_name", "reporte.docx"),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )


# ─────────────────────────────────────────────────────────────────
# PAGE: Resultados Globales
# ─────────────────────────────────────────────────────────────────
def page_resultados():
    st.markdown("<div class='section-header'>📊 Resultados Globales — Ranking de Propuestas</div>", unsafe_allow_html=True)

    all_results = {k: v for k, v in st.session_state.pipeline_results.items() if v and not v.get("error")}

    if not all_results:
        st.markdown("""
        <div class='card' style='text-align:center;padding:60px 20px;border:2px dashed #e2e8f0;'>
          <div style='font-size:3rem;'>📭</div>
          <div style='font-size:1.2rem;font-weight:700;color:#1e293b;margin-top:12px;'>Sin resultados aún</div>
          <div style='color:#64748b;margin-top:6px;'>Evalúa al menos una empresa para ver el ranking global</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Aggregate all scored proposals
    all_scored = []
    for company, result in all_results.items():
        for p in result.get("scored", []):
            all_scored.append({**p, "_empresa": company})

    all_scored.sort(key=lambda x: (x.get("habilitado", False), x.get("puntaje_total", 0)), reverse=True)

    # Summary metrics
    total = len(all_scored)
    habilitados = sum(1 for p in all_scored if p.get("habilitado"))
    mejor = all_scored[0] if all_scored else None

    mc1, mc2, mc3, mc4 = st.columns(4)
    metrics = [
        ("Total evaluadas", total, "#6366f1"),
        ("Habilitadas", habilitados, "#22c55e"),
        ("No habilitadas", total - habilitados, "#ef4444"),
        ("Mejor puntaje", f"{mejor['puntaje_total']:.1f}" if mejor else "—", "#f59e0b"),
    ]
    for col, (label, value, color) in zip([mc1, mc2, mc3, mc4], metrics):
        with col:
            st.markdown(f"""
            <div style='background:{color};border-radius:12px;padding:20px;text-align:center;color:white;'>
              <div style='font-size:2rem;font-weight:700;'>{value}</div>
              <div style='font-size:12px;opacity:0.9;margin-top:4px;'>{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── RANKING TABLE ──────────────────────────────────────────────
    st.markdown("### 🏆 Ranking completo")

    tab_ranking, tab_charts, tab_detail = st.tabs(["Tabla", "Gráficos", "Detalle por empresa"])

    with tab_ranking:
        st.markdown("""
        <div style='display:grid;grid-template-columns:50px 1fr 120px 120px 150px 130px;gap:8px;
                    padding:10px 12px;background:#f8fafc;border-radius:8px;
                    font-size:12px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;
                    margin-bottom:8px;'>
          <div>#</div><div>Empresa / Propuesta</div><div>Puntaje</div><div>%</div><div>Precio</div><div>Estado</div>
        </div>
        """, unsafe_allow_html=True)

        rank_counter = 1
        for p in all_scored:
            pct = p.get("porcentaje", 0)
            hab = p.get("habilitado", False)
            precio = p.get("precio_ofertado")
            moneda = p.get("calificacion_detalle", {}).get("propuesta_economica_detalle", {}).get("moneda", "")
            precio_str = format_currency(precio, moneda) if precio else "N/D"

            if hab:
                rank_label = str(rank_counter)
                rank_class = f"rank-{min(rank_counter, 3) if rank_counter <= 3 else 'n'}"
                rank_counter += 1
            else:
                rank_label = "—"
                rank_class = "rank-n"

            color = color_for_pct(pct)

            st.markdown(f"""
            <div style='display:grid;grid-template-columns:50px 1fr 120px 120px 150px 130px;gap:8px;
                        align-items:center;padding:14px 12px;background:white;border:1px solid #e2e8f0;
                        border-radius:10px;margin-bottom:6px;'>
              <div>
                <span class='rank-badge {rank_class}'>{rank_label}</span>
              </div>
              <div>
                <div style='font-weight:600;color:#0f172a;font-size:14px;'>{p['provider'][:45]}</div>
                <div style='font-size:12px;color:#94a3b8;margin-top:2px;'>{p.get("_empresa","")}</div>
              </div>
              <div style='font-weight:700;color:{color};font-size:16px;'>{p['puntaje_total']:.1f}</div>
              <div>{pct:.1f}%</div>
              <div style='font-size:13px;color:#475569;'>{precio_str}</div>
              <div><span class='{"pill-green" if hab else "pill-red"}'>{"HABILITADO" if hab else "NO HAB."}</span></div>
            </div>
            """, unsafe_allow_html=True)

    with tab_charts:
        if all_scored:
            try:
                import plotly.graph_objects as go
                import plotly.express as px

                # Bar chart — puntajes
                providers = [p["provider"][:30] for p in all_scored]
                scores = [p["puntaje_total"] for p in all_scored]
                colors_bar = [color_for_pct(p["porcentaje"]) for p in all_scored]

                fig_bar = go.Figure(go.Bar(
                    x=scores, y=providers,
                    orientation="h",
                    marker_color=colors_bar,
                    text=[f"{s:.1f}" for s in scores],
                    textposition="outside",
                ))
                fig_bar.update_layout(
                    title="Puntaje Total por Propuesta",
                    xaxis_title="Puntaje",
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    height=max(300, 60 * len(all_scored)),
                    margin=dict(l=10, r=80, t=40, b=20),
                    font=dict(family="DM Sans", size=13),
                )
                st.plotly_chart(fig_bar, use_container_width=True)

                # Breakdown radar (first habilitado only)
                first_hab = next((p for p in all_scored if p.get("habilitado") and p.get("desglose_puntaje")), None)
                if first_hab:
                    criterios = [d["nombre"][:20] for d in first_hab["desglose_puntaje"]]
                    vals = [d["puntaje_obtenido"] for d in first_hab["desglose_puntaje"]]
                    max_vals = [d["puntaje_maximo"] for d in first_hab["desglose_puntaje"]]

                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(
                        r=max_vals, theta=criterios, fill="toself",
                        fillcolor="rgba(99,102,241,0.1)", line_color="rgba(99,102,241,0.3)",
                        name="Máximo posible"
                    ))
                    fig_radar.add_trace(go.Scatterpolar(
                        r=vals, theta=criterios, fill="toself",
                        fillcolor="rgba(99,102,241,0.4)", line_color="#6366f1",
                        name=first_hab["provider"][:25]
                    ))
                    fig_radar.update_layout(
                        polar=dict(radialaxis=dict(visible=True)),
                        title=f"Perfil de criterios — {first_hab['provider'][:30]}",
                        showlegend=True,
                        font=dict(family="DM Sans"),
                        height=420,
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)

            except ImportError:
                # Fallback: native bar chart
                import pandas as pd
                df = pd.DataFrame({
                    "Propuesta": [p["provider"][:30] for p in all_scored],
                    "Puntaje": [p["puntaje_total"] for p in all_scored],
                })
                st.bar_chart(df.set_index("Propuesta"))

    with tab_detail:
        if not all_results:
            st.info("Sin resultados")
        for company, result in all_results.items():
            rec = result.get("recommendation", {})
            with st.expander(f"🏢 {company} — Recomendación IA", expanded=False):
                if rec:
                    if rec.get("ganador_sugerido"):
                        st.markdown(f"**🏆 Ganador sugerido:** {rec['ganador_sugerido']}")
                    if rec.get("justificacion"):
                        st.markdown(f"**Justificación:**\n{rec['justificacion']}")
                    if rec.get("analisis_comparativo"):
                        st.markdown(f"**Análisis comparativo:**\n{rec['analisis_comparativo']}")
                    alertas = rec.get("alertas", [])
                    if alertas:
                        st.markdown("**⚠️ Alertas:**")
                        for a in alertas:
                            st.markdown(f"- {a}")
                    if rec.get("recomendacion_final"):
                        st.info(f"📌 **Recomendación ejecutiva:** {rec['recomendacion_final']}")
                else:
                    st.markdown("Sin recomendación generada")

            # Download per company
            if result.get("report_bytes"):
                st.download_button(
                    f"⬇️ Descargar reporte de {company}",
                    data=result["report_bytes"],
                    file_name=result.get("report_name", f"reporte_{company}.docx"),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"dl_{company}",
                )

    # ── Recommendation highlight ───────────────────────────────────
    if all_results:
        st.markdown("---")
        st.markdown("### 💡 Recomendaciones de la IA")
        for company, result in all_results.items():
            rec = result.get("recommendation", {})
            if rec and rec.get("recomendacion_final"):
                st.markdown(f"""
                <div class='card' style='border-left:4px solid #6366f1;'>
                  <div style='font-size:12px;color:#6366f1;font-weight:700;margin-bottom:8px;'>
                    RECOMENDACIÓN — {company.upper()}
                  </div>
                  <div style='color:#1e293b;'>{rec['recomendacion_final']}</div>
                </div>
                """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# Router
# ─────────────────────────────────────────────────────────────────
page = st.session_state.page
if page == "RFP":
    page_rfp()
elif page == "Propuestas":
    page_propuestas()
elif page == "Resultados":
    page_resultados()
