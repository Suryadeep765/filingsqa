import subprocess
import sys


def run_step(module):
    subprocess.run(
        [sys.executable, "-m", module],
        check=True,
    )


def ingest_filings(limit):
    run_step_with_limit = [
        sys.executable,
        "-m",
        "ingest.fetch_filings",
        "--limit",
        str(limit),
    ]

    subprocess.run(run_step_with_limit, check=True)

    for module in [
        "ingest.clean_filings",
        "ingest.chunk",
        "ingest.embed",
        "ingest.build_index",
    ]:
        run_step(module)
