from collections.abc import Iterable


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    content = " ".join(text.split())
    if not content:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(content):
        end = min(start + chunk_size, len(content))
        chunks.append(content[start:end])
        if end == len(content):
            break
        start = max(0, end - overlap)
    return chunks


def summarize_evidence_snippets(snippets: Iterable[str], max_items: int = 5) -> list[str]:
    result: list[str] = []
    for snippet in snippets:
        cleaned = snippet.strip()
        if cleaned:
            result.append(cleaned[:240])
        if len(result) >= max_items:
            break
    return result
