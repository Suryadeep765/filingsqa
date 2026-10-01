import argparse

from api.retrieval import Retriever
from api.generate import Generator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    retriever = Retriever()
    generator = Generator()

    results = retriever.search(args.query, top_k=args.top_k)
    answer = generator.generate(args.query, results)

    print("=" * 80)
    print("QUESTION")
    print("=" * 80)
    print(args.query)

    print()
    print("=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(answer)

    print()
    print("=" * 80)
    print("SOURCES")
    print("=" * 80)

    for rank, result in enumerate(results, start=1):
        print(
            f"[{rank}] "
            f"{result['company_name']} | "
            f"{result['filing_date']} | "
            f"{result['item']} | "
            f"score={result['score']:.4f}"
        )


if __name__ == "__main__":
    main()