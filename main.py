import asyncio
from pathlib import Path
from src.parser import parse_doc

async def main():
    raw_data_dir = Path("data/raw")
    parsed_data_dir = Path("data/parsed")
    sample_pdf = raw_data_dir / "tan_2025_cIMS - Poster.pdf"

    if not sample_pdf.exists():
        print(f"Sample PDF not found at {sample_pdf}")
        return

    print(f"Parsing {sample_pdf} with LlamaCloud...")
    try:
        markdown_content = await parse_doc(sample_pdf, save_to=parsed_data_dir/"tan_2025_cIMS - Poster.md")
        print("\nParsing successful! Preview of extracted Markdown:")
        print("-" * 50)
        if markdown_content:
            print(markdown_content[:50])
        print("-" * 50)
    except Exception as e:
        import traceback
        print(f"An error occurred while parsing: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
