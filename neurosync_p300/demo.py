"""Run the reproducible Neurosync milestone demonstration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .channel_selection import forward_select_channels
from .decoder import DecoderConfig, decode_dataset, summarize_decoding
from .features import extract_features
from .model import DiagonalLDA
from .preprocessing import preprocess_epochs
from .synthetic import generate_synthetic_dataset


def _fit_and_score(train, test, channel_indices, *, fixed_repetitions=None, config=None):
    train_clean = preprocess_epochs(train.epochs, train.sampling_rate)
    test_clean = preprocess_epochs(test.epochs, test.sampling_rate)
    train_features = extract_features(train_clean[:, channel_indices, :], train.sampling_rate)
    test_features = extract_features(test_clean[:, channel_indices, :], test.sampling_rate)
    model = DiagonalLDA(shrinkage=0.20).fit(train_features, train.labels)
    results = decode_dataset(
        model,
        test_features,
        test,
        config=config,
        fixed_repetitions=fixed_repetitions,
    )
    return summarize_decoding(results)


def run_demo(*, output_dir: str | Path, seed: int = 7, n_train_trials: int = 80, n_test_trials: int = 40) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    symbols = list("ABCDEF")

    wet_train = generate_synthetic_dataset(
        n_trials=n_train_trials, symbols=symbols, electrode_type="wet", seed=seed
    )
    wet_test = generate_synthetic_dataset(
        n_trials=n_test_trials, symbols=symbols, electrode_type="wet", seed=seed + 1
    )
    dry_train = generate_synthetic_dataset(
        n_trials=n_train_trials, symbols=symbols, electrode_type="dry", seed=seed + 2
    )
    dry_test = generate_synthetic_dataset(
        n_trials=n_test_trials, symbols=symbols, electrode_type="dry", seed=seed + 3
    )

    dry_clean = preprocess_epochs(dry_train.epochs, dry_train.sampling_rate)
    selection = forward_select_channels(
        dry_clean,
        dry_train.labels,
        dry_train.trial_ids,
        dry_train.channel_names,
        dry_train.sampling_rate,
        min_channels=4,
        max_channels=6,
        seed=seed,
    )
    full_channels = list(range(wet_train.n_channels))
    selected_channels = selection.indices
    adaptive = DecoderConfig(
        min_repetitions=2,
        max_repetitions=6,
        confidence_threshold=0.72,
        margin_threshold=0.18,
        temperature=4.0,
    )

    metrics = {
        "wet_8ch_fixed_6rep": _fit_and_score(wet_train, wet_test, full_channels, fixed_repetitions=6),
        "dry_8ch_fixed_6rep": _fit_and_score(dry_train, dry_test, full_channels, fixed_repetitions=6),
        "dry_selected_fixed_6rep": _fit_and_score(dry_train, dry_test, selected_channels, fixed_repetitions=6),
        "dry_selected_adaptive": _fit_and_score(dry_train, dry_test, selected_channels, config=adaptive),
    }

    report = {
        "project": "Neurosync P300 low-channel speller",
        "seed": seed,
        "software_only": True,
        "train_trials": n_train_trials,
        "test_trials": n_test_trials,
        "symbols": symbols,
        "channels_available": dry_train.channel_names,
        "selected_channels": selection.names,
        "channel_selection_cv_balanced_accuracy": selection.cross_validated_balanced_accuracy,
        "channel_selection_history": selection.history,
        "metrics": metrics,
        "interpretation": [
            "The synthetic demo checks the software path and expected trade-offs; it is not human or ALS evidence.",
            "Adaptive stopping is allowed to end early only when confidence and top-two margin both pass thresholds.",
            "Real claims require pre-registered held-out recordings, artifact checks, and testing with ALS participants under ethics approval.",
        ],
    }
    (output_dir / "demo_results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    _write_summary(output_dir / "demo_summary.md", report)
    return report


def _write_summary(path: Path, report: dict) -> None:
    lines = [
        "# Neurosync P300 demo results",
        "",
        "> These are deterministic synthetic-data engineering results. They must not be presented as patient, clinical, or human-subject results.",
        "",
        f"- Seed: `{report['seed']}`",
        f"- Training trials: `{report['train_trials']}`; test trials: `{report['test_trials']}`",
        f"- Selected channels: `{', '.join(report['selected_channels'])}`",
        f"- Selection cross-validated balanced accuracy: `{report['channel_selection_cv_balanced_accuracy']:.3f}`",
        "",
        "| Configuration | Accuracy | Mean repetitions | Early-stop rate | Mean confidence |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, metrics in report["metrics"].items():
        lines.append(
            f"| {name} | {metrics['accuracy']:.3f} | {metrics['mean_repetitions']:.2f} | "
            f"{metrics['early_stop_rate']:.3f} | {metrics['mean_confidence']:.3f} |"
        )
    lines += [
        "",
        "## Algorithm",
        "",
        "1. Baseline-correct each epoch and apply a 0.5–20 Hz FFT band-limit.",
        "2. Extract the 250–600 ms post-flash response window.",
        "3. Select 4–6 channels by forward selection with trial-level cross-validation.",
        "4. Fit regularized diagonal LDA for target versus non-target flashes.",
        "5. Accumulate classifier evidence by symbol and stop early only when confidence and top-two margin are both high.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="results/demo", help="directory for JSON and Markdown outputs")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--train-trials", type=int, default=80)
    parser.add_argument("--test-trials", type=int, default=40)
    args = parser.parse_args()
    report = run_demo(
        output_dir=args.output_dir,
        seed=args.seed,
        n_train_trials=args.train_trials,
        n_test_trials=args.test_trials,
    )
    print(json.dumps({"selected_channels": report["selected_channels"], "metrics": report["metrics"]}, indent=2))


if __name__ == "__main__":
    main()

