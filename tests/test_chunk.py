import tiktoken
import pytest

from ingest.chunk import chunk_text


@pytest.fixture
def encoder():
    return tiktoken.get_encoding(
        "cl100k_base"
    )


def test_chunk_text_returns_chunks(encoder):
    text = "This is a test sentence. " * 200

    chunks = chunk_text(
        text,
        encoder,
        chunk_size=100,
        overlap=20,
    )

    assert len(chunks) > 1


def test_chunk_size_respected(encoder):
    text = "This is a test sentence. " * 100

    chunks = chunk_text(
        text,
        encoder,
        chunk_size=100,
        overlap=20,
    )

    for chunk in chunks:
        assert chunk["token_count"] <= 100


def test_overlap_validation(encoder):
    with pytest.raises(ValueError):
        chunk_text(
            "hello world",
            encoder,
            chunk_size=100,
            overlap=100,
        )


def test_empty_text(encoder):
    assert (
        chunk_text(
            "",
            encoder,
            chunk_size=100,
            overlap=20,
        )
        == []
    )