import os
from pathlib import Path

from dotenv import load_dotenv
from llama_cloud import AsyncLlamaCloud


def _load_api_key() -> str:
    """Loads the LlamaParse API key from .env.local, raising if absent."""
    env_path = Path(__file__).resolve().parent.parent / ".env.local"
    load_dotenv(dotenv_path=env_path)

    api_key = os.getenv("LLAMA_PARSE_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "LLAMA_PARSE_API_KEY is not set. "
            "Add it to your .env.local file."
        )
    return api_key


def _make_client() -> AsyncLlamaCloud:
    """Constructs an authenticated AsyncLlamaCloud client."""
    return AsyncLlamaCloud(api_key=_load_api_key())


async def parse_doc(path: str | Path, save_to: str | Path) -> str | None:
    """
    Parses a document using LlamaCloud's agentic parser.

    Args:
        path: Local path to the document (PDF, Word, etc.).

    Returns:
        The extracted full markdown content.

    Raises:
        EnvironmentError: If the API key is missing.
        llama_cloud.ApiError: If the upstream API call fails.
    """
    client = _make_client()

    # Upload document for parsing
    file_obj = await client.files.create(file=str(path), purpose="parse")

    # Run the agentic parser on the uploaded file
    result = await client.parsing.parse(
        file_id=file_obj.id,
        tier="agentic",
        version="latest",
        expand=["markdown_full"],
    )

    with open(str(save_to), "w", encoding="utf-8") as f:
        f.write(result.markdown_full or '')

    return result.markdown_full
