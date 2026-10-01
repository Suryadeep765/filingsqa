import json
from pathlib import Path

import tiktoken


INPUT_PATH = Path(
    "data/processed/cleaned_filings.jsonl"
)

OUTPUT_PATH = Path(
    "data/processed/chunks.jsonl"
)

DEFAULT_CHUNK_SIZE = 512
DEFAULT_OVERLAP = 64


def get_encoder():
    return tiktoken.get_encoding("cl100k_base")


def chunk_text(
    text,
    encoder,
    chunk_size=DEFAULT_CHUNK_SIZE,
    overlap=DEFAULT_OVERLAP,
):
    if not text:
        return []

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    tokens = encoder.encode(text)

    chunks = []

    start = 0

    while start < len(tokens):
        end = min(
            start + chunk_size,
            len(tokens),
        )

        chunk_tokens = tokens[start:end]

        chunk_text_value = encoder.decode(
            chunk_tokens
        ).strip()

        if chunk_text_value:
            chunks.append(
                {
                    "text": chunk_text_value,
                    "source_start_token": start,
                    "source_end_token": end,
                    "token_count": len(chunk_tokens),
                }
            )

        if end >= len(tokens):
            break

        start = end - overlap

    return chunks


def create_chunks():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}"
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    encoder = get_encoder()

    total_chunks = 0
    total_filings = 0

    with (
        INPUT_PATH.open(
            encoding="utf-8"
        ) as input_file,
        OUTPUT_PATH.open(
            "w",
            encoding="utf-8"
        ) as output_file,
    ):
        for line in input_file:
            filing = json.loads(line)

            total_filings += 1

            for item in filing["items"]:
                chunks = chunk_text(
                    item["text"],
                    encoder,
                )

                for chunk_index, chunk in enumerate(
                    chunks
                ):
                    record = {
                        "accession_number": (
                            filing[
                                "accession_number"
                            ]
                        ),
                        "cik": filing["cik"],
                        "company_name": (
                            filing["company_name"]
                        ),
                        "filing_date": (
                            filing["filing_date"]
                        ),
                        "form_type": (
                            filing["form_type"]
                        ),
                        "filing_url": (
                            filing["filing_url"]
                        ),
                        "item": item["item"],
                        "chunk_index": chunk_index,
                        "text": chunk["text"],
                        "source_start_token": (
                            chunk[
                                "source_start_token"
                            ]
                        ),
                        "source_end_token": (
                            chunk[
                                "source_end_token"
                            ]
                        ),
                        "token_count": (
                            chunk["token_count"]
                        ),
                    }

                    output_file.write(
                        json.dumps(
                            record,
                            ensure_ascii=False,
                        )
                        + "\n"
                    )

                    total_chunks += 1

    print("=" * 70)
    print(f"Processed filings: {total_filings}")
    print(f"Generated chunks: {total_chunks}")
    print(f"Chunk size: {DEFAULT_CHUNK_SIZE}")
    print(f"Overlap: {DEFAULT_OVERLAP}")
    print(f"Saved to: {OUTPUT_PATH}")
    print("=" * 70)


if __name__ == "__main__":
    create_chunks()