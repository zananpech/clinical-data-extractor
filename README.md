# Clinical Data Extractor

An automated pipeline that parses clinical research PDFs and extracts structured study metadata using LlamaCloud's agentic AI. Produces two output formats: a full audit trail for hallucination review and a flat JSON ready for SQL ingestion.

---

## How It Works

```
PDF → LlamaCloud Parser → Markdown → LlamaCloud Extractor → ClinicalStudy
                                                                    ↓
                                              data/output/audit/<stem>.json   (full CitedField audit)
                                              data/output/db/<stem>.json      (flat values for SQL)
```

1. **Parse**: The PDF is uploaded to LlamaCloud's agentic parser, which extracts full markdown.
2. **Extract**: The markdown is uploaded to LlamaCloud's extraction API, guided by the `ClinicalStudy` Pydantic schema.
3. **Output**: Two JSON files are written per document — one for auditing, one for storage.

---

## Project Structure

```
clinical-data-extractor/
├── main.py                          # CLI entry point
├── src/
│   ├── schemas.py                   # Pydantic data models (ClinicalStudy, AgeEntry, CitedField)
│   ├── utils.py                     # Shared LlamaCloud client + API key loader
│   ├── parsers/
│   │   └── llama_cloud_parser.py    # PDF → Markdown (LlamaCloud Parse API)
│   └── extractors/
│       ├── llama_cloud_extractor.py # Markdown → ClinicalStudy (LlamaCloud Extract API)
│       └── gemini_instructor.py     # Markdown → ClinicalStudy (Gemini + Instructor, alternative)
├── data/
│   ├── raw/                         # Input PDFs
│   ├── parsed/                      # Intermediate markdown files
│   └── output/
│       ├── audit/                   # Full CitedField JSONs for hallucination review
│       └── db/                      # Flat value-only JSONs for SQL storage
├── pyproject.toml
└── .env.local                       # API keys (not committed)
```

---

## Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) for dependency management
- A [LlamaCloud](https://cloud.llamaindex.ai/) account and API key
- (Optional) A Google Gemini API key if using the `gemini_instructor` extractor

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/zananpech/clinical-data-extractor.git
cd clinical-data-extractor
```

**2. Install dependencies**
```bash
uv sync
```

**3. Configure API keys**

Copy the example env file and fill in your keys:
```bash
cp .env.example .env.local
```

```env
LLAMA_PARSE_API_KEY=llx-...
GEMINI_API_KEY=AIza...        # only needed for the Gemini extractor
```

---

## Usage

### Run on a single PDF
```bash
uv run python main.py data/raw/paper.pdf
```

### Run on an entire folder of PDFs (concurrent)
```bash
uv run python main.py data/raw/
```

Results are written to:
- `data/output/audit/<stem>.json` — full audit output
- `data/output/db/<stem>.json` — DB-ready flat output

---

## Output Formats

### Audit JSON (`data/output/audit/`)
Each field is a full `CitedField` object containing the extracted value alongside supporting evidence. Used for **hallucination review**.

```json
{
  "publication_year": {
    "value": "2025",
    "substring_quote": "September 17-20, 2025; Toronto, Canada",
    "section": "Footer",
    "page": "1",
    "confidence": "high",
    "extraction_method": "direct"
  },
  "age": [
    {
      "treatment": { "value": "Teclistamab", ... },
      "age_n": { "value": "123", ... },
      ...
    }
  ]
}
```

### DB JSON (`data/output/db/`)
Flat value-only dict matching the target schema. Ready for SQL ingestion.

```json
{
  "document": "paper1.pdf",
  "publication_year": "2025",
  "reported_study_design": "retrospective, observational study",
  "study_setting": "RWE",
  "start_date": "25/10/2022",
  "end_date": "01/04/2025",
  "age": [
    {
      "treatment": "Teclistamab",
      "age_n": "123",
      "age_esttype": "Median",
      "age_estimate": "71",
      "age_disptype": "IQR",
      "age_disp": "--",
      "age_lb": "63",
      "age_ub": "77",
      "age_docname": "--",
      "age_comment": "--"
    }
  ]
}
```

---

## Tech Stack

| Component | Library |
|---|---|
| PDF Parsing | [LlamaCloud Parse API](https://docs.llamaindex.ai/en/stable/llama_cloud/) |
| Structured Extraction | [LlamaCloud Extract API](https://docs.llamaindex.ai/en/stable/llama_cloud/) |
| Schema Validation | [Pydantic v2](https://docs.pydantic.dev/) |
| Alternative Extractor | [Instructor](https://python.useinstructor.com/) + Gemini 2.5 Flash |
| Dependency Management | [uv](https://docs.astral.sh/uv/) |
| Runtime | Python 3.11 |
