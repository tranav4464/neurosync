"""Multi-seed synthetic evaluation for regression testing CASP decisions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .benchmark import benchmark_wet_reference_vs_casp
from .decoder import DecoderConfig
from .session import train_and_decode
from .synthetic import DEFAULT_SYMBOLS, generate_synthetic_dataset, inject_contact_artifacts


def _average(records: list[dict], key: str) -> dict[str, float]:
    metrics = [record[key] for record in records]
    numeric_keys = sorted({name for metric in metrics for name, value in metric.items() if isinstance(value, (int, float))})
    return {name: float(np.mean([metric[name] for metric in metrics if name in metric])) for name in numeric_keys}


def run_evaluation_suite(
    *,
    output_dir: str | Path,
    runs: int = 8,
    seed: int = 101,
    train_trials: int = 48,
    test_trials: int = 24,
    repetitions: int = 6,
    spatial_filter_components: int = 0,
    sparse_feature_count: int = 0,
) -> dict:
    """Run matched synthetic wet/dry and contact-failure stress comparisons.

    This is a regression/evaluation suite for code changes. It intentionally
    does not transform synthetic outcomes into a clinical claim.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    target_rng = np.random.default_rng(seed)
    if repetitions < 2:
        raise ValueError("repetitions must be at least 2")
    config = DecoderConfig(max_repetitions=repetitions, temperature=4.0, confidence_threshold=0.72, margin_threshold=0.18)
    for run in range(runs):
        run_seed = seed + run * 11
        train_targets = target_rng.choice(DEFAULT_SYMBOLS, size=train_trials, replace=True).tolist()
        test_targets = target_rng.choice(DEFAULT_SYMBOLS, size=test_trials, replace=True).tolist()
        wet_train = generate_synthetic_dataset(n_trials=train_trials, repetitions=repetitions, electrode_type="wet", seed=run_seed, targets=train_targets)
        dry_train = generate_synthetic_dataset(n_trials=train_trials, repetitions=repetitions, electrode_type="dry", seed=run_seed + 1, targets=train_targets)
        wet_test = generate_synthetic_dataset(n_trials=test_trials, repetitions=repetitions, electrode_type="wet", seed=run_seed + 2, targets=test_targets)
        dry_test = generate_synthetic_dataset(n_trials=test_trials, repetitions=repetitions, electrode_type="dry", seed=run_seed + 3, targets=test_targets)
        paired = benchmark_wet_reference_vs_casp(
            wet_train,
            wet_test,
            dry_train,
            dry_test,
            fixed_repetitions=repetitions,
            noninferiority_margin=0.05,
            spatial_filter_components=spatial_filter_components,
            sparse_feature_count=sparse_feature_count,
        )
        corrupted = inject_contact_artifacts(dry_test, fraction=0.25, seed=run_seed + 4, by_trial=True, all_channels=True)
        ordinary = train_and_decode(dry_train, corrupted, decoder_config=config, contact_aware=False)
        casp = train_and_decode(dry_train, corrupted, decoder_config=config, contact_aware=True)
        records.append({
            "seed": run_seed,
            "paired": paired,
            "ordinary_corrupted": ordinary.metrics,
            "casp_corrupted": casp.metrics,
        })

    paired_conclusions = [record["paired"]["noninferiority"]["conclusion"] for record in records]
    report = {
        "simulated_only": True,
        "runs": runs,
        "train_trials_per_run": train_trials,
        "test_trials_per_run": test_trials,
        "repetitions_per_trial": repetitions,
        "spatial_filter_components": spatial_filter_components,
        "sparse_feature_count": sparse_feature_count,
        "central_question": "Can sparse CASP be non-inferior to a wet reference without unsafe false accepts?",
        "paired_summary": {
            "reference_safe_metrics": _average([{"value": record["paired"]["reference"]["safe_metrics"]} for record in records], "value"),
            "casp_safe_metrics": _average([{"value": record["paired"]["casp"]["safe_metrics"]} for record in records], "value"),
            "mean_correct_accept_rate_difference": float(np.mean([record["paired"]["noninferiority"]["candidate_minus_reference"] for record in records])),
            "noninferior_runs": int(sum(item == "NON_INFERIOR" for item in paired_conclusions)),
        },
        "corrupted_contact_summary": {
            "ordinary": _average(records, "ordinary_corrupted"),
            "casp": _average(records, "casp_corrupted"),
        },
        "per_run": records,
        "interpretation": [
            "This suite is a software regression test over synthetic signal assumptions, not clinical evidence.",
            "A sparse method must be judged on correct accepted outputs and wrong accepted outputs, not accuracy alone.",
            "A low re-seat rate in this simulation does not validate a real headset; real contact/impedance data are required.",
        ],
    }
    (output_dir / "evaluation_results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    _write_summary(output_dir / "evaluation_summary.md", report)
    return report


def _write_summary(path: Path, report: dict) -> None:
    paired = report["paired_summary"]
    corrupted = report["corrupted_contact_summary"]
    lines = [
        "# NeuroSync CASP synthetic evaluation suite",
        "",
        "> This is a multi-seed software evaluation using synthetic EEG. It is not human, ALS, hardware, or clinical evidence.",
        "",
        f"- Runs: `{report['runs']}`",
        f"- Per run: `{report['train_trials_per_run']}` train and `{report['test_trials_per_run']}` matched test trials; `{report['repetitions_per_trial']}` repetitions per symbol",
        f"- Paired non-inferior runs: `{paired['noninferior_runs']}/{report['runs']}`",
        f"- Mean sparse-minus-wet correct-accept-rate difference: `{paired['mean_correct_accept_rate_difference']:.3f}`",
        "",
        "| Scenario | Correct-accept rate | Wrong-accept rate | Coverage | Re-seat rate |",
        "|---|---:|---:|---:|---:|",
        f"| Wet reference | {paired['reference_safe_metrics']['correct_accept_rate']:.3f} | {paired['reference_safe_metrics']['wrong_accept_rate']:.3f} | {paired['reference_safe_metrics']['coverage']:.3f} | {paired['reference_safe_metrics']['reseat_rate']:.3f} |",
        f"| Sparse CASP, clean dry | {paired['casp_safe_metrics']['correct_accept_rate']:.3f} | {paired['casp_safe_metrics']['wrong_accept_rate']:.3f} | {paired['casp_safe_metrics']['coverage']:.3f} | {paired['casp_safe_metrics']['reseat_rate']:.3f} |",
        f"| Ordinary decoder, corrupted dry | {corrupted['ordinary']['accept_rate'] * corrupted['ordinary']['accepted_accuracy']:.3f} | {corrupted['ordinary']['accept_rate'] * (1 - corrupted['ordinary']['accepted_accuracy']):.3f} | {corrupted['ordinary']['coverage']:.3f} | {corrupted['ordinary']['reseat_rate']:.3f} |",
        f"| CASP, corrupted dry | {corrupted['casp']['accept_rate'] * corrupted['casp']['accepted_accuracy']:.3f} | {corrupted['casp']['accept_rate'] * (1 - corrupted['casp']['accepted_accuracy']):.3f} | {corrupted['casp']['coverage']:.3f} | {corrupted['casp']['reseat_rate']:.3f} |",
        "",
        "## Interpretation",
        "",
        "The synthetic suite is designed to reveal safety/coverage trade-offs. A result is useful only if it survives a matched held-out human session with real amplifier markers and measured electrode contact quality.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="results/evaluation")
    parser.add_argument("--runs", type=int, default=8)
    parser.add_argument("--seed", type=int, default=101)
    parser.add_argument("--train-trials", type=int, default=48)
    parser.add_argument("--test-trials", type=int, default=24)
    parser.add_argument("--repetitions", type=int, default=6)
    parser.add_argument("--spatial-filter-components", type=int, default=0, help="0 disables; 2-3 enables the prototype spatial-filter ablation")
    parser.add_argument("--sparse-feature-count", type=int, default=0, help="0 disables; otherwise retains this many training-selected features")
    args = parser.parse_args()
    print(json.dumps(run_evaluation_suite(
        output_dir=args.output_dir,
        runs=args.runs,
        seed=args.seed,
        train_trials=args.train_trials,
        test_trials=args.test_trials,
        repetitions=args.repetitions,
        spatial_filter_components=args.spatial_filter_components,
        sparse_feature_count=args.sparse_feature_count,
    ), indent=2))


if __name__ == "__main__":
    main()
