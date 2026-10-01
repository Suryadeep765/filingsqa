import json
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


INDEX_PATH = Path(
    "data/processed/filings.index"
)

METADATA_PATH = Path(
    "data/processed/chunk_metadata.jsonl"
)

MODEL_NAME = "BAAI/bge-small-en-v1.5"


class Retriever:

    def __init__(
        self,
        index_path=INDEX_PATH,
        metadata_path=METADATA_PATH,
        model_name=MODEL_NAME,
    ):
        self.index = faiss.read_index(
            str(index_path)
        )

        self.model = SentenceTransformer(
            model_name
        )

        self.metadata = []

        with metadata_path.open(
            encoding="utf-8"
        ) as file:
            for line in file:
                self.metadata.append(
                    json.loads(line)
                )

    def search(
        self,
        query,
        top_k=5,
    ):
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        )

        scores, indices = self.index.search(
            query_embedding,
            top_k,
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):
            if index < 0:
                continue

            result = dict(
                self.metadata[index]
            )

            result["score"] = float(
                score
            )

            results.append(result)

        return results