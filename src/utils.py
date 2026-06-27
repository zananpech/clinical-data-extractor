from llama_cloud import LlamaCloud
from functools import lru_cache
import os
from pathlib import Path
from dotenv import load_dotenv


def _load_api_key() -> str:
    """Loads the LlamaParse API key from .env.local or environment, raising if absent."""
    api_key = os.getenv("LLAMA_PARSE_API_KEY")
    if not api_key:
        env_path = Path(__file__).resolve().parent.parent / ".env.local"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
        else:
            env_fallback = Path(__file__).resolve().parent.parent / ".env"
            if env_fallback.exists():
                load_dotenv(dotenv_path=env_fallback)
        api_key = os.getenv("LLAMA_PARSE_API_KEY")

    if not api_key:
        raise EnvironmentError(
            "LLAMA_PARSE_API_KEY is not set. "
            "Please set it as an environment variable or add it to your .env.local file."
        )
    return api_key

@lru_cache(maxsize=1)
def get_llama_client() -> LlamaCloud:
    """Create and cache a single LlamaCloud client for the lifetime of the process."""
    return LlamaCloud(api_key=_load_api_key())
