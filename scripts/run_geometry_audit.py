"""Audit a measured forward model under every single-electrode dropout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from neurosync_p300.data import load_npz
from neurosync_p300.forward_model import load_forward_model
from neurosync_p300.geometry import audit_single_channel_dropout


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calibration", required=True, help="calibration EEGDataset NPZ")
    parser.add_argument("--forward-model", required=True, help="BEM/FEM forward-model NPZ")
    parser.add_argument("--output", default="results/geometry_dropout_audit.json")
    args = parser.parse_args()

    dataset = load_npz(args.calibration)
    model = load_forward_model(args.forward_model)
    leadfield = model.align(dataset.channel_names)
    baseline_samples = max(2, int(round(0.2 * dataset.sampling_rate)))
    baseline = dataset.epochs[..., :baseline_samples].transpose(1, 0, 2).reshape(dataset.n_channels, -1)
    covariance = np.cov(baseline)
    report = audit_single_channel_dropout(
        leadfield,
        covariance,
        dataset.channel_names,
        target_indices=list(model.target_indices),
        artifact_indices=list(model.artifact_indices) or None,
    )
    payload = {
        "forward_model_provenance": model.provenance,
        "claim_boundary": "Conditional geometry diagnostic; not a decoding or clinical-performance result.",
        **report,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
