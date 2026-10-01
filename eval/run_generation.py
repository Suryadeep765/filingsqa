import json
import time
from pathlib import Path

from api.retrieval import Retriever
from api.generate import Generator


GOLDEN_SET_PATH = Path("eval/golden_set.jsonl")
RESULTS_PATH = Path("results/generation_results.jsonl")


def load_golden_set():
    records = []

    with GOLDEN_SET_PATH.open(encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    return records


def main():
    golden_set = load_golden_set()

    retriever = Retriever()
    generator = Generator()

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    latencies = []

    with RESULTS_PATH.open("w", encoding="utf-8") as output_file:
        for index, case in enumerate(golden_set, start=1):
            start = time.perf_counter()

            results = retriever.search(
                case["question"],
                top_k=5,
            )

            answer = generator.generate(
                case["question"],
                results,
            )

            latency = time.perf_counter() - start
            latencies.append(latency)

            record = {
                "id": case["id"],
                "question": case["question"],
                "expected_answer": case["expected_answer"],
                "generated_answer": answer,
                "retrieved_rank": next(
                    (
                        rank
                        for rank, result in enumerate(results, start=1)
                        if result["accession_number"]
                        == case["expected_accession"]
                    ),
                    None,
                ),
                "latency_seconds": latency,
                "sources": [
                    {
                        "company_name": result["company_name"],
                        "accession_number": result["accession_number"],
                        "score": result["score"],
                    }
                    for result in results
                ],
            }

            output_file.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )

            print()
            print(f"[{index}/{len(golden_set)}] {case['id']}")
            print(f"Question: {case['question']}")
            print(f"Expected: {case['expected_answer']}")
            print(f"Answer:   {answer}")
            print(f"Latency:  {latency:.2f}s")

    latencies.sort()

    p50_index = int(0.50 * (len(latencies) - 1))
    p95_index = int(0.95 * (len(latencies) - 1))

    p50 = latencies[p50_index]
    p95 = latencies[p95_index]

    print()
    print("=" * 70)
    print("GENERATION EVALUATION")
    print("=" * 70)
    print(f"Questions:        {len(golden_set)}")
    print(f"Median latency:   {p50:.3f}s")
    print(f"P95 latency:      {p95:.3f}s")
    print(f"Results:          {RESULTS_PATH}")
    print("=" * 70)


if __name__ == "__main__":
    main()