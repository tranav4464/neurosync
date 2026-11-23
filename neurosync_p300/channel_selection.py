"""Forward-selection utilities for a 4-6 electrode design."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .features import extract_features
from .geometry import compute_observability_certificate, get_canonical_p300_proxy
from .model import DiagonalLDA


@dataclass
class ChannelSelectionResult:
    indices: list[int]
    names: list[str]
    cross_validated_balanced_accuracy: float
    history: list[dict] = field(default_factory=list)
    objective_score: float | None = None
    geometry_source: str = "none"


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


def _score_subset_stats(
    epochs: np.ndarray,
    labels: np.ndarray,
    trial_ids: np.ndarray,
    sampling_rate: float,
    subset: list[int],
    folds: list[tuple[np.ndarray, np.ndarray]],
) -> tuple[float, float]:
    features = extract_features(epochs[:, subset, :], sampling_rate)
    scores = []
    for train_idx, validation_idx in folds:
        model = DiagonalLDA().fit(features[train_idx], labels[train_idx])
        scores.append(_balanced_accuracy(labels[validation_idx], model.predict(features[validation_idx])))
    return float(np.mean(scores)), float(np.std(scores))


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


def stability_select_channels(
    epochs: np.ndarray,
    labels: np.ndarray,
    trial_ids: np.ndarray,
    channel_names: list[str],
    sampling_rate: float,
    *,
    channels: int = 6,
) -> ChannelSelectionResult:
    """Select channels that persist across leave-one-trial calibrations.

    This is a conservative alternative to one-shot forward selection.  It
    never sees a future recording: each inner fit omits an entire character
    trial, and final channel votes are resolved deterministically by mean
    inner-CV score then channel index.
    """
    ids = np.asarray(trial_ids)
    unique_trials = np.unique(ids)
    if len(unique_trials) < 3:
        raise ValueError("stability selection requires at least three trials")
    if not 1 <= channels <= len(channel_names):
        raise ValueError("channels must fit channel_names")
    votes = np.zeros(len(channel_names), dtype=int)
    scores = np.zeros(len(channel_names), dtype=float)
    for held_out in unique_trials:
        keep = ids != held_out
        selected = forward_select_channels(
            epochs[keep], np.asarray(labels)[keep], ids[keep], channel_names,
            sampling_rate, min_channels=channels, max_channels=channels,
        )
        votes[selected.indices] += 1
        scores[selected.indices] += selected.cross_validated_balanced_accuracy
    indices = sorted(
        range(len(channel_names)), key=lambda index: (-votes[index], -scores[index], index)
    )[:channels]
    return ChannelSelectionResult(
        indices=indices,
        names=[channel_names[index] for index in indices],
        cross_validated_balanced_accuracy=float(np.mean(scores[indices] / np.maximum(votes[indices], 1))),
        history=[{
            "selection_method": "leave_one_trial_stability",
            "vote_count": int(votes[index]),
            "mean_inner_cv_balanced_accuracy": float(scores[index] / max(votes[index], 1)),
            "channel": channel_names[index],
        } for index in indices],
    )


def biophysically_regularized_channel_selection(
    epochs: np.ndarray,
    labels: np.ndarray,
    trial_ids: np.ndarray,
    channel_names: list[str],
    sampling_rate: float,
    *,
    leadfield: np.ndarray | None = None,
    min_channels: int = 4,
    max_channels: int = 6,
    n_splits: int = 3,
    beta_observability: float = 0.15,
    beta_ambiguity: float = 0.10,
    beta_instability: float = 0.10,
    beta_contact: float = 0.10,
    channel_reliability: np.ndarray | None = None,
    geometry_source: str | None = None,
    target_indices: list[int] | None = None,
    artifact_indices: list[int] | None = None,
    min_improvement: float = 0.002,
    seed: int = 7,
) -> ChannelSelectionResult:
    """Select a compact montage with an optional geometry-proxy diagnostic.

    The built-in channel-name table is a research heuristic, not an anatomical
    forward model. It cannot certify source distinction or clinical safety.
    """
    if not 1 <= min_channels <= max_channels <= len(channel_names):
        raise ValueError("channel limits must fit the available channels")
    if leadfield is None:
        leadfield = get_canonical_p300_proxy(channel_names)
        geometry_source = geometry_source or "illustrative_proxy"
    else:
        leadfield = np.asarray(leadfield, dtype=float)
        if leadfield.ndim != 2 or leadfield.shape[0] != len(channel_names):
            raise ValueError("leadfield rows must match channel_names")
        geometry_source = geometry_source or "external_forward_model"
    if channel_reliability is None:
        channel_reliability = np.ones(len(channel_names), dtype=float)
    channel_reliability = np.asarray(channel_reliability, dtype=float)
    if channel_reliability.shape != (len(channel_names),):
        raise ValueError("channel_reliability must have one value per channel")
    channel_reliability = np.clip(channel_reliability, 0.0, 1.0)

    folds = _trial_folds(np.asarray(trial_ids), n_splits, seed)
    selected: list[int] = []
    history: list[dict] = []
    previous_score = -np.inf

    for size in range(1, max_channels + 1):
        candidates = [i for i in range(len(channel_names)) if i not in selected]
        candidate_scores = []
        for candidate in candidates:
            subset = selected + [candidate]
            empirical_acc, fold_instability = _score_subset_stats(
                epochs, labels, trial_ids, sampling_rate, subset, folds
            )
            
            # Compute geometric observability for candidate subset
            sub_g = leadfield[subset, :]
            baseline_samples = max(2, int(round(0.2 * sampling_rate)))
            baseline = epochs[:, subset, :baseline_samples].transpose(1, 0, 2).reshape(len(subset), -1)
            sub_cov = np.cov(baseline) if len(subset) > 1 else np.eye(1)
            if sub_cov.ndim < 2:
                sub_cov = np.eye(len(subset))
            report = compute_observability_certificate(
                sub_g,
                sub_cov,
                target_indices=target_indices,
                artifact_indices=artifact_indices,
            )
            
            # Biophysically regularized objective
            regularized_score = (
                empirical_acc
                + beta_observability * report.certificate
                - beta_ambiguity * report.worst_case_ambiguity
                - beta_instability * fold_instability
                - beta_contact * (1.0 - float(np.mean(channel_reliability[subset])))
            )
            candidate_scores.append((regularized_score, empirical_acc, fold_instability, report, candidate))

        best_reg_score, best_emp_acc, best_instability, best_rep, best_candidate = max(
            candidate_scores, key=lambda item: (item[0], item[1], -item[4])
        )
        improvement = best_reg_score - previous_score if np.isfinite(previous_score) else np.inf

        if size > min_channels and improvement < min_improvement:
            history.append({
                "size": size,
                "added": channel_names[best_candidate],
                "channels": [channel_names[i] for i in selected] + [channel_names[best_candidate]],
                "regularized_score": round(float(best_reg_score), 6),
                "empirical_accuracy": round(float(best_emp_acc), 6),
                "fold_instability": round(float(best_instability), 6),
                "mean_contact_reliability": round(float(np.mean(channel_reliability[selected + [best_candidate]])), 6),
                "observability_certificate": best_rep.certificate,
                "worst_case_ambiguity": best_rep.worst_case_ambiguity,
                "geometry_source": geometry_source,
                "accepted": False,
            })
            break

        selected.append(best_candidate)
        history.append({
            "size": size,
            "added": channel_names[best_candidate],
            "channels": [channel_names[i] for i in selected],
            "regularized_score": round(float(best_reg_score), 6),
            "empirical_accuracy": round(float(best_emp_acc), 6),
            "fold_instability": round(float(best_instability), 6),
            "mean_contact_reliability": round(float(np.mean(channel_reliability[selected])), 6),
            "observability_certificate": best_rep.certificate,
            "worst_case_ambiguity": best_rep.worst_case_ambiguity,
            "geometry_source": geometry_source,
            "accepted": True,
        })
        previous_score = best_reg_score

    final_emp_acc = _score_subset(epochs, labels, trial_ids, sampling_rate, selected, folds)
    return ChannelSelectionResult(
        indices=selected,
        names=[channel_names[i] for i in selected],
        cross_validated_balanced_accuracy=float(final_emp_acc),
        history=history,
        objective_score=float(previous_score),
        geometry_source=str(geometry_source),
    )


