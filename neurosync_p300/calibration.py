"""Leakage-resistant score-temperature calibration for P300 flash scores."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .model import DiagonalLDA


@dataclass
class TemperatureCalibration:
    temperature: float
    validation_log_loss: float
    candidates_tested: list[float]


@dataclass
class DecisionCalibration:
    """Out-of-fold settings for the final symbol-level accept decision."""

    temperature: float
    confidence_threshold: float
    margin_threshold: float
    utility: float
    correct_accept_rate: float
    wrong_accept_rate: float
    coverage: float


def _trial_folds(trial_ids: np.ndarray, n_splits: int, seed: int) -> list[tuple[np.ndarray, np.ndarray]]:
    unique = np.unique(trial_ids)
    if len(unique) < 2:
        raise ValueError("at least two trials are required for out-of-fold calibration")
    rng = np.random.default_rng(seed)
    shuffled = rng.permutation(unique)
    groups = np.array_split(shuffled, min(n_splits, len(unique)))
    return [
        (np.flatnonzero(~np.isin(trial_ids, group)), np.flatnonzero(np.isin(trial_ids, group)))
        for group in groups
    ]


def _balanced_log_loss(scores: np.ndarray, labels: np.ndarray, temperature: float) -> float:
    probabilities = 1.0 / (1.0 + np.exp(-np.clip(scores / temperature, -60, 60)))
    losses = -(labels * np.log(np.clip(probabilities, 1e-8, 1 - 1e-8)) + (1 - labels) * np.log(np.clip(1 - probabilities, 1e-8, 1 - 1e-8)))
    class_losses = [losses[labels == label].mean() for label in (0, 1) if np.any(labels == label)]
    return float(np.mean(class_losses))


def _symbol_log_loss(
    scores: np.ndarray,
    labels: np.ndarray,
    symbols: np.ndarray,
    trial_ids: np.ndarray,
    temperature: float,
) -> float:
    """Negative log likelihood after the same evidence accumulation as decoding."""

    losses = []
    for trial_id in np.unique(trial_ids):
        indices = np.flatnonzero(trial_ids == trial_id)
        choices = sorted(set(symbols[indices].tolist()))
        target = np.unique(symbols[indices][labels[indices] == 1])
        if len(target) != 1:
            raise ValueError("each calibration trial must contain one unique target symbol")
        evidence = np.asarray([scores[indices][symbols[indices] == choice].sum() for choice in choices])
        scaled = evidence / temperature
        scaled -= np.max(scaled)
        probabilities = np.exp(scaled)
        probabilities /= probabilities.sum()
        target_index = choices.index(str(target[0]))
        losses.append(-np.log(np.clip(probabilities[target_index], 1e-8, 1.0)))
    return float(np.mean(losses))


def calibrate_temperature_oof(
    features: np.ndarray,
    labels: np.ndarray,
    trial_ids: np.ndarray,
    *,
    symbols: np.ndarray | None = None,
    n_splits: int = 3,
    seed: int = 7,
    candidates: tuple[float, ...] = (0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0),
) -> TemperatureCalibration:
    """Choose a temperature using only out-of-fold flash scores.

    This is intentionally modest calibration: it scales LDA decision scores
    before symbol-level softmax accumulation. It does not make probabilities
    clinically calibrated, and it must be rechecked on a held-out session.
    """

    X = np.asarray(features, dtype=float)
    y = np.asarray(labels, dtype=int)
    ids = np.asarray(trial_ids, dtype=int)
    if len(X) != len(y) or len(y) != len(ids):
        raise ValueError("features, labels, and trial_ids must have matching rows")
    oof_scores = np.empty(len(y), dtype=float)
    for fit_idx, validation_idx in _trial_folds(ids, n_splits, seed):
        model = DiagonalLDA(shrinkage=0.20).fit(X[fit_idx], y[fit_idx])
        oof_scores[validation_idx] = model.decision_function(X[validation_idx])
    if symbols is not None:
        symbol_values = np.asarray(symbols).astype(str)
        if len(symbol_values) != len(y):
            raise ValueError("symbols and labels must have matching rows")
        losses = [(temperature, _symbol_log_loss(oof_scores, y, symbol_values, ids, temperature)) for temperature in candidates]
    else:
        losses = [(temperature, _balanced_log_loss(oof_scores, y, temperature)) for temperature in candidates]
    temperature, loss = min(losses, key=lambda item: item[1])
    return TemperatureCalibration(float(temperature), float(loss), list(candidates))


def calibrate_decision_oof(
    features: np.ndarray,
    labels: np.ndarray,
    trial_ids: np.ndarray,
    symbols: np.ndarray,
    *,
    n_splits: int = 3,
    seed: int = 7,
    temperatures: tuple[float, ...] = (0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0),
    confidence_thresholds: tuple[float, ...] = (0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60, 0.72),
    margin_thresholds: tuple[float, ...] = (0.0, 0.05, 0.10, 0.18),
    wrong_accept_penalty: float = 2.0,
) -> DecisionCalibration:
    """Tune temperature and accept thresholds from out-of-fold symbol evidence.

    Utility is ``correct_accept_rate - wrong_accept_penalty * wrong_accept_rate``.
    This prevents the all-reject solution from winning a threshold search while
    still assigning a greater cost to an unsafe wrong acceptance than to an
    abstention. The penalty is an engineering policy that must be pre-specified
    for a real study.
    """

    X = np.asarray(features, dtype=float)
    y = np.asarray(labels, dtype=int)
    ids = np.asarray(trial_ids, dtype=int)
    symbol_values = np.asarray(symbols).astype(str)
    if len(X) != len(y) or len(y) != len(ids) or len(y) != len(symbol_values):
        raise ValueError("features, labels, trial_ids, and symbols must have matching rows")
    oof_scores = np.empty(len(y), dtype=float)
    for fit_idx, validation_idx in _trial_folds(ids, n_splits, seed):
        model = DiagonalLDA(shrinkage=0.20).fit(X[fit_idx], y[fit_idx])
        oof_scores[validation_idx] = model.decision_function(X[validation_idx])

    trials = []
    for trial_id in np.unique(ids):
        indices = np.flatnonzero(ids == trial_id)
        choices = sorted(set(symbol_values[indices].tolist()))
        targets = np.unique(symbol_values[indices][y[indices] == 1])
        if len(targets) != 1:
            raise ValueError("each calibration trial must contain one unique target symbol")
        evidence = np.asarray([oof_scores[indices][symbol_values[indices] == choice].sum() for choice in choices])
        trials.append((choices, evidence, str(targets[0])))

    best: DecisionCalibration | None = None
    for temperature in temperatures:
        decisions = []
        for choices, evidence, target in trials:
            scaled = evidence / temperature
            scaled -= np.max(scaled)
            probabilities = np.exp(scaled)
            probabilities /= probabilities.sum()
            ranked = np.argsort(probabilities)[::-1]
            confidence = float(probabilities[ranked[0]])
            margin = float(probabilities[ranked[0]] - probabilities[ranked[1]]) if len(ranked) > 1 else confidence
            decisions.append((choices[ranked[0]] == target, confidence, margin))
        for confidence_threshold in confidence_thresholds:
            for margin_threshold in margin_thresholds:
                accepted = [(correct, confidence, margin) for correct, confidence, margin in decisions if confidence >= confidence_threshold and margin >= margin_threshold]
                correct_rate = sum(correct for correct, _, _ in accepted) / len(trials)
                wrong_rate = (len(accepted) - sum(correct for correct, _, _ in accepted)) / len(trials)
                coverage = len(accepted) / len(trials)
                utility = correct_rate - wrong_accept_penalty * wrong_rate
                proposal = DecisionCalibration(
                    float(temperature),
                    float(confidence_threshold),
                    float(margin_threshold),
                    float(utility),
                    float(correct_rate),
                    float(wrong_rate),
                    float(coverage),
                )
                if best is None or (proposal.utility, proposal.correct_accept_rate, proposal.coverage) > (best.utility, best.correct_accept_rate, best.coverage):
                    best = proposal
    if best is None:
        raise RuntimeError("unable to calibrate decision thresholds")
    return best

