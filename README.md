# RFP Evaluator — Evaluador de Propuestas Comerciales con IA
**Motor de IA: OpenAI gpt-4o-mini**

Agente de evaluación automática de propuestas comerciales.
Analiza un RFP, evalúa propuestas de múltiples proveedores y genera un reporte Word con ranking y recomendación.

## Estructura del proyecto

```
rfp_evaluator/
├── main.py               # Pipeline principal (orquestador)
├── extractor.py          # Extracción de texto PDF / DOCX
├── rfp_parser.py         # Parsing del RFP → JSON de criterios
├── evaluator.py          # Evaluación de propuestas con IA
├── scorer.py             # Scoring, ranking y recomendación
├── report_generator.py   # Generación del reporte Word
├── requirements.txt
├── .env                  # Tu OPENAI_API_KEY va aquí
├── input/
│   ├── rfp/              # Coloca aquí el RFP (1 archivo PDF o DOCX)
│   └── proposals/        # Coloca aquí las propuestas
│       ├── proveedor_A.pdf                  ← propuesta de 1 archivo
│       └── proveedor_B/                     ← propuesta multi-documento
│           ├── cotizacion.pdf
│           └── experiencia.pdf
└── output/               # Resultados generados automáticamente
```

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

Edita el archivo `.env` y pon tu API key de OpenAI:
```
OPENAI_API_KEY=sk-proj-...
```

Obtén tu key en: https://platform.openai.com/api-keys

## Uso

```bash
python main.py
```

O con rutas personalizadas:
```bash
python main.py --rfp input/rfp/ --proposals input/proposals/ --output output/
```

## Archivos de salida

| Archivo | Contenido |
|---|---|
| `01_extraccion.json` | Textos extraídos de todos los documentos |
| `02_rfp_criterios.json` | Criterios habilitantes y de calificación del RFP |
| `03_eval_[proveedor].json` | Evaluación individual por proveedor |
| `03_evaluaciones_todas.json` | Todas las evaluaciones consolidadas |
| `04_ranking.json` | Ranking con puntajes detallados |
| `05_recomendacion.json` | Recomendación narrativa de la IA |
| `reporte_evaluacion_[fecha].docx` | Reporte Word final |

## Pipeline

```
RFP + Propuestas (PDF/DOCX)
        ↓
  extractor.py     → texto limpio por documento
        ↓
  rfp_parser.py    → JSON: criterios habilitantes + calificación
        ↓
  evaluator.py     → JSON por proveedor: cumplimiento + datos económicos
        ↓
  scorer.py        → ranking con fórmula de precio + criterios booleanos
        ↓
  report_generator.py → reporte Word profesional
```

## Fórmula de precio

Implementa la regla de tres inversa estándar:

```
Puntaje_x = (Puntaje_máximo × Oferta_más_baja) / Oferta_x
```

## Modelo de IA

Usa `gpt-4o-mini` (OpenAI) — económico y preciso para:
- Extracción estructurada de criterios del RFP
- Evaluación de cumplimiento con evidencia
- Generación de recomendación narrativa
