# 🧵 Dhaga & Co. — Cataloging Pipeline Accelerator

Mini Project 1: Pattern-Based Workflow MVP

[![Tests](https://img.shields.io/badge/pytest-10%20passed-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)]()
[![Framework](https://img.shields.io/badge/framework-LangChain%20%7C%20Streamlit-orange.svg)]()
[![Provider](https://img.shields.io/badge/provider-Groq-purple.svg)]()

A lightweight internal cataloging MVP for Dhaga & Co. that turns messy vendor product data into structured, usable catalog entries with guardrails for quality and review.

---

## Why this project exists

Dhaga & Co. receives large volumes of vendor inputs with inconsistent fields, duplicate color names, conflicting fabric notes, and weak product titles. The listing team loses time on repetitive cleanup instead of focusing on merchandising decisions.

This project demonstrates a practical workflow that:

- standardizes raw SKU metadata into a clean schema
- maps messy vendor color strings to a canonical taxonomy
- generates Hinglish product copy and tags grounded in vendor context
- catches contradictory or unusable specs before they are published

The result is a demo-ready internal operations tool for faster catalog creation and safer automation.

---

## What the MVP does

### Core capabilities
- Vendor attribute normalization for titles, categories, fabric, and notes
- Canonical color mapping across a 16-color taxonomy
- Context-aware Hinglish listing copy and search tags
- Evaluator-style guardrails for contradictory fabric and invalid care instructions
- Human-review routing when the data fails defined quality checks

### Example flow
The application follows a structured pipeline:

`Raw Vendor Input -> Route & Extract -> Normalize Color -> Generate Copy -> Evaluate Guardrail`

This keeps deterministic logic and model-driven generation clearly separated.

---

## Project status

The repo is a working prototype and test-backed MVP.

- Python package: ready for local execution
- LLM integration: Groq-backed LangChain pipeline
- Frontend: Streamlit operations portal
- Validation: test suite passes

Current automated validation result:

```bash
python -m pytest -q
```

Result: 10 passed

---

## Quickstart

### 1. Clone the repository
```bash
git clone <repo-url>
cd fde-mini-project-01-dhaga-catalog-enrichment
```

### 2. Create a virtual environment
```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
copy .env.example .env
```

Then update `.env` with your Groq credentials:

```env
GROQ_API_KEY=your_groq_api_key_here
CHEAP_MODEL=openai/gpt-oss-20b
STRONG_MODEL=openai/gpt-oss-120b
```

> This project uses Groq, not OpenRouter. The app expects `GROQ_API_KEY` and optional model overrides via `CHEAP_MODEL` and `STRONG_MODEL`.

### 5. Run the tests
```bash
python -m pytest -q
```

### 6. Launch the Streamlit app
```bash
streamlit run app.py
```

Open the local app at `http://localhost:8501`.

---

## Architecture and design rules

### 1. Two-model deployment
The runtime is configured in `config.py` and `core/models.py`.

| Role | Default model | Temperature | Purpose |
| --- | --- | ---: | --- |
| Cheap / Fast | `openai/gpt-oss-20b` | `0.0` | category routing and raw attribute extraction |
| Strong / Creative | `openai/gpt-oss-120b` | `0.7` | copy generation and Hinglish tags |
| Evaluator path | same strong model | `0.1` | guardrail checks for contradictions and unsafe data |

### 2. Deterministic vs model-driven logic
The project intentionally separates logic by type:

- Deterministic code: price checks, SKU validation, canonical color mapping, schema validation, cost math
- Model-driven logic: unstructured category parsing, fabric extraction, copywriting, contradiction detection

This creates a safer system where business rules remain explicit and transparent.

### 3. Guardrail behavior
The pipeline is designed to fail visibly instead of silently publishing bad catalog data.

The intentional failure case is row `DHG-999` in `data/raw_vendor_samples.csv`:

- fabric: `100% heavy denim silk velvet`
- care notes: `do not wash do not dry clean tight oversized fit`

When processed, the item is marked `NEEDS_HUMAN_REVIEW` and the app highlights the invalid review reasons in the UI.

---

## Business logic and ROI framing

The repo includes a simple operational ROI model for the project brief.

| Metric | Value |
| --- | ---: |
| New SKUs per week | 400 |
| Average cost per SKU | ~₹0.18 |
| Weekly API cost | ~₹72 |
| Manual hours saved | ~86.7 hrs/week |
| Estimated labor savings | >₹20,000/week |

These values are defined in `config.py` and `core/cost_tracker.py` and are intended as demo-oriented business assumptions.

---

## Repository structure

```text
fde-mini-project-01-dhaga-catalog-enrichment/
├── README.md                     # Project overview and setup guide
├── .env.example                 # Groq environment template
├── .env                         # Local environment variables (not committed)
├── .gitignore
├── app.py                       # Streamlit catalog operations portal
├── config.py                    # Model config, temperatures, pricing, canonical colors
├── requirements.txt             # Python dependencies
├── discovery_note.md            # Project discovery note
├── build_note.md                # Implementation summary
├── phase3_presentation_script.md # Presentation script for client review
├── data/
│   └── raw_vendor_samples.csv   # Vendor sample rows including the explicit failure case
├── core/
│   ├── __init__.py
│   ├── color_normalizer.py      # Canonical 16-color mapping logic
│   ├── cost_tracker.py          # Weekly volume and ROI arithmetic
│   ├── models.py                # Groq-backed LangChain client setup
│   ├── pipeline.py              # 5-step workflow orchestration
│   └── schemas.py               # Pydantic schema and enum definitions
├── tests/
│   ├── test_color_normalizer.py
│   ├── test_pipeline.py
│   └── test_schemas.py
└── .streamlit/
    └── config.toml
```

---

## Troubleshooting

### LLM/auth errors
If the app shows an authentication or rate-limit error:

- verify that your `.env` file exists and contains a valid `GROQ_API_KEY`
- confirm the key is active in your Groq account
- retry after a brief pause if rate limits are hit

### Missing dependencies
```bash
pip install -r requirements.txt
```

### Test failures
```bash
python -m pytest -q
```

---

## Notes for maintainers

- The project is intentionally lightweight and easy to run locally.
- The live LLM path requires a valid Groq API key.
- The sample failure case (`DHG-999`) is deliberately retained as a visible QA and demo trigger.
- The app is designed to make broken catalog data obvious rather than silently passing it through.
