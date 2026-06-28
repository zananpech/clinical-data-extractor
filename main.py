import json
import logging
import asyncio
import argparse
from pathlib import Path
from src.extractors.llama_cloud_extractor import extract_clinical_study
from src.parsers.llama_cloud_parser import parse_doc

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger(__name__)

PARSED_DIR = Path("data/parsed")
AUDIT_DIR = Path("data/output/audit")
DB_DIR = Path("data/output/db")


async def process_pdf(pdf_path: Path) -> None:
    """Run the full parse → extract pipeline for a single PDF."""
    stem = pdf_path.stem
    md_path = PARSED_DIR / f"{stem}.md"
    audit_path = AUDIT_DIR / f"{stem}.json"
    db_path = DB_DIR / f"{stem}.json"

    PARSED_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    DB_DIR.mkdir(parents=True, exist_ok=True)

    logger.info(f"[{stem}] Parsing PDF...")
    markdown_content = await parse_doc(pdf_path, save_to=md_path)

    if not markdown_content:
        logger.warning(f"[{stem}] Parsing returned empty content, skipping extraction.")
        return

    logger.info(f"[{stem}] Extracting clinical study data...")
    clinical_study = extract_clinical_study(md_path)

    audit_path.write_text(clinical_study.model_dump_json(indent=2), encoding="utf-8")
    logger.info(f"[{stem}] Saved audit data to {audit_path}")

    db_path.write_text(json.dumps(clinical_study.to_db_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"[{stem}] Saved DB data to {db_path}")


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clinical data extractor — parse PDFs and extract structured study data."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to a PDF file or a folder containing PDFs.",
    )
    args = parser.parse_args()
    input_path: Path = args.input

    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        return

    if input_path.is_file():
        if input_path.suffix.lower() != ".pdf":
            logger.error(f"Input file must be a PDF, got: {input_path.suffix}")
            return
        pdfs = [input_path]
    elif input_path.is_dir():
        pdfs = sorted(input_path.glob("*.pdf"))
        if not pdfs:
            logger.warning(f"No PDF files found in folder: {input_path}")
            return
        logger.info(f"Found {len(pdfs)} PDF(s) in {input_path}")
    else:
        logger.error(f"Input path is neither a file nor a directory: {input_path}")
        return

    await asyncio.gather(*[process_pdf(pdf) for pdf in pdfs])
    logger.info("Pipeline complete.")


if __name__ == "__main__":
    asyncio.run(main())


