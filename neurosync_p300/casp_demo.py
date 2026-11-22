"""Run the contact-aware NeuroSync CASP engineering demonstration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .decoder import DecoderConfig
from .session import train_and_decode
from .synthetic import generate_synthetic_dataset, inject_contact_artifacts


def run_casp_demo(*, output_dir: str | Path, seed: int = 23) -> dict:
    """Compare ordinary decoding with CASP on deliberately corrupted dry EEG.

    The result is intentionally labelled simulated: it checks whether the
    software changes its action when signal quality drops; it does not validate
    a hardware headset or clinical performance.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    train = generate_synthetic_dataset(n_trials=80, repetitions=6, electrode_type="dry", seed=seed)
    clean_test = generate_synthetic_dataset(n_trials=40, repetitions=6, electrode_type="dry", seed=seed + 1)
    corrupted_test = inject_contact_artifacts(
        clean_test,
        fraction=0.22,
        seed=seed + 2,
        by_trial=True,
        all_channels=True,
    )
    config = DecoderConfig(
        min_repetitions=2,
        max_repetitions=6,
        confidence_threshold=0.72,
        margin_threshold=0.18,
        stability_repetitions=2,
        temperature=4.0,
        minimum_epoch_quality=0.45,
        reseat_after_bad_repetitions=2,
    )
    ordinary = train_and_decode(train, corrupted_test, decoder_config=config, contact_aware=False)
    casp = train_and_decode(train, corrupted_test, decoder_config=config, contact_aware=True, quality_weighting=False)
    clean_casp = train_and_decode(train, clean_test, decoder_config=config, contact_aware=True, quality_weighting=False)
    payload = {
        "project": "NeuroSync CASP",
        "simulated_only": True,
        "central_question": "Can contact-aware sparse decoding preserve accepted-output performance while refusing artifact-heavy data?",
        "selected_channels": casp.selection.names,
        "artifact_fraction": 0.22,
        "ordinary_decoder_on_corrupted_dry": ordinary.metrics,
        "casp_on_corrupted_dry": casp.metrics,
        "casp_on_clean_dry": clean_casp.metrics,
        "interpretation": [
            "CASP is designed to change its action when calibrated signal-quality metrics are poor.",
            "This is a synthetic stress test, not evidence of dry-headset or ALS performance.",
            "The central question remains unanswered until a pre-registered wet-versus-dry held-out human study is completed.",
        ],
    }
    (output_dir / "casp_results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_summary(output_dir / "casp_summary.md", payload)
    return payload


def _write_summary(path: Path, report: dict) -> None:
    rows = [
        "# NeuroSync CASP simulated stress test",
        "",
        "> Synthetic engineering result only. It does not establish human, ALS, or clinical performance.",
        "",
        f"- Selected channels: `{', '.join(report['selected_channels'])}`",
        f"- Injected artifact fraction: `{report['artifact_fraction']:.0%}` of flash epochs",
        "",
        "| Configuration | Overall accuracy | Accepted accuracy | Coverage | Re-seat rate | Reject rate |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name in ("ordinary_decoder_on_corrupted_dry", "casp_on_corrupted_dry", "casp_on_clean_dry"):
        metric = report[name]
        rows.append(
            f"| {name} | {metric['accuracy']:.3f} | {metric['accepted_accuracy']:.3f} | "
            f"{metric['coverage']:.3f} | {metric['reseat_rate']:.3f} | {metric['reject_rate']:.3f} |"
        )
    rows += [
        "",
        "CASP only accepts a selection after evidence, stability, and quality gates pass. It requests a headset re-seat after repeated low-quality repetitions.",
    ]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="results/casp_demo")
    parser.add_argument("--seed", type=int, default=23)
    args = parser.parse_args()
    print(json.dumps(run_casp_demo(output_dir=args.output_dir, seed=args.seed), indent=2))


if __name__ == "__main__":
    main()
