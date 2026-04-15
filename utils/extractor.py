"""
extractor.py
Extrae texto de archivos PDF y DOCX.
Soporta documentos multi-página y preserva estructura básica.
"""

import os
from pathlib import Path


def extract_text(filepath: str) -> str:
    """
    Extrae el texto completo de un archivo PDF o DOCX.
    Retorna el texto como string limpio.
    """
    path = Path(filepath)
    ext = path.suffix.lower()

    if ext == ".pdf":
        return _extract_pdf(filepath)
    elif ext in (".docx", ".doc"):
        return _extract_docx(filepath)
    else:
        raise ValueError(f"Formato no soportado: {ext}. Use PDF o DOCX.")


def _extract_pdf(filepath: str) -> str:
    """Extrae texto de PDF usando pdfplumber."""
    import pdfplumber

    pages_text = []
    with pdfplumber.open(filepath) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text and text.strip():
                pages_text.append(f"[Página {i}]\n{text.strip()}")

    return "\n\n".join(pages_text)


def _extract_docx(filepath: str) -> str:
    """Extrae texto de DOCX preservando párrafos y tablas."""
    from docx import Document
    from docx.oxml.ns import qn

    doc = Document(filepath)
    parts = []

    for element in doc.element.body:
        tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag

        if tag == "p":
            para_text = "".join(
                run.text for run in element.findall(f".//{qn('w:t')}")
            ).strip()
            if para_text:
                parts.append(para_text)

        elif tag == "tbl":
            rows = element.findall(f".//{qn('w:tr')}")
            for row in rows:
                cells = row.findall(f".//{qn('w:tc')}")
                cell_texts = []
                for cell in cells:
                    cell_text = "".join(
                        t.text or "" for t in cell.findall(f".//{qn('w:t')}")
                    ).strip()
                    cell_texts.append(cell_text)
                if any(cell_texts):
                    parts.append(" | ".join(cell_texts))

    return "\n".join(parts)


def load_rfp(rfp_dir: str) -> dict:
    """
    Carga el RFP desde la carpeta indicada.
    Espera exactamente un archivo PDF o DOCX.
    Retorna: {"filename": str, "text": str}
    """
    rfp_path = Path(rfp_dir)
    files = list(rfp_path.glob("*.pdf")) + list(rfp_path.glob("*.docx"))

    if not files:
        raise FileNotFoundError(f"No se encontró ningún PDF o DOCX en {rfp_dir}")
    if len(files) > 1:
        print(f"[AVISO] Se encontraron {len(files)} archivos en {rfp_dir}. "
              f"Se usará: {files[0].name}")

    filepath = str(files[0])
    text = extract_text(filepath)
    return {"filename": files[0].name, "text": text}


def load_proposals(proposals_dir: str) -> list:
    """
    Carga todas las propuestas de la carpeta indicada.
    Cada propuesta puede ser una carpeta o un archivo individual.

    Estructura soportada:
      proposals/
        proveedor_A.pdf          <- propuesta de un solo archivo
        proveedor_B/             <- propuesta multi-documento
          cotizacion.pdf
          certificado_sap.pdf

    Retorna lista de:
      {"provider": str, "files": [{"filename": str, "text": str}], "full_text": str}
    """
    proposals_path = Path(proposals_dir)
    proposals = []

    # Archivos directos en la carpeta raíz
    direct_files = (
        list(proposals_path.glob("*.pdf")) +
        list(proposals_path.glob("*.docx"))
    )
    for f in sorted(direct_files):
        provider_name = f.stem
        text = extract_text(str(f))
        proposals.append({
            "provider": provider_name,
            "files": [{"filename": f.name, "text": text}],
            "full_text": text,
        })

    # Subcarpetas (propuesta multi-documento)
    for subdir in sorted(p for p in proposals_path.iterdir() if p.is_dir()):
        provider_name = subdir.name
        sub_files = (
            list(subdir.glob("*.pdf")) +
            list(subdir.glob("*.docx"))
        )
        if not sub_files:
            continue

        file_entries = []
        combined_text_parts = []
        for f in sorted(sub_files):
            text = extract_text(str(f))
            file_entries.append({"filename": f.name, "text": text})
            combined_text_parts.append(f"=== {f.name} ===\n{text}")

        proposals.append({
            "provider": provider_name,
            "files": file_entries,
            "full_text": "\n\n".join(combined_text_parts),
        })

    return proposals
