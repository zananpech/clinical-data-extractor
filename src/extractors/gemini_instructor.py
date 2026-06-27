import instructor
from src.schemas import ClinicalStudy


# logging.basicConfig(level=logging.DEBUG)

def extract_clinical_study(markdown: str) -> ClinicalStudy:
    """
    Extracts clinical study information from the given markdown using Gemini 2.5 Flash.
    
    Args:
        markdown: The markdown content to extract information from.
    
    Returns:
        A ClinicalStudy object with the extracted information.
    """

    client = instructor.from_provider("google/gemini-2.5-flash")

    response = client.chat.completions.create(
        response_model=ClinicalStudy,
        messages=[
            {"role": "system", "content": ("You are a clinical data extraction assistant. Extract only information explicitly stated in the document. "
            "For each extracted field, populate `substring_quotes` with the exact "
            "verbatim phrase(s) from the source text that justify the extracted value. "
            "If no supporting text exists (e.g. filename), leave it empty."
        )},
            {"role": "user", "content": markdown},
        ],
        max_retries=3
    )

    return response
