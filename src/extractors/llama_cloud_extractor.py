import time
from pathlib import Path
from typing import Union
from src.schemas import ClinicalStudy
from src.utils import get_llama_client


def extract_clinical_study(
    markdown_path: Union[str, Path]
) -> ClinicalStudy:
    '''
    Extracts clinical study information from the given markdown file using LlamaCloud's agentic extraction.
    
    Args:
        markdown_path: The local path to the markdown file.
    
    Returns:
        A ClinicalStudy object with the extracted information.
    '''

    client = get_llama_client()

    markdown_path = Path(markdown_path)
    if not markdown_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {markdown_path}")

    # Upload the markdown file to LlamaCloud
    file_obj = client.files.create(file=str(markdown_path), purpose="extract")

    job = client.extract.create(
        file_input=file_obj.id,
        configuration={
            "data_schema": ClinicalStudy.model_json_schema(),
            "tier": "agentic",
            "extraction_target": "per_doc",
            "parse_tier": "agentic",
            "cite_sources": True,
            "confidence_scores": True,
        },
    )

    while job.status not in ("COMPLETED", "FAILED", "CANCELLED"):
        time.sleep(2)
        job = client.extract.get(job.id)

    if job.status != "COMPLETED":
        raise RuntimeError(
            f"Extract job {job.id} ended in {job.status}: {job.error_message}"
        )

    return ClinicalStudy.model_validate(job.extract_result)