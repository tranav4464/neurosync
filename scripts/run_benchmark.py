"""Run the paired wet-reference versus sparse-CASP engineering benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from neurosync_p300.benchmark import benchmark_wet_reference_vs_casp
from neurosync_p300.data import load_npz


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wet-train", required=True)
    parser.add_argument("--wet-test", required=True)
    parser.add_argument("--sparse-train", required=True, help="dry or semi-dry training NPZ")
    parser.add_argument("--sparse-test", required=True, help="dry or semi-dry matched-test NPZ")
    parser.add_argument("--fixed-repetitions", type=int, default=6)
    parser.add_argument("--margin", type=float, default=0.05)
    parser.add_argument("--output", default="results/paired_benchmark.json")
    args = parser.parse_args()

    report = benchmark_wet_reference_vs_casp(
        load_npz(args.wet_train),
        load_npz(args.wet_test),
        load_npz(args.sparse_train),
        load_npz(args.sparse_test),
        fixed_repetitions=args.fixed_repetitions,
        noninferiority_margin=args.margin,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
