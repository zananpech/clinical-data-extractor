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

1. **Parse**: The PDF is uploaded to LlamaCloud's agentic parser, which extracts a full markdown representation. The markdown is saved to `data/parsed/` for reference, allowing you to review parsing accuracy and layout preservation before extraction.
2. **Extract**: The parsed markdown is sent to LlamaCloud's extraction API, guided by the structure of the `ClinicalStudy` Pydantic schema.
3. **Output**: Two JSON files are written per document:
   - **Audit JSON** (`data/output/audit/`): Contains full `CitedField` objects (with source quotes, confidence ratings, and locations) to verify data quality and check for hallucinations.
   - **Flat JSON** (`data/output/db/`): Contains only flat values which are identical to the assignment requirement, ready for SQL ingestion.

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
├── Dockerfile                       # Multi-stage Docker build config
├── .dockerignore                    # Docker build ignore rules
├── .env.example                     # Template for environment variables
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

### Run with Docker

If you prefer to run the extractor without installing Python or packages locally, you can use Docker:

**1. Build the Docker image:**
```bash
docker build -t clinical-extractor .
```

**2. Run the pipeline:**
Pass your API keys via environment variables and mount the local `data` directory to access raw files and view results:

* **On Linux/macOS/Git Bash:**
  ```bash
  docker run --env-file .env.local -v $(pwd)/data:/app/data clinical-extractor data/raw/
  ```
* **On Windows (PowerShell):**
  ```powershell
  docker run --env-file .env.local -v ${PWD}/data:/app/data clinical-extractor data/raw/
  ```

Results are written to:
- `data/output/audit/<stem>.json` — full audit output
- `data/output/db/<stem>.json` — DB-ready flat output which is identical to the assignment requirement

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

---

## PDF Parsing & Extraction Challenges
* Initially, I experimented with open-source parsers (like Docling), but it took too long to parse the data because it tried to load a VLM to extract data from charts, and my local development machine does not have a GPU.
* Then, I decided to use LlamaCloud Parse for parsing and Instructor + Gemini to extract structured data from the generated markdown. This was much faster, but the extracted values suffered from hallucinations, which I believe was a limitation of the smaller models.
* Finally, I switched to LlamaCloud Agentic Extraction for both parsing and extracting data directly. This approach yielded highly accurate results, which I double-checked and verified against the provided source citations.

---

## Schema & Definitional Choices

Every extracted field is wrapped in a `CitedField` object containing:
- `value` — the extracted data point.
- `substring_quote` — the verbatim quote from the source document that justifies the value.
- `page`, `section`, `confidence` (`high`/`medium`/`low`), and `extraction_method` (`direct`/`inferred`/`calculated`).

Key decisions in the `AgeEntry` schema:
- `age_disp` is only populated when the dispersion type is SD. For Range, IQR, and 95%CI, the bounds are stored in `age_lb` / `age_ub`.
- `study_setting` is a normalized classification (`"Trial"` or `"RWE"`), kept separate from `reported_study_design`, which preserves the verbatim phrasing from the paper.
- Missing values default to `"--"` across all fields, as specified.

---

## Accuracy Evaluation & Researcher Validation

To scale this pipeline responsibly, we need to ensure high data integrity. Here is how I would evaluate accuracy in collaboration with a clinical researcher and how this system's architecture facilitates that process:

### 1. Accuracy Evaluation Methodology
* **Golden Dataset**: Work with a researcher to manually extract data from a representative sample of 15–20 study PDFs to establish a ground-truth dataset.
* **Evaluation Metrics**:
  * **Exact Match (EM)**: Used for structured fields like `publication_year`, `study_setting` (e.g., RWE vs. Clinical Trial), and dates.
  * **Semantic Similarity (BERTScore/LLM-as-a-Judge)**: Used for free-text fields like `reported_study_design` where phrasing might differ slightly from the source but carry the identical clinical meaning.
  * **Precision/Recall/F1-Score**: Used for nested list extractions (like the `age` lists) to ensure we did not miss any patient subgroups (Recall) or invent extra groups (Precision).

