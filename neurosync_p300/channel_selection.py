"""Forward-selection utilities for a 4-6 electrode design."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .features import extract_features
from .model import DiagonalLDA


@dataclass
class ChannelSelectionResult:
    indices: list[int]
    names: list[str]
    cross_validated_balanced_accuracy: float
    history: list[dict] = field(default_factory=list)


def _balanced_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    values = []
    for label in (0, 1):
        mask = y_true == label
        values.append(float(np.mean(y_pred[mask] == label)) if np.any(mask) else 0.0)
    return float(np.mean(values))


def _trial_folds(trial_ids: np.ndarray, n_splits: int, seed: int) -> list[tuple[np.ndarray, np.ndarray]]:
    unique = np.unique(trial_ids)
    rng = np.random.default_rng(seed)
    unique = rng.permutation(unique)
    folds = np.array_split(unique, min(n_splits, len(unique)))
    result = []
    for fold in folds:
        validation = np.isin(trial_ids, fold)
        result.append((np.flatnonzero(~validation), np.flatnonzero(validation)))
    return result


def _score_subset(
    epochs: np.ndarray,
    labels: np.ndarray,
    trial_ids: np.ndarray,
    sampling_rate: float,
    subset: list[int],
    folds: list[tuple[np.ndarray, np.ndarray]],
) -> float:
    features = extract_features(epochs[:, subset, :], sampling_rate)
    scores = []
    for train_idx, validation_idx in folds:
        model = DiagonalLDA()
        model.fit(features[train_idx], labels[train_idx])
        scores.append(_balanced_accuracy(labels[validation_idx], model.predict(features[validation_idx])))
    return float(np.mean(scores))


def forward_select_channels(
    epochs: np.ndarray,
    labels: np.ndarray,
    trial_ids: np.ndarray,
    channel_names: list[str],
    sampling_rate: float,
    *,
    min_channels: int = 4,
    max_channels: int = 6,
    n_splits: int = 3,
    min_improvement: float = 0.002,
    seed: int = 7,
) -> ChannelSelectionResult:
    """Select a compact channel set using trial-level cross-validation."""

    if not 1 <= min_channels <= max_channels <= len(channel_names):
        raise ValueError("channel limits must fit the available channels")
    folds = _trial_folds(np.asarray(trial_ids), n_splits, seed)
    selected: list[int] = []
    history: list[dict] = []
    previous_score = -np.inf

    for size in range(1, max_channels + 1):
        candidates = [i for i in range(len(channel_names)) if i not in selected]
        candidate_scores = []
        for candidate in candidates:
            subset = selected + [candidate]
            candidate_scores.append((
                _score_subset(epochs, labels, trial_ids, sampling_rate, subset, folds),
                candidate,
            ))
        best_score, best_candidate = max(candidate_scores, key=lambda item: (item[0], -item[1]))
        improvement = best_score - previous_score if np.isfinite(previous_score) else np.inf
        if size > min_channels and improvement < min_improvement:
            history.append({
                "size": size,
                "added": channel_names[best_candidate],
                "channels": [channel_names[i] for i in selected] + [channel_names[best_candidate]],
                "cross_validated_balanced_accuracy": round(float(best_score), 6),
                "accepted": False,
            })
            break

        selected.append(best_candidate)
        history.append({
            "size": size,
            "added": channel_names[best_candidate],
            "channels": [channel_names[i] for i in selected],
            "cross_validated_balanced_accuracy": round(float(best_score), 6),
            "accepted": True,
        })
        previous_score = best_score

    return ChannelSelectionResult(
        indices=selected,
        names=[channel_names[i] for i in selected],
        cross_validated_balanced_accuracy=float(previous_score),
        history=history,
    )

