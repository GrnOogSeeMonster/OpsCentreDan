from app.rag.chunking import chunk_text


def test_chunk_text_produces_overlap_chunks() -> None:
    source = "a" * 2400
    chunks = chunk_text(source, chunk_size=900, overlap=100)

    assert len(chunks) >= 3
    assert len(chunks[0]) == 900
    assert len(chunks[1]) >= 800


def test_chunk_text_empty_input() -> None:
    assert chunk_text("   ") == []