### 2. How the System Facilitates Validation (The Audit Trail)
Manual validation of clinical data is traditionally slow because researchers have to scroll through long PDFs to verify numbers. This system solves that by producing a comprehensive **Audit JSON** (`data/output/audit/`):
* Every single field is extracted as a `CitedField` mapping, containing the `value`, the exact `substring_quote` from the paper, the `page` number, and the model's self-assessed `confidence` score.
* This changes the researcher's job from a **search task** (hunting for data across pages) to a **verification task** (simply checking if the `substring_quote` on the cited `page` supports the extracted `value`). This reduces manual auditing time by a lot.
* We can also help researchers in automating this validation process by checking if all quoted substrings exist in the source documents.

---

## Future Improvements (With More Time)

If I had more time to work on this project, I would focus on the following enhancements:

1. **Interactive Audit Dashboard (UI)**:
   * Build a lightweight web application (a simple React app) where a researcher can upload and see the PDF on the left and the extracted fields on the right.
   * Clicking on any field automatically scrolls the PDF viewer to the correct `page` and highlights the corresponding `substring_quote`.
2. **Dynamic Schema Validation & Self-Correction**:
   * Add a validation loop after extraction. If custom Pydantic validators fail (e.g., `end_date` is chronologically before `start_date`), feed the validation error back to the LLM as a prompt for auto-correction.
3. **Hybrid Parsing and Routing**:
   * Implement a router that inspects PDFs: native digital PDFs can be parsed locally and cheaply, whereas scanned documents, image-heavy pages, or complex tables are automatically routed to LlamaCloud Parse to save API costs. Utilize open-source tools like `docling` or `unstructured` if we have access to a GPU to help reduce costs.
4. **Deduplication**:
   * Implement file content hashing (e.g., SHA-256) and extract metadata identifiers (e.g., DOI, ClinicalTrials.gov NCT IDs) to detect and skip duplicate publications, preventing redundant parsing and API costs.
5. **CI/CD Integration & Extraction Regression Tests**:
   * Build automated test suites that run the extraction over a fixed set of synthetic mock-clinical markdowns. This ensures updates to schemas or prompts don't cause performance regressions on existing fields.
   * Automate the Docker image build in the cloud and run tests to ensure everything is working as expected.
6. **Observability & Monitoring**:
   * Integrate LLM tracing tools like Langfuse to monitor token usage, API costs, latency, and performance. Stream logs to a service like Sentry to track runtime errors in real-time.
7. **Evaluation & Benchmarking**:
   * Create a gold standard dataset to evaluate the performance of the extraction system.
   * Compare the performance of different LLMs (e.g., Claude, GPT, Gemini) for the extraction task if later on we decide to move away from LlamaCloud.
   * Implement a validation pipeline to check if quoted substrings actually exist in the source documents.
8. **Security & Input Sanitization**:
   * Add a guardrail middleware to defend against prompt injection, PII detection, and toxicity during the ingestion process to ensure HIPAA safety and prompt integrity.
9. **Storage**:
   * Integrate with cloud storage solutions like AWS S3 to store extracted data and markdown files.
   * If necessary, store extracted structured data into AWS RDS database or DynamoDB so that researchers can query in future for data analysis.

---

## Coding Assistant Utilization

I used an AI coding assistant (Claude) as a pair programmer and technical advisor throughout the development of this project:

* **Tool Research & Evaluation**: Researched different PDF parsing and extraction libraries (such as comparing local solutions like Docling with API endpoints like LlamaCloud). The assistant compiled trade-off analyses, allowing me to make informed technical decisions.
* **Architectural Peer Review**: I drafted the initial ingestion pipeline and used the assistant to challenge my assumptions, identify potential edge cases (such as rate limits and concurrent processing failures), and iterate on the design until the pipeline was robust.
* **Implementation & Code Quality**: Collaborated with the assistant to refactor key components, enhance logging and error-handling structures.
* **Documentation Improvement**: I used the assistant to help me improve the documentation and make it more clear and concise.
