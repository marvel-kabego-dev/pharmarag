from langchain_text_splitters import RecursiveCharacterTextSplitter
def split_pages(pages: list[dict]) -> list[dict]:
    """Split each page text into chunks while preserving source and page metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    result: list[dict] = []

    for page in pages:
        text = page.get("text", "")
        source = page.get("source")
        page_number = page.get("page")

        if not isinstance(text, str):
            continue

        chunks = splitter.split_text(text)

        for chunk_id, chunk_text in enumerate(chunks):
            result.append(
                {
                    "text": chunk_text,
                    "source": source,
                    "page": page_number,
                    "chunk_id": chunk_id,
                }
            )

    return result
