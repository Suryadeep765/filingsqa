import json
from pathlib import Path

from api.retrieval import Retriever


GOLDEN_SET_PATH = Path("eval/golden_set.jsonl")
RESULTS_PATH = Path("results/retrieval_results.jsonl")


def load_golden_set():
    records = []

    with GOLDEN_SET_PATH.open(encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    return records


def reciprocal_rank(results, expected_accession):
    for rank, result in enumerate(results, start=1):
        if result["accession_number"] == expected_accession:
            return 1.0 / rank

    return 0.0


def main():
    golden_set = load_golden_set()
    retriever = Retriever()

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    hit_at_1 = 0
    hit_at_3 = 0
    hit_at_5 = 0
    reciprocal_ranks = []

    with RESULTS_PATH.open("w", encoding="utf-8") as output_file:
        for case in golden_set:
            results = retriever.search(
                case["question"],
                top_k=5,
            )

            ranks = [
                rank
                for rank, result in enumerate(results, start=1)
                if result["accession_number"] == case["expected_accession"]
            ]

            rank = ranks[0] if ranks else None

            if rank == 1:
                hit_at_1 += 1

            if rank is not None and rank <= 3:
                hit_at_3 += 1

            if rank is not None and rank <= 5:
                hit_at_5 += 1

            rr = reciprocal_rank(
                results,
                case["expected_accession"],
            )

            reciprocal_ranks.append(rr)

            record = {
                "id": case["id"],
                "question": case["question"],
                "expected_accession": case["expected_accession"],
                "retrieved_rank": rank,
                "reciprocal_rank": rr,
                "results": [
                    {
                        "rank": result_rank,
                        "company_name": result["company_name"],
                        "accession_number": result["accession_number"],
                        "score": result["score"],
                    }
                    for result_rank, result in enumerate(results, start=1)
                ],
            }

            output_file.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )

            print(
                f"{case['id']} | "
                f"rank={rank} | "
                f"RR={rr:.3f} | "
                f"{case['question']}"
            )

    total = len(golden_set)

    if total == 0:
        raise ValueError("Golden set is empty.")

    mean_reciprocal_rank = sum(reciprocal_ranks) / total

    print()
    print("=" * 70)
    print("RETRIEVAL EVALUATION")
    print("=" * 70)
    print(f"Questions: {total}")
    print(f"Hit@1:    {hit_at_1 / total:.3f}")
    print(f"Hit@3:    {hit_at_3 / total:.3f}")
    print(f"Hit@5:    {hit_at_5 / total:.3f}")
    print(f"MRR:      {mean_reciprocal_rank:.3f}")
    print(f"Results:  {RESULTS_PATH}")
    print("=" * 70)


if __name__ == "__main__":
    main()