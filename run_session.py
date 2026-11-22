"""Train on one Neurosync NPZ recording and decode another."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from neurosync_p300.data import load_npz
from neurosync_p300.decoder import DecoderConfig
from neurosync_p300.session import train_and_decode


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, help="training .npz file")
    parser.add_argument("--test", required=True, help="held-out .npz file")
    parser.add_argument("--output", default="results/session_results.json")
    parser.add_argument("--fixed-repetitions", type=int, default=None)
    args = parser.parse_args()

    train = load_npz(args.train)
    test = load_npz(args.test)
    result = train_and_decode(
        train,
        test,
        decoder_config=DecoderConfig(),
        fixed_repetitions=args.fixed_repetitions,
    )
    payload = {
        "selected_channels": result.selection.names,
        "selection_cv_balanced_accuracy": result.selection.cross_validated_balanced_accuracy,
        "metrics": result.metrics,
        "temperature_calibration": result.calibration.__dict__ if result.calibration else None,
        "decoded_trials": [trial.__dict__ for trial in result.decoded],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"selected_channels": result.selection.names, "metrics": result.metrics}, indent=2))


if __name__ == "__main__":
    main()

