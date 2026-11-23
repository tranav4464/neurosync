"""Run the file-disjoint bigP3BCI event-detection benchmark."""

from __future__ import annotations

import argparse
import json

from neurosync_p300.bigp3bci_benchmark import benchmark_cohort, benchmark_recording_pair, save_report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train")
    parser.add_argument("--test")
    parser.add_argument(
        "--pair", action="append", nargs=2, metavar=("TRAIN", "TEST"),
        help="repeat for a predeclared cohort of file-disjoint recording pairs",
    )
    parser.add_argument("--output", default="results/bigp3bci_pair.json")
    parser.add_argument("--selection-method", choices=("forward", "stability"), default="forward")
    args = parser.parse_args()
    if args.pair:
        if args.train or args.test:
            parser.error("use either --pair or --train/--test")
        report = benchmark_cohort(args.pair, selection_method=args.selection_method)
    else:
        if not args.train or not args.test:
            parser.error("--train and --test are required when --pair is absent")
        report = benchmark_recording_pair(args.train, args.test, selection_method=args.selection_method)
    save_report(report, args.output)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
