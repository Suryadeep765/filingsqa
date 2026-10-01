import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


INPUT_PATH = Path(
    "data/processed/chunks.jsonl"
)

OUTPUT_DIR = Path(
    "data/processed"
)

EMBEDDINGS_PATH = OUTPUT_DIR / "embeddings.npy"
METADATA_PATH = OUTPUT_DIR / "chunk_metadata.jsonl"

MODEL_NAME = "BAAI/bge-small-en-v1.5"


def load_chunks():
    chunks = []

    with INPUT_PATH.open(
        encoding="utf-8"
    ) as file:
        for line in file:
            chunks.append(
                json.loads(line)
            )

    return chunks


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    chunks = load_chunks()

    if not chunks:
        raise ValueError(
            "No chunks found."
        )

    print(
        f"Loaded {len(chunks)} chunks."
    )

    print(
        f"Loading embedding model: {MODEL_NAME}"
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    print("Generating embeddings...")

    embeddings = model.encode(
        texts,
        batch_size=16,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    embeddings = np.asarray(
        embeddings,
        dtype=np.float32,
    )

    print(
        f"Embedding shape: {embeddings.shape}"
    )

    np.save(
        EMBEDDINGS_PATH,
        embeddings,
    )

    with METADATA_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        for chunk in chunks:
            file.write(
                json.dumps(
                    chunk,
                    ensure_ascii=False,
                )
                + "\n"
            )

    print("=" * 70)
    print(
        f"Saved embeddings: {EMBEDDINGS_PATH}"
    )
    print(
        f"Saved metadata: {METADATA_PATH}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()