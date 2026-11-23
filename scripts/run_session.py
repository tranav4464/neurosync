"""Train on one Neurosync NPZ recording and decode another."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from neurosync_p300.data import load_npz
from neurosync_p300.decoder import DecoderConfig
from neurosync_p300.forward_model import load_forward_model
from neurosync_p300.session import train_and_decode


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, help="training .npz file")
    parser.add_argument("--test", required=True, help="held-out .npz file")
    parser.add_argument("--output", default="results/session_results.json")
    parser.add_argument("--fixed-repetitions", type=int, default=None)
    parser.add_argument(
        "--forward-model",
        default=None,
        help="optional validated channels x sources NPZ exported from a BEM/FEM workflow",
    )
    args = parser.parse_args()

    train = load_npz(args.train)
    test = load_npz(args.test)
    forward_model = load_forward_model(args.forward_model) if args.forward_model else None
    result = train_and_decode(
        train,
        test,
        decoder_config=DecoderConfig(),
        fixed_repetitions=args.fixed_repetitions,
        forward_model=forward_model,
    )
    payload = {
        "selected_channels": result.selection.names,
        "selection_cv_balanced_accuracy": result.selection.cross_validated_balanced_accuracy,
        "selection_objective_score": result.selection.objective_score,
        "geometry_source": result.selection.geometry_source,
        "selection_history": result.selection.history,
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

