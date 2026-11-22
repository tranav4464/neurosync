"""Data containers and an intentionally simple NPZ interchange format.

The prototype represents one flash/epoch as ``channels x samples``.  Every
epoch has a trial id, a repetition number, and the symbol that was flashed.
The format is deliberately explicit so it can later be populated by a
hardware adapter without changing the decoder.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import numpy as np


@dataclass
class EEGDataset:
    """Epoch-level EEG data for a P300 spelling session."""

    epochs: np.ndarray
    labels: np.ndarray
    symbols: np.ndarray
    trial_ids: np.ndarray
    repetitions: np.ndarray
    channel_names: list[str]
    sampling_rate: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> "EEGDataset":
        self.epochs = np.asarray(self.epochs, dtype=float)
        self.labels = np.asarray(self.labels, dtype=int)
        self.symbols = np.asarray(self.symbols).astype(str)
        self.trial_ids = np.asarray(self.trial_ids, dtype=int)
        self.repetitions = np.asarray(self.repetitions, dtype=int)

        if self.epochs.ndim != 3:
            raise ValueError("epochs must have shape (n_epochs, n_channels, n_samples)")
        n_epochs, n_channels, _ = self.epochs.shape
        arrays = {
            "labels": self.labels,
            "symbols": self.symbols,
            "trial_ids": self.trial_ids,
            "repetitions": self.repetitions,
        }
        for name, array in arrays.items():
            if len(array) != n_epochs:
                raise ValueError(f"{name} must have {n_epochs} entries")
        if len(self.channel_names) != n_channels:
            raise ValueError("channel_names must match the channel dimension")
        if set(np.unique(self.labels)) - {0, 1}:
            raise ValueError("labels must contain only 0 (non-target) and 1 (target)")
        if self.sampling_rate <= 0:
            raise ValueError("sampling_rate must be positive")
        return self

    @property
    def n_channels(self) -> int:
        return int(self.epochs.shape[1])

    @property
    def n_samples(self) -> int:
        return int(self.epochs.shape[2])

    @property
    def trial_count(self) -> int:
        return int(len(np.unique(self.trial_ids)))

    def select_channels(self, indices: Iterable[int]) -> "EEGDataset":
        indices = list(indices)
        return EEGDataset(
            epochs=self.epochs[:, indices, :],
            labels=self.labels.copy(),
            symbols=self.symbols.copy(),
            trial_ids=self.trial_ids.copy(),
            repetitions=self.repetitions.copy(),
            channel_names=[self.channel_names[i] for i in indices],
            sampling_rate=self.sampling_rate,
            metadata={**self.metadata, "selected_channels": [self.channel_names[i] for i in indices]},
        ).validate()


def save_npz(dataset: EEGDataset, path: str | Path) -> None:
    """Save a dataset in the documented NumPy archive format."""

    dataset.validate()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        epochs=dataset.epochs,
        labels=dataset.labels,
        symbols=dataset.symbols,
        trial_ids=dataset.trial_ids,
        repetitions=dataset.repetitions,
        channel_names=np.asarray(dataset.channel_names),
        sampling_rate=np.asarray(dataset.sampling_rate),
    )


def load_npz(path: str | Path) -> EEGDataset:
    """Load and validate a dataset saved by :func:`save_npz`."""

    with np.load(path, allow_pickle=False) as bundle:
        required = {
            "epochs",
            "labels",
            "symbols",
            "trial_ids",
            "repetitions",
            "channel_names",
            "sampling_rate",
        }
        missing = required - set(bundle.files)
        if missing:
            raise ValueError(f"NPZ is missing required arrays: {sorted(missing)}")
        dataset = EEGDataset(
            epochs=bundle["epochs"],
            labels=bundle["labels"],
            symbols=bundle["symbols"],
            trial_ids=bundle["trial_ids"],
            repetitions=bundle["repetitions"],
            channel_names=[str(x) for x in bundle["channel_names"].tolist()],
            sampling_rate=float(bundle["sampling_rate"]),
        )
    return dataset.validate()

