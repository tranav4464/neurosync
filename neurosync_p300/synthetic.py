"""Synthetic P300 data for reproducible engineering tests.

This is not a substitute for human EEG.  It creates a controlled signal with
known target flashes, low-frequency drift, and an adjustable dry-electrode
noise penalty so the pipeline can be tested before a lab recording exists.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from .data import EEGDataset


DEFAULT_CHANNELS = ["Fz", "Cz", "Pz", "CPz", "POz", "Oz", "P3", "P4"]
DEFAULT_SYMBOLS = list("ABCDEF")


def generate_synthetic_dataset(
    *,
    n_trials: int = 80,
    repetitions: int = 6,
    symbols: Sequence[str] = DEFAULT_SYMBOLS,
    channel_names: Sequence[str] = DEFAULT_CHANNELS,
    sampling_rate: float = 128.0,
    duration_seconds: float = 1.0,
    pre_stimulus_seconds: float = 0.2,
    electrode_type: str = "wet",
    seed: int = 7,
    targets: Sequence[str] | None = None,
) -> EEGDataset:
    """Generate target/non-target epochs with a configurable electrode model."""

    if electrode_type not in {"wet", "dry"}:
        raise ValueError("electrode_type must be 'wet' or 'dry'")
    symbols = list(symbols)
    channel_names = list(channel_names)
    if not symbols:
        raise ValueError("at least one symbol is required")
    if repetitions < 1 or n_trials < 1:
        raise ValueError("n_trials and repetitions must be positive")
    if targets is not None:
        targets = list(targets)
        if len(targets) != n_trials or any(target not in symbols for target in targets):
            raise ValueError("targets must contain one valid symbol per trial")

    rng = np.random.default_rng(seed)
    n_channels = len(channel_names)
    n_samples = int(round(duration_seconds * sampling_rate))
    time = np.arange(n_samples, dtype=float) / sampling_rate - pre_stimulus_seconds
    n_epochs = n_trials * repetitions * len(symbols)
    epochs = np.empty((n_epochs, n_channels, n_samples), dtype=float)
    labels = np.empty(n_epochs, dtype=int)
    flashed_symbols: list[str] = []
    trial_ids = np.empty(n_epochs, dtype=int)
    repetition_ids = np.empty(n_epochs, dtype=int)

    # Central/parietal sites carry the largest synthetic P300 response.
    response_gain = np.asarray([0.45, 0.80, 1.00, 0.92, 0.70, 0.45, 0.48, 0.48])
    if n_channels != len(response_gain):
        response_gain = np.linspace(0.45, 1.0, n_channels)
        response_gain = response_gain[::-1]

    if electrode_type == "wet":
        noise_std = 0.62
        drift_std = 0.22
        response_scale = 0.78
    else:
        noise_std = 1.75
        drift_std = 0.72
        response_scale = 0.30

    cursor = 0
    for trial in range(n_trials):
        target = targets[trial] if targets is not None else symbols[int(rng.integers(0, len(symbols)))]
        for repetition in range(1, repetitions + 1):
            order = rng.permutation(symbols)
            for symbol in order:
                # Background includes slow delta/theta drift and a modest
                # alpha component. Dry electrodes receive more drift and
                # independent high-frequency contact noise.
                phase = rng.uniform(0, 2 * np.pi, size=n_channels)
                drift = drift_std * np.sin(2 * np.pi * 0.8 * time[None, :] + phase[:, None])
                drift += 0.10 * np.sin(2 * np.pi * 4.5 * time[None, :] + phase[:, None] / 2)
                noise = rng.normal(0, noise_std, size=(n_channels, n_samples))
                if electrode_type == "dry":
                    noise += rng.normal(0, 0.22, size=(n_channels, 1))
                    noise += rng.normal(0, 0.12, size=(n_channels, n_samples))

                is_target = int(symbol == target)
                p300 = np.exp(-0.5 * ((time - 0.31) / 0.065) ** 2)
                p300 += 0.52 * np.exp(-0.5 * ((time - 0.47) / 0.10) ** 2)
                p300 -= 0.20 * np.exp(-0.5 * ((time - 0.20) / 0.035) ** 2)
                trial_response_jitter = rng.normal(1.0, 0.16)
                response = is_target * response_scale * trial_response_jitter * response_gain[:, None] * p300[None, :]

                epochs[cursor] = drift + noise + response
                labels[cursor] = is_target
                flashed_symbols.append(symbol)
                trial_ids[cursor] = trial
                repetition_ids[cursor] = repetition
                cursor += 1

    return EEGDataset(
        epochs=epochs,
        labels=labels,
        symbols=np.asarray(flashed_symbols),
        trial_ids=trial_ids,
        repetitions=repetition_ids,
        channel_names=channel_names,
        sampling_rate=sampling_rate,
        metadata={
            "source": "synthetic",
            "electrode_type": electrode_type,
            "target_definition": "flashed symbol equals trial target",
            "seed": seed,
        },
    ).validate()


def inject_contact_artifacts(
    dataset: EEGDataset,
    *,
    fraction: float = 0.15,
    seed: int = 17,
    by_trial: bool = False,
    all_channels: bool = False,
) -> EEGDataset:
    """Create an intentionally corrupted copy for CASP safety demonstrations.

    The function adds slow contact drift and short transient excursions to a
    subset of flash epochs. ``by_trial=True, all_channels=True`` creates a
    whole-cap contact-failure condition for testing the re-seat path. It is
    only a controlled software stress test, not a physiological model of an
    electrode failure.
    """

    dataset.validate()
    if not 0.0 <= fraction <= 1.0:
        raise ValueError("fraction must be between 0 and 1")
    rng = np.random.default_rng(seed)
    epochs = dataset.epochs.copy()
    if by_trial:
        trial_values = np.unique(dataset.trial_ids)
        artifact_count = int(round(len(trial_values) * fraction))
        affected_trials = rng.choice(trial_values, size=artifact_count, replace=False) if artifact_count else np.array([], dtype=int)
        affected = np.flatnonzero(np.isin(dataset.trial_ids, affected_trials))
    else:
        artifact_count = int(round(len(epochs) * fraction))
        affected = np.sort(rng.choice(len(epochs), size=artifact_count, replace=False)) if artifact_count else np.array([], dtype=int)
    time = np.arange(dataset.n_samples, dtype=float) / dataset.sampling_rate
    for epoch_index in affected:
        channels = range(dataset.n_channels) if all_channels else [int(rng.integers(0, dataset.n_channels))]
        transient_center = int(rng.integers(dataset.n_samples // 4, 3 * dataset.n_samples // 4))
        transient = np.zeros(dataset.n_samples)
        transient[transient_center: transient_center + min(3, dataset.n_samples - transient_center)] = rng.uniform(8.0, 12.0)
        for channel in channels:
            drift = rng.uniform(5.0, 8.0) * np.sin(2 * np.pi * rng.uniform(0.4, 1.2) * time + rng.uniform(0, 2 * np.pi))
            epochs[epoch_index, channel] += drift + transient
    return EEGDataset(
        epochs=epochs,
        labels=dataset.labels.copy(),
        symbols=dataset.symbols.copy(),
        trial_ids=dataset.trial_ids.copy(),
        repetitions=dataset.repetitions.copy(),
        channel_names=list(dataset.channel_names),
        sampling_rate=dataset.sampling_rate,
        metadata={
            **dataset.metadata,
            "synthetic_contact_artifact_fraction": fraction,
            "artifact_by_trial": by_trial,
            "artifact_all_channels": all_channels,
            "artifact_epoch_indices": affected.tolist(),
        },
    ).validate()

