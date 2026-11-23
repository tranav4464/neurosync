"""Run the file-disjoint bigP3BCI event-detection benchmark."""

from __future__ import annotations

import argparse
import json

from neurosync_p300.bigp3bci_benchmark import benchmark_recording_pair, save_report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True)
    parser.add_argument("--test", required=True)
    parser.add_argument("--output", default="results/bigp3bci_pair.json")
    args = parser.parse_args()
    report = benchmark_recording_pair(args.train, args.test)
    save_report(report, args.output)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
