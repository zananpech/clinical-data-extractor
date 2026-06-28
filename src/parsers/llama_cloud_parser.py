import logging
from pathlib import Path
from src.utils import get_llama_client

logger = logging.getLogger(__name__)


async def parse_doc(path: str | Path, save_to: str | Path) -> str | None:
    """
    Parses a document using LlamaCloud's agentic parser.

    Args:
        path: Local path to the document (PDF, Word, etc.).
        save_to: Path to save the extracted markdown content to.

    Returns:
        The extracted full markdown content.
    """
    client = get_llama_client()

    file_obj = client.files.create(file=str(path), purpose="parse")

    file_name = Path(path).name

    result = client.parsing.parse(
        file_id=file_obj.id,
        tier="agentic",
        version="latest",
        expand=["markdown_full"],
        processing_options={ "cost_optimizer": { "enable": True } }
    )

    markdown_content = f"# File name: {file_name}\n\n{result.markdown_full or ''}"

    save_to_path = Path(save_to)
    save_to_path.parent.mkdir(parents=True, exist_ok=True)
    save_to_path.write_text(markdown_content, encoding="utf-8")

    logger.info(f"Wrote {len(markdown_content)} chars of markdown to {save_to}")

    return markdown_content
