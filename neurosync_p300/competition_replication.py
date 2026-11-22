"""Leakage-resistant within-subject replication on Competition III Dataset II."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .channel_selection import forward_select_channels
from .competition_data import load_competition_iii_train_ascii
from .data import EEGDataset
from .features import extract_features
from .feature_selection import StandardizedMeanFeatureSelector
from .model import DiagonalLDA
from .preprocessing import preprocess_epochs


MATRIX = ("ABCDEF", "GHIJKL", "MNOPQR", "STUVWX", "YZ1234", "56789_")


def _subset(dataset: EEGDataset, trial_ids: np.ndarray) -> EEGDataset:
    mask = np.isin(dataset.trial_ids, trial_ids)
    return EEGDataset(
        epochs=dataset.epochs[mask], labels=dataset.labels[mask], symbols=dataset.symbols[mask],
        trial_ids=dataset.trial_ids[mask], repetitions=dataset.repetitions[mask],
        channel_names=list(dataset.channel_names), sampling_rate=dataset.sampling_rate, metadata=dict(dataset.metadata),
    ).validate()


def _character(column: int, row: int) -> str:
    return MATRIX[row - 7][column - 1]


def _decode_row_column(scores: np.ndarray, dataset: EEGDataset, targets: dict[int, str], repetitions: int) -> dict:
    predictions: dict[int, str] = {}
    for trial in np.unique(dataset.trial_ids):
        mask = (dataset.trial_ids == trial) & (dataset.repetitions <= repetitions)
        codes = dataset.symbols[mask].astype(int)
        values = scores[mask]
        evidence = {code: float(values[codes == code].sum()) for code in range(1, 13)}
        column = max(range(1, 7), key=lambda code: evidence[code])
        row = max(range(7, 13), key=lambda code: evidence[code])
        predictions[int(trial)] = _character(column, row)
    truth = {trial: targets[trial] for trial in predictions}
    accuracy = float(np.mean([predictions[trial] == truth[trial] for trial in predictions]))
    return {"accuracy": accuracy, "predictions": predictions, "truth": truth}


def run_subject_a_replication(
    directory: str | Path,
    *,
    held_out_trials: int = 25,
    repetitions: int = 15,
    seed: int = 7,
    min_channels: int = 4,
    max_channels: int = 6,
    sparse_feature_count: int = 0,
) -> dict:
    """Run a held-out-character sparse-montage replication.

    This is a within-subject replication, not a cross-participant result. It
    uses only the official labelled training set and holds out whole character
    epochs before every learnable stage.
    """

    dataset = load_competition_iii_train_ascii(directory)
    trial_values = np.unique(dataset.trial_ids)
    if not 1 <= held_out_trials < len(trial_values):
        raise ValueError("held_out_trials must be between 1 and trial_count - 1")
    target_list = dataset.metadata.get("target_characters", [])
    if len(target_list) != len(trial_values):
        raise ValueError("Competition target labels are unavailable or malformed")
    targets = {int(trial): str(target_list[int(trial)]) for trial in trial_values}
    rng = np.random.default_rng(seed)
    test_ids = np.sort(rng.choice(trial_values, size=held_out_trials, replace=False))
    train_ids = np.setdiff1d(trial_values, test_ids)
    train, test = _subset(dataset, train_ids), _subset(dataset, test_ids)

    train_clean = preprocess_epochs(train.epochs, train.sampling_rate)
    test_clean = preprocess_epochs(test.epochs, test.sampling_rate)
    selection = forward_select_channels(
        train_clean, train.labels, train.trial_ids, train.channel_names, train.sampling_rate,
        min_channels=min_channels, max_channels=max_channels,
    )
    train_features = extract_features(train_clean[:, selection.indices, :], train.sampling_rate)
    test_features = extract_features(test_clean[:, selection.indices, :], test.sampling_rate)
    if sparse_feature_count:
        selector = StandardizedMeanFeatureSelector(max_features=min(sparse_feature_count, train_features.shape[1]))
        train_features = selector.fit(train_features, train.labels).transform(train_features)
        test_features = selector.transform(test_features)
    model = DiagonalLDA(shrinkage=0.20).fit(train_features, train.labels)
    flash_prediction = model.predict(test_features)
    balanced_accuracy = float(0.5 * (
        np.mean(flash_prediction[test.labels == 0] == 0) + np.mean(flash_prediction[test.labels == 1] == 1)
    ))
    decoded = _decode_row_column(model.decision_function(test_features), test, targets, repetitions)
    return {
        "dataset": "BCI Competition III Dataset II / Subject A train set",
        "claim_boundary": "Within-subject held-out-character replication only; no test-set labels, clinical, dry-electrode, or wet-reference claim.",
        "seed": seed,
        "held_out_trials": test_ids.tolist(),
        "train_trials": len(train_ids),
        "test_trials": len(test_ids),
        "repetitions": repetitions,
        "sparse_feature_count": sparse_feature_count,
        "selected_channels": selection.names,
        "selection_cv_balanced_accuracy": selection.cross_validated_balanced_accuracy,
        "held_out_flash_balanced_accuracy": balanced_accuracy,
        "held_out_character_accuracy": decoded["accuracy"],
        "predictions": decoded["predictions"],
        "truth": decoded["truth"],
    }


def save_replication_report(report: dict, output: str | Path) -> None:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
