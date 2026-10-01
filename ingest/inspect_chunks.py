import json

from pathlib import Path


path = Path(
    "data/processed/chunks.jsonl"
)

with path.open(
    encoding="utf-8"
) as file:
    for index, line in enumerate(file):
        chunk = json.loads(line)

        print("=" * 80)
        print(f"Chunk: {index}")
        print(
            f"Company: "
            f"{chunk['company_name']}"
        )
        print(
            f"Item: "
            f"{chunk['item']}"
        )
        print(
            f"Chunk index: "
            f"{chunk['chunk_index']}"
        )
        print(
            f"Token count: "
            f"{chunk['token_count']}"
        )
        print(
            f"Token range: "
            f"{chunk['source_start_token']}"
            f" - "
            f"{chunk['source_end_token']}"
        )
        print()
        print(chunk["text"][:1500])
        print()

        if index >= 4:
            break