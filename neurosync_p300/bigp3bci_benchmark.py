"""File-disjoint P300 event-detection benchmark for a named bigP3BCI study.

This benchmark intentionally evaluates target-versus-nontarget event detection
instead of character accuracy.  Study-specific stimulus encoders must be
validated before character decoding is meaningful.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .bigp3bci_data import load_bigp3bci_edf
from .channel_selection import forward_select_channels
from .features import extract_features
from .model import ShrinkageLDA
from .preprocessing import preprocess_epochs


def _balanced_accuracy(labels: np.ndarray, predictions: np.ndarray) -> float:
    values = []
    for value in (0, 1):
        mask = labels == value
        values.append(float(np.mean(predictions[mask] == value)))
    return float(np.mean(values))


def _roc_auc(labels: np.ndarray, scores: np.ndarray) -> float:
    """Mann-Whitney AUC with average ranks for tied classifier scores."""
    y = np.asarray(labels, dtype=int)
    s = np.asarray(scores, dtype=float)
    positive = y == 1
    n_positive, n_negative = int(positive.sum()), int((~positive).sum())
    if n_positive == 0 or n_negative == 0:
        raise ValueError("ROC AUC requires both classes")
    order = np.argsort(s, kind="mergesort")
    ranks = np.empty(len(s), dtype=float)
    start = 0
    while start < len(s):
        end = start + 1
        while end < len(s) and s[order[end]] == s[order[start]]:
            end += 1
        ranks[order[start:end]] = (start + 1 + end) / 2.0
        start = end
    return float((ranks[positive].sum() - n_positive * (n_positive + 1) / 2.0) / (n_positive * n_negative))


def _align_test_channels(train_names: list[str], test_names: list[str]) -> list[int]:
    lookup = {name: index for index, name in enumerate(test_names)}
    try:
        return [lookup[name] for name in train_names]
    except KeyError as exc:
        raise ValueError(f"test file is missing training channel {exc.args[0]}") from exc


def benchmark_recording_pair(
    train_path: str | Path,
    test_path: str | Path,
    *,
    channel_counts: tuple[int, ...] = (6, 32),
) -> dict:
    """Train on one EDF recording and evaluate a later, separate EDF file."""
    train = load_bigp3bci_edf(train_path)
    test = load_bigp3bci_edf(test_path)
    if train.sampling_rate != test.sampling_rate:
        raise ValueError("train/test sampling rates differ")
    test_order = _align_test_channels(train.channel_names, test.channel_names)
    test_epochs = test.epochs[:, test_order]
    train_clean = preprocess_epochs(train.epochs, train.sampling_rate)
    test_clean = preprocess_epochs(test_epochs, test.sampling_rate)
    if max(channel_counts) > len(train.channel_names):
        raise ValueError("requested channel count exceeds available EEG channels")
    results = []
    for count in channel_counts:
        if count == len(train.channel_names):
            indices = list(range(count))
            names = list(train.channel_names)
            selection_score = None
        else:
            selection = forward_select_channels(
                train_clean, train.labels, train.trial_ids, train.channel_names,
                train.sampling_rate, min_channels=count, max_channels=count,
            )
            indices, names = selection.indices, selection.names
            selection_score = selection.cross_validated_balanced_accuracy
        train_features = extract_features(
            train_clean[:, indices], train.sampling_rate,
            window_seconds=(0.10, 0.80), downsample=8,
        )
        test_features = extract_features(
            test_clean[:, indices], test.sampling_rate,
            window_seconds=(0.10, 0.80), downsample=8,
        )
        model = ShrinkageLDA(shrinkage=0.10).fit(train_features, train.labels)
        scores = model.decision_function(test_features)
        predictions = (scores >= 0.0).astype(int)
        results.append({
            "channels": count,
            "selected_channels": names,
            "training_only_selection_cv_balanced_accuracy": selection_score,
            "held_out_event_roc_auc": _roc_auc(test.labels, scores),
            "held_out_event_balanced_accuracy": _balanced_accuracy(test.labels, predictions),
            "held_out_events": int(len(test.labels)),
            "held_out_target_events": int(test.labels.sum()),
        })
    return {
        "dataset": "bigP3BCI 1.0.0", "study": "Study A", "paradigm": "RD, 9x8",
        "train_file": Path(train_path).name, "held_out_file": Path(test_path).name,
        "split": "file-disjoint Train recording to later Test recording",
        "endpoint": "event-level target-vs-nontarget ROC AUC and balanced accuracy",
        "claim_boundary": "Event detection only; no unvalidated conversion to character accuracy or dry-electrode claim.",
        "train_audit": train.metadata["event_table_audit"],
        "held_out_audit": test.metadata["event_table_audit"],
        "results": results,
    }


def benchmark_cohort(recording_pairs: list[tuple[str | Path, str | Path]]) -> dict:
    """Run a predeclared set of file-disjoint pairs and summarize it equally.

    Each participant contributes one recording-pair result, preventing a long
    EDF file or a participant with more events from dominating the cohort mean.
    """
    if not recording_pairs:
        raise ValueError("at least one train/test recording pair is required")
    participants = [benchmark_recording_pair(train, test) for train, test in recording_pairs]
    counts = sorted({item["channels"] for result in participants for item in result["results"]})
    summary = {}
    for count in counts:
        rows = [next(item for item in result["results"] if item["channels"] == count) for result in participants]
        aucs = np.asarray([item["held_out_event_roc_auc"] for item in rows])
        balanced = np.asarray([item["held_out_event_balanced_accuracy"] for item in rows])
        summary[str(count)] = {
            "participants": int(len(rows)),
            "mean_held_out_event_roc_auc": float(aucs.mean()),
            "median_held_out_event_roc_auc": float(np.median(aucs)),
            "min_held_out_event_roc_auc": float(aucs.min()),
            "max_held_out_event_roc_auc": float(aucs.max()),
            "mean_held_out_event_balanced_accuracy": float(balanced.mean()),
        }
    return {
        "analysis": "predeclared file-disjoint event-detection cohort",
        "participants": participants,
        "cohort_summary": summary,
        "claim_boundary": "Study-specific event detection; no character-accuracy, dry-electrode, or clinical claim.",
    }


def save_report(report: dict, output: str | Path) -> None:
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
