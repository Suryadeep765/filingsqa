import argparse

from api.retrieval import Retriever


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "query",
        type=str,
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
    )

    args = parser.parse_args()

    retriever = Retriever()

    results = retriever.search(
        args.query,
        top_k=args.top_k,
    )

    print("=" * 80)
    print(
        f"Query: {args.query}"
    )
    print("=" * 80)

    for rank, result in enumerate(
        results,
        start=1,
    ):
        print(
            f"\n[{rank}] "
            f"Score: {result['score']:.4f}"
        )

        print(
            f"Company: "
            f"{result['company_name']}"
        )

        print(
            f"Date: "
            f"{result['filing_date']}"
        )

        print(
            f"Item: "
            f"{result['item']}"
        )

        print(
            f"Accession: "
            f"{result['accession_number']}"
        )

        print()

        print(
            result["text"][:1000]
        )


if __name__ == "__main__":
    main()