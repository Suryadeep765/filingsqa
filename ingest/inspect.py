import json

from pathlib import Path


path = Path("data/raw/filings.jsonl")

with path.open(encoding="utf-8") as file:
    for line in file:
        filing = json.loads(line)

        print("=" * 80)
        print(f"Company: {filing['company_name']}")
        print(f"Date: {filing['filing_date']}")
        print(f"Accession: {filing['accession_number']}")
        print(
            f"Items: "
            f"{[item['item'] for item in filing['items']]}"
        )

        for item in filing["items"]:
            print(f"\n--- {item['item']} ---")
            print(item["text"][:1000])

        print()