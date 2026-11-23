"""Run the official-split NeuroSync benchmark on all BNCI 2014-008 ALS subjects."""

from __future__ import annotations

import argparse
import json

from neurosync_p300.bnci_008_benchmark import benchmark_cohort, save_report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True)
    parser.add_argument("--output", default="results/bnci_008_cohort.json")
    args = parser.parse_args()
    report = benchmark_cohort(args.directory)
    save_report(report, args.output)
    print(json.dumps(report["cohort_summary"], indent=2))


if __name__ == "__main__":
    main()
