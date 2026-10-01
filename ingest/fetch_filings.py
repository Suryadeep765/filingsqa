import argparse
import json
from pathlib import Path

from edgar import get_filings, set_identity

from config.settings import SEC_USER_AGENT


TARGET_ITEMS = {
    "Item 1.01",
    "Item 2.01",
    "Item 2.05",
}

OUTPUT_PATH = Path("data/raw/filings.jsonl")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch SEC 8-K filings relevant to FilingsQA."
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Number of candidate 8-K filings to inspect.",
    )

    return parser.parse_args()


def normalize_item_name(item):
    item = item.strip()

    if not item.startswith("Item "):
        item = f"Item {item}"

    return item


def extract_filing(filing):
    eight_k = filing.obj()

    if eight_k is None:
        return None

    available_items = {
        normalize_item_name(item)
        for item in (eight_k.items or [])
    }

    matched_items = sorted(
        available_items & TARGET_ITEMS
    )

    if not matched_items:
        return None

    items = []

    for item_name in matched_items:
        try:
            text = eight_k[item_name]
        except Exception:
            numeric_item = item_name.replace("Item ", "")

            try:
                text = eight_k[numeric_item]
            except Exception:
                text = None

        if not text:
            continue

        items.append(
            {
                "item": item_name,
                "text": text.strip(),
            }
        )

    if not items:
        return None

    accession_number = getattr(
        filing,
        "accession_number",
        getattr(filing, "accession_no", None),
    )

    cik = getattr(filing, "cik", None)

    company_name = getattr(
        filing,
        "company",
        getattr(filing, "company_name", None),
    )

    filing_url = getattr(
        filing,
        "filing_url",
        None,
    )

    return {
        "accession_number": accession_number,
        "cik": str(cik) if cik is not None else None,
        "company_name": company_name,
        "filing_date": str(filing.filing_date),
        "form_type": "8-K",
        "filing_url": filing_url,
        "items": items,
    }


def fetch_filings(limit):
    set_identity(SEC_USER_AGENT)

    filings = get_filings(
        form="8-K",
        amendments=False,
    ).head(limit)

    print(
        f"Retrieved {len(filings)} candidate 8-K filings."
    )

    results = []

    for index, filing in enumerate(filings, start=1):
        try:
            result = extract_filing(filing)

            if result is None:
                continue

            results.append(result)

            matched = [
                item["item"]
                for item in result["items"]
            ]

            print(
                f"[{index}/{len(filings)}] "
                f"{result['company_name']} | "
                f"{result['filing_date']} | "
                f"{matched}"
            )

        except Exception as exc:
            print(
                f"[{index}/{len(filings)}] "
                f"ERROR: {exc}"
            )

    return results


def save_jsonl(records):
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        for record in records:
            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )


def main():
    args = parse_args()

    records = fetch_filings(args.limit)

    save_jsonl(records)

    print()
    print("=" * 70)
    print(f"Relevant filings: {len(records)}")
    print(f"Saved to: {OUTPUT_PATH}")
    print("=" * 70)


if __name__ == "__main__":
    main()