import json
from pathlib import Path

import faiss
import numpy as np


EMBEDDINGS_PATH = Path(
    "data/processed/embeddings.npy"
)

METADATA_PATH = Path(
    "data/processed/chunk_metadata.jsonl"
)

INDEX_PATH = Path(
    "data/processed/filings.index"
)


def load_metadata():
    metadata = []

    with METADATA_PATH.open(
        encoding="utf-8"
    ) as file:
        for line in file:
            metadata.append(
                json.loads(line)
            )

    return metadata


def main():
    if not EMBEDDINGS_PATH.exists():
        raise FileNotFoundError(
            f"Missing embeddings: {EMBEDDINGS_PATH}"
        )

    embeddings = np.load(
        EMBEDDINGS_PATH
    ).astype(np.float32)

    metadata = load_metadata()

    if len(embeddings) != len(metadata):
        raise ValueError(
            "Embedding count does not match metadata count."
        )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(embeddings)

    faiss.write_index(
        index,
        str(INDEX_PATH),
    )

    print("=" * 70)
    print(
        f"Vectors indexed: {index.ntotal}"
    )
    print(
        f"Vector dimension: {dimension}"
    )
    print(
        f"Index: {INDEX_PATH}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()