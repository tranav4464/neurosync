"""Official-split character benchmark for BNCI 2014-008."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .bnci_008_data import MATRIX, load_bnci_008_mat
from .channel_selection import forward_select_channels
from .competition_replication import _subset
from .features import extract_features
from .model import DiagonalLDA, ShrinkageLDA
from .preprocessing import preprocess_epochs


def _decode(scores: np.ndarray, dataset, targets: list[str], repetitions: int) -> float:
    correct = []
    for trial in np.unique(dataset.trial_ids):
        mask = (dataset.trial_ids == trial) & (dataset.repetitions <= repetitions)
        codes = dataset.symbols[mask].astype(int)
        values = scores[mask]
        evidence = {code: float(values[codes == code].sum()) for code in range(1, 13)}
        row = max(range(1, 7), key=evidence.get)
        column = max(range(7, 13), key=evidence.get)
        prediction = MATRIX[row - 1][column - 7]
        correct.append(prediction == targets[int(trial)])
    return float(np.mean(correct))


def benchmark_subject(path: str | Path, *, channel_counts=(4, 6, 8), repetitions=(1, 3, 5, 10)) -> dict:
    dataset = load_bnci_008_mat(path)
    train_ids = np.asarray(dataset.metadata["official_calibration_trials"])
    test_ids = np.asarray(dataset.metadata["official_feedback_trials"])
    train, test = _subset(dataset, train_ids), _subset(dataset, test_ids)
    train_clean = preprocess_epochs(train.epochs, train.sampling_rate)
    test_clean = preprocess_epochs(test.epochs, test.sampling_rate)
    results = []
    for count in channel_counts:
        selection = forward_select_channels(
            train_clean, train.labels, train.trial_ids, train.channel_names, train.sampling_rate,
            min_channels=count, max_channels=count,
        )
        selected_train = train_clean[:, selection.indices]
        selected_test = test_clean[:, selection.indices]
        baseline_train = extract_features(selected_train, train.sampling_rate)
        baseline_test = extract_features(selected_test, test.sampling_rate)
        baseline_model = DiagonalLDA(shrinkage=0.20).fit(baseline_train, train.labels)
        og_train = extract_features(
            selected_train, train.sampling_rate, window_seconds=(0.10, 0.80), downsample=8
        )
        og_test = extract_features(
            selected_test, test.sampling_rate, window_seconds=(0.10, 0.80), downsample=8
        )
        og_model = ShrinkageLDA(shrinkage=0.10).fit(og_train, train.labels)
        method_scores = {
            "diagonal_lda_baseline": baseline_model.decision_function(baseline_test),
            "spatiotemporal_shrinkage_lda": og_model.decision_function(og_test),
        }
        results.append({
            "channels": count,
            "selected_channels": selection.names,
            "selection_cv_balanced_accuracy": selection.cross_validated_balanced_accuracy,
            "methods": {
                method: {
                    "character_accuracy_by_repetition": {
                        str(rep): _decode(scores, test, dataset.metadata["target_characters"], rep)
                        for rep in repetitions
                    }
                }
                for method, scores in method_scores.items()
            },
        })
    return {
        "dataset": "BNCI 2014-008",
        "subject": Path(path).stem,
        "population": "ALS",
        "train_characters": len(train_ids),
        "held_out_feedback_characters": len(test_ids),
        "protocol": "official first-15 calibration / final-20 feedback split",
        "claim_boundary": "Public active-electrode ALS data; not dry-electrode, prospective, or wet-reference evidence.",
        "results": results,
    }


def benchmark_cohort(directory: str | Path) -> dict:
    paths = sorted(Path(directory).glob("A*.mat"))
    if not paths:
        raise FileNotFoundError("no A*.mat files found")
    subjects = [benchmark_subject(path) for path in paths]
    summary = {}
    for count in (4, 6, 8):
        summary[str(count)] = {}
        for method in ("diagonal_lda_baseline", "spatiotemporal_shrinkage_lda"):
            summary[str(count)][method] = {}
            for repetition in (1, 3, 5, 10):
                values = [
                    next(item for item in subject["results"] if item["channels"] == count)
                    ["methods"][method]["character_accuracy_by_repetition"][str(repetition)]
                    for subject in subjects
                ]
                confirmation = values[1:]
                summary[str(count)][method][str(repetition)] = {
                    "all_subject_mean": float(np.mean(values)),
                    "development_subject_A01": float(values[0]),
                    "confirmation_A02_A08_mean": float(np.mean(confirmation)),
                    "confirmation_A02_A08_median": float(np.median(confirmation)),
                    "confirmation_A02_A08_min": float(np.min(confirmation)),
                    "confirmation_A02_A08_max": float(np.max(confirmation)),
                    "confirmation_subjects_at_or_above_0_85": int(np.sum(np.asarray(confirmation) >= 0.85)),
                }
    six = np.asarray([
        next(item for item in subject["results"] if item["channels"] == 6)
        ["methods"]["spatiotemporal_shrinkage_lda"]["character_accuracy_by_repetition"]["10"]
        for subject in subjects[1:]
    ])
    eight = np.asarray([
        next(item for item in subject["results"] if item["channels"] == 8)
        ["methods"]["spatiotemporal_shrinkage_lda"]["character_accuracy_by_repetition"]["10"]
        for subject in subjects[1:]
    ])
    differences = six - eight
    rng = np.random.default_rng(2026)
    bootstrap = np.asarray([
        np.mean(differences[rng.integers(0, len(differences), len(differences))])
        for _ in range(10000)
    ])
    lower, upper = np.quantile(bootstrap, [0.025, 0.975])
    paired = {
        "endpoint": "10-repetition character accuracy",
        "confirmation_subjects": [subject["subject"] for subject in subjects[1:]],
        "six_channel_mean": float(np.mean(six)),
        "eight_channel_mean": float(np.mean(eight)),
        "six_minus_eight_mean": float(np.mean(differences)),
        "subject_bootstrap_95_ci": [float(lower), float(upper)],
        "declared_engineering_noninferiority_margin": 0.05,
        "noninferior_at_margin": bool(lower >= -0.05),
        "interpretation": "Paired participant-level engineering analysis; not a prospective clinical non-inferiority trial.",
    }
    return {
        "development_policy": "A01 used to freeze the spatiotemporal window, downsampling, and shrinkage; A02-A08 are confirmation subjects.",
        "subjects": subjects,
        "cohort_summary": summary,
        "paired_confirmation_6_vs_8": paired,
    }


def save_report(report: dict, output: str | Path) -> None:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
