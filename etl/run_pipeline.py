"""Pipeline orchestrator: extract -> validate -> transform -> load -> brief.

Usage:
    python -m etl.run_pipeline                # full run
    python -m etl.run_pipeline --skip-extract # reuse raw files already on disk
    python -m etl.run_pipeline --skip-brief   # skip the Bedrock executive brief
"""

import argparse

from etl import brief, extract, load, transform, validate


def main() -> None:
    parser = argparse.ArgumentParser(description="Debt Cycle BI Tracker pipeline")
    parser.add_argument("--skip-extract", action="store_true", help="reuse files in data/raw/fred")
    parser.add_argument("--skip-brief", action="store_true", help="skip the LLM executive brief")
    args = parser.parse_args()

    if not args.skip_extract:
        print("[1/5] Extract (FRED API)")
        extract.run()
    else:
        print("[1/5] Extract skipped")

    print("[2/5] Validate (data-quality gate)")
    frames = validate.run()

    print("[3/5] Transform (star schema + marts)")
    tables = transform.run(frames)

    print("[4/5] Load (PostgreSQL)")
    load.run(tables)

    if not args.skip_brief:
        print("[5/5] Executive brief (Claude on Bedrock)")
        brief.run()
    else:
        print("[5/5] Brief skipped")

    print("Pipeline complete.")


if __name__ == "__main__":
    main()
