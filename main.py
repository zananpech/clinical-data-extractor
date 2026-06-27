import logging
import asyncio
from pathlib import Path
from src.extractors.llama_cloud_extractor import extract_clinical_study
from src.parsers.llama_cloud_parser import parse_doc

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    raw_data_dir = Path("data/raw")
    parsed_data_dir = Path("data/parsed")
    sample_pdf = raw_data_dir / "tan_2025_cIMS - Poster.pdf"

    if not sample_pdf.exists():
        logger.error(f"Sample PDF not found at {sample_pdf}")
        return

    logger.info(f"Parsing {sample_pdf} with LlamaCloud...")
    try:
        markdown_content = await parse_doc(
            sample_pdf, save_to=parsed_data_dir / "tan_2025_cIMS - Poster.md"
        )
        logger.info("Parsing successful! Preview of extracted Markdown:")
        logger.info("-" * 50)
        if markdown_content:
            logger.info(markdown_content[:50])
        logger.info("-" * 50)

        logger.info("Extracting clinical study information...")
        clinical_study = extract_clinical_study(parsed_data_dir / "tan_2025_cIMS - Poster.md")
        logger.info("Extraction successful! Clinical study information:")
        logger.info(clinical_study.model_dump_json(indent=2))
        logger.info(f"substring quotes: {clinical_study.substring_quotes}")

    except Exception as e:
        logger.error(f"An error occurred while parsing: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())

