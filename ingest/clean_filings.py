import json
from pathlib import Path

from ingest.clean import clean_text


INPUT_PATH = Path("data/raw/filings.jsonl")
OUTPUT_PATH = Path("data/processed/cleaned_filings.jsonl")


def clean_filings():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}"
        )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    count = 0

    with (
        INPUT_PATH.open(
            encoding="utf-8"
        ) as input_file,
        OUTPUT_PATH.open(
            "w",
            encoding="utf-8"
        ) as output_file,
    ):
        for line in input_file:
            filing = json.loads(line)

            for item in filing["items"]:
                item["text"] = clean_text(
                    item["text"]
                )

            output_file.write(
                json.dumps(
                    filing,
                    ensure_ascii=False,
                )
                + "\n"
            )

            count += 1

    print(f"Cleaned {count} filings.")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    clean_filings()