"""Run a real-data held-out-character P300 replication."""

from __future__ import annotations

import argparse
import json

from neurosync_p300.competition_replication import run_subject_a_replication, save_replication_report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True)
    parser.add_argument("--held-out-trials", type=int, default=25)
    parser.add_argument("--repetitions", type=int, default=15)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--min-channels", type=int, default=4)
    parser.add_argument("--max-channels", type=int, default=6)
    parser.add_argument("--sparse-feature-count", type=int, default=0)
    parser.add_argument("--classifier", choices=("diagonal_lda", "spatiotemporal_shrinkage_lda"), default="diagonal_lda")
    parser.add_argument("--output", default="results/competition_iii_replication_subject_a.json")
    args = parser.parse_args()
    report = run_subject_a_replication(
        args.directory, held_out_trials=args.held_out_trials, repetitions=args.repetitions, seed=args.seed,
        min_channels=args.min_channels, max_channels=args.max_channels, sparse_feature_count=args.sparse_feature_count,
        classifier=args.classifier,
    )
    save_replication_report(report, args.output)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
