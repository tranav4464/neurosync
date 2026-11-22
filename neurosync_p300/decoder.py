"""Evidence accumulation and adaptive stopping for P300 spelling."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .data import EEGDataset
from .model import DiagonalLDA
from .quality import QualityAssessment


@dataclass
class DecoderConfig:
    min_repetitions: int = 2
    max_repetitions: int = 6
    confidence_threshold: float = 0.72
    margin_threshold: float = 0.18
    stability_repetitions: int = 2
    temperature: float = 1.0
    minimum_epoch_quality: float = 0.45
    reseat_after_bad_repetitions: int = 2
    reject_confidence_threshold: float = 0.35


@dataclass
class DecodedTrial:
    trial_id: int
    predicted_symbol: str
    repetitions_used: int
    confidence: float
    margin: float
    stopped_early: bool
    scores: dict[str, float]
    action: str = "ACCEPT"
    mean_quality: float = 1.0
    bad_repetitions: int = 0
    true_symbol: str | None = None


def _softmax(scores: np.ndarray, temperature: float) -> np.ndarray:
    scaled = scores / max(temperature, 1e-8)
    scaled -= np.max(scaled)
    values = np.exp(scaled)
    return values / np.sum(values)


def decode_dataset(
    model: DiagonalLDA,
    features: np.ndarray,
    dataset: EEGDataset,
    *,
    config: DecoderConfig | None = None,
    fixed_repetitions: int | None = None,
    quality: QualityAssessment | None = None,
) -> list[DecodedTrial]:
    """Decode one symbol per trial from flash-level model scores.

    For each repetition the classifier score for the flashed symbol is added
    to that symbol's running evidence. Adaptive mode stops once confidence and
    top-two margin pass their thresholds; fixed mode uses exactly the requested
    number of repetitions.
    """

    dataset.validate()
    features = np.asarray(features, dtype=float)
    if len(features) != len(dataset.epochs):
        raise ValueError("features and dataset must contain the same number of epochs")
    config = config or DecoderConfig()
    if config.min_repetitions < 1 or config.max_repetitions < config.min_repetitions:
        raise ValueError("invalid repetition limits")
    if config.stability_repetitions < 1:
        raise ValueError("stability_repetitions must be positive")
    if fixed_repetitions is not None and not 1 <= fixed_repetitions <= config.max_repetitions:
        raise ValueError("fixed_repetitions must be within decoder limits")

    if quality is not None and len(quality.epoch_quality) != len(features):
        raise ValueError("quality and features must contain the same number of epochs")
    flash_scores = model.decision_function(features)
    decoded: list[DecodedTrial] = []
    for trial_id in np.unique(dataset.trial_ids):
        trial_indices = np.flatnonzero(dataset.trial_ids == trial_id)
        symbols = sorted(set(dataset.symbols[trial_indices].tolist()))
        evidence = {symbol: 0.0 for symbol in symbols}
        true_symbol = None
        if np.any(dataset.labels[trial_indices] == 1):
            true_symbol = str(dataset.symbols[trial_indices][dataset.labels[trial_indices] == 1][0])

        repetition_values = sorted(np.unique(dataset.repetitions[trial_indices]).tolist())
        max_rep = min(config.max_repetitions, len(repetition_values))
        used = max_rep
        confidence = 0.0
        margin = 0.0
        stop_early = False
        top_history: list[str] = []
        bad_repetitions = 0
        repetition_quality: list[float] = []
        action = "REPEAT"

        for repetition in repetition_values[:max_rep]:
            current = trial_indices[dataset.repetitions[trial_indices] == repetition]
            current_quality = float(np.mean(quality.epoch_quality[current])) if quality is not None else 1.0
            repetition_quality.append(current_quality)
            if current_quality < config.minimum_epoch_quality:
                bad_repetitions += 1
            else:
                for index in current:
                    evidence[str(dataset.symbols[index])] += float(flash_scores[index])
            ordered = sorted(evidence.items(), key=lambda item: item[1], reverse=True)
            probabilities = _softmax(np.asarray([score for _, score in ordered]), config.temperature)
            confidence = float(probabilities[0])
            margin = float(probabilities[0] - probabilities[1]) if len(probabilities) > 1 else confidence
            top_history.append(ordered[0][0])
            stable = len(top_history) >= config.stability_repetitions and len(
                set(top_history[-config.stability_repetitions:])
            ) == 1

            if fixed_repetitions is not None:
                if repetition >= fixed_repetitions:
                    used = fixed_repetitions
                    break
            elif (
                repetition >= config.min_repetitions
                and stable
                and current_quality >= config.minimum_epoch_quality
                and confidence >= config.confidence_threshold
                and margin >= config.margin_threshold
            ):
                used = int(repetition)
                stop_early = used < max_rep
                action = "ACCEPT"
                break

        ordered = sorted(evidence.items(), key=lambda item: item[1], reverse=True)
        mean_quality = float(np.mean(repetition_quality)) if repetition_quality else 0.0
        if bad_repetitions >= config.reseat_after_bad_repetitions:
            action = "RESEAT_HEADSET"
        elif fixed_repetitions is not None:
            action = "ACCEPT" if confidence >= config.confidence_threshold and margin >= config.margin_threshold else "REPEAT"
        elif action != "ACCEPT":
            if confidence < config.reject_confidence_threshold:
                action = "REJECT"
            else:
                action = "REPEAT"
        decoded.append(DecodedTrial(
            trial_id=int(trial_id),
            predicted_symbol=ordered[0][0],
            repetitions_used=int(used),
            confidence=confidence,
            margin=margin,
            stopped_early=stop_early,
            scores={symbol: float(score) for symbol, score in ordered},
            action=action,
            mean_quality=mean_quality,
            bad_repetitions=bad_repetitions,
            true_symbol=true_symbol,
        ))
    return decoded


def summarize_decoding(results: list[DecodedTrial]) -> dict[str, float]:
    """Return milestone-friendly trial-level metrics."""

    if not results:
        return {"accuracy": 0.0, "accepted_accuracy": 0.0, "coverage": 0.0, "mean_repetitions": 0.0, "early_stop_rate": 0.0, "mean_confidence": 0.0}
    known = [item for item in results if item.true_symbol is not None]
    accuracy = float(np.mean([item.predicted_symbol == item.true_symbol for item in known])) if known else 0.0
    accepted = [item for item in known if item.action == "ACCEPT"]
    accepted_accuracy = float(np.mean([item.predicted_symbol == item.true_symbol for item in accepted])) if accepted else 0.0
    actions = {action: sum(item.action == action for item in results) for action in ("ACCEPT", "REPEAT", "REJECT", "RESEAT_HEADSET")}
    return {
        "accuracy": accuracy,
        "accepted_accuracy": accepted_accuracy,
        "coverage": float(len(accepted) / len(known)) if known else 0.0,
        "mean_repetitions": float(np.mean([item.repetitions_used for item in results])),
        "early_stop_rate": float(np.mean([item.stopped_early for item in results])),
        "mean_confidence": float(np.mean([item.confidence for item in results])),
        "accept_rate": float(actions["ACCEPT"] / len(results)),
        "repeat_rate": float(actions["REPEAT"] / len(results)),
        "reject_rate": float(actions["REJECT"] / len(results)),
        "reseat_rate": float(actions["RESEAT_HEADSET"] / len(results)),
    }

