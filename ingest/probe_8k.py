from edgar import get_filings, set_identity

from config.settings import SEC_USER_AGENT

set_identity(SEC_USER_AGENT)

TARGET_ITEMS = {
    "Item 1.01",
    "Item 2.01",
    "Item 2.05",
}

filings = get_filings(
    form="8-K",
    amendments=False,
).head(25)

print(f"Retrieved {len(filings)} candidate 8-K filings\n")

matches = 0

for filing in filings:
    try:
        eight_k = filing.obj()

        if eight_k is None:
            continue

        items = set(eight_k.items or [])
        matched_items = sorted(items & TARGET_ITEMS)

        if matched_items:
            matches += 1

            print("=" * 80)
            print(f"Company: {getattr(filing, 'company', None)}")
            print(f"Date: {filing.filing_date}")
            print(f"Accession: {getattr(filing, 'accession_number', getattr(filing, 'accession_no', None))}")
            print(f"Items: {matched_items}")

            for item in matched_items:
                content = eight_k[item]

                if content:
                    print(f"\n--- {item} ---")
                    print(content[:500].replace("\n", " "))

            print()

    except Exception as exc:
        print(f"ERROR processing {filing}: {exc}")

print("=" * 80)
print(f"Matched filings: {matches}/{len(filings)}")