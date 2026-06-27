from typing import Literal
from pydantic import BaseModel, Field
from instructor import CitationMixin

class CitedField(BaseModel):
    value: str = Field(default="--", description="The extracted value.")
    substring_quote: str = Field(default="--", description="The substring quote from the document.")
    section: str = Field(
        default="--",
        description="Document section where found, e.g. 'Table 1', 'Methods', 'Abstract'."
    )
    page: str = Field(default="--", description="Page number where the field was found.")
    confidence: Literal["high", "medium", "low"] = Field(
        default="high",
        description=(
            "high = explicitly stated verbatim; "
            "medium = minor interpretation needed; "
            "low = inferred or ambiguous"
        )
    )
    extraction_method: Literal["direct", "inferred", "calculated"] = Field(
        default="direct",
        description=(
            "direct = copied verbatim; "
            "inferred = reasoned from context; "
            "calculated = derived (e.g. SD from SE)"
        )
    )


class AgeEntry(BaseModel):
    """
    Represents participant age details for a specific treatment arm.
    """
    treatment: CitedField = Field(
        default_factory=lambda: CitedField(value="--"),
        description=(
            "The name/label of the treatment arm verbatim. "
            "If not reported, return '--'."
        )
    )
    age_n: CitedField = Field(
        default_factory=lambda: CitedField(value="--"),
        description=(
            "The number of patients evaluated for age in this treatment arm. "
            "If not reported, return '--'."
        )
    )
    age_esttype: CitedField = Field(
        default_factory=lambda: CitedField(value="--"),  
        description=(
            "The estimate type for the central-tendency of age: 'Mean' or 'Median'. "
            "If not reported, return '--'."
        )
    )
    age_estimate: CitedField = Field(
        default_factory=lambda: CitedField(value="--"),  
        description=(
            "The central-tendency value (mean or median) for age. "
            "If not reported, return '--'."
        )
    )
    age_disptype: CitedField = Field(
        default_factory=lambda: CitedField(value="--"),  
        description=(
            "The dispersion type: 'Range', 'SD', '95%CI','IQR'"
            "If not reported, return '--'."
        )
    )
    age_disp: CitedField = Field(
        default_factory=lambda: CitedField(value="--"),  
        description=(
            "The dispersion value (specifically when 'SD' is used). "
            "If not reported, return '--'."
        )
    )
    age_lb: CitedField = Field(
        default_factory=lambda: CitedField(value="--"),  
        description=(
            "The lower bound of age dispersion (the minimum value if 'Range', "
            "or the lower bound if 'IQR' or '95%CI'). "
            "If not reported, return '--'."
        )
    )
    age_ub: CitedField = Field(
        default_factory=lambda: CitedField(value="--"),  
        description=(
            "The upper bound of age dispersion (the maximum value if 'Range', "
            "or the upper bound if 'IQR' or '95%CI'). "
            "If not reported, return '--'."
        )
    )
    age_docname: CitedField = Field(
        default_factory=lambda: CitedField(value="--"),  
        description=(
            "The source document name (e.g., 'paper1.pdf'). "
            "If not reported, return '--'."
        )
    )
    age_comment: CitedField = Field(
        default_factory=lambda: CitedField(value="--"),  
        description=(
            "Any comments, notes, assumptions, or ambiguities worth flagging "
            "to a researcher regarding the age details. "
            "If not reported, return '--'."
        )
    )


class ClinicalStudy(CitationMixin, BaseModel):
    """
    Extracted clinical study metadata and participant characteristics from a research paper or poster.
    """
    document: CitedField = Field(
        default_factory=lambda: CitedField(value="--"),  
        description=(
            "The filename of the source document (e.g., 'paper1.pdf'). "
            "If not reported, return '--'."
        )
    )
    publication_year: CitedField = Field(
        default_factory=lambda: CitedField(value="--"),  
        description=(
            "The year the article was published. "
            "If not reported, return '--'."
        )
    )
    reported_study_design: CitedField = Field(
        default_factory=lambda: CitedField(value="--"),  
        description=(
            "The study design verbatim, exactly as written in the paper "
            "(do not normalize or paraphrase). "
            "If not reported, return '--'."
        )
    )
    study_setting: CitedField = Field(
        default_factory=lambda: CitedField(value="--"),  
        description=(
            "High-level setting class: 'Trial' or 'RWE' (real-world evidence). "
            "If not reported, return '--'."
        )
    )
    start_date: CitedField = Field(
        default_factory=lambda: CitedField(value="--"),  
        description=(
            "Study start date, formatted as DD/MM/YYYY. "
            "Extract from language like 'enrollment start', 'patients enrolled from', or 'data collected from'. "
            "Populate only from enrollment / data-collection language — don't substitute a publication date or a follow-up-only window. "
            "Formatting rule: Formatting DD/MM/YYYY, with fill-in for partial dates: "
            "month + year -> day = 01 (e.g., April 2024 -> 01/04/2024); "
            "year only -> 01/01/YYYY; "
            "season/quarter -> first day of the first month (e.g., Q2 2024 -> 01/04/2024); "
            "nothing reported -> '--'."
        )
    )
    end_date: CitedField = Field(
        default_factory=lambda: CitedField(value="--"),  
        description=(
            "Study end date, formatted as DD/MM/YYYY. "
            "Extract from language like 'enrollment end', 'patients enrolled until', 'follow-up cutoff', or 'data collected through'. "
            "Populate only from enrollment / data-collection language — don't substitute a publication date or a follow-up-only window. "
            "Formatting rule: Formatting DD/MM/YYYY, with fill-in for partial dates: "
            "month + year -> day = 01 (e.g., April 2024 -> 01/04/2024); "
            "year only -> 01/01/YYYY; "
            "season/quarter -> first day of the first month (e.g., Q2 2024 -> 01/04/2024); "
            "nothing reported -> '--'."
        )
    )
    age: list[AgeEntry] = Field(
        default_factory=list,
        description=(
            "Participant age details, with one object per treatment arm."
        )
    )
