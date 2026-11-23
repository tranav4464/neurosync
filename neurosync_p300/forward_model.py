"""Validated interchange for participant/template EEG forward models.

Forward models are intentionally imported rather than guessed.  An NPZ file
can be exported from MNE-Python, FieldTrip, or another BEM/FEM workflow and
must contain ``leadfield`` and ``channel_names``.  Optional source labels and
provenance are retained for reporting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class ForwardModel:
    leadfield: np.ndarray
    channel_names: tuple[str, ...]
    source_labels: tuple[str, ...] = ()
    target_indices: tuple[int, ...] = (0, 1)
    artifact_indices: tuple[int, ...] = ()
    provenance: dict[str, str] = field(default_factory=dict)

    def validate(self) -> "ForwardModel":
        matrix = np.asarray(self.leadfield, dtype=float)
        if matrix.ndim != 2 or matrix.shape[0] != len(self.channel_names):
            raise ValueError("leadfield must be channels x sources and match channel_names")
        if matrix.shape[1] < 2 or not np.isfinite(matrix).all():
            raise ValueError("leadfield needs at least two finite source signatures")
        if len(set(self.channel_names)) != len(self.channel_names):
            raise ValueError("forward-model channel names must be unique")
        if self.source_labels and len(self.source_labels) != matrix.shape[1]:
            raise ValueError("source_labels must match the leadfield source dimension")
        all_indices = self.target_indices + self.artifact_indices
        if not self.target_indices or any(index < 0 or index >= matrix.shape[1] for index in all_indices):
            raise ValueError("source-group indices must address leadfield columns")
        if set(self.target_indices) & set(self.artifact_indices):
            raise ValueError("target and artifact source groups must not overlap")
        return self

    def align(self, requested_channels: list[str]) -> np.ndarray:
        """Return rows in dataset order; fail rather than silently interpolate."""
        lookup = {name.casefold(): index for index, name in enumerate(self.channel_names)}
        missing = [name for name in requested_channels if name.casefold() not in lookup]
        if missing:
            raise ValueError(f"forward model is missing channels: {missing}")
        return np.asarray(self.leadfield, dtype=float)[
            [lookup[name.casefold()] for name in requested_channels], :
        ]


def load_forward_model(path: str | Path) -> ForwardModel:
    """Load a forward model from the documented, non-pickled NPZ format."""
    with np.load(path, allow_pickle=False) as bundle:
        required = {"leadfield", "channel_names"}
        missing = required - set(bundle.files)
        if missing:
            raise ValueError(f"forward model is missing arrays: {sorted(missing)}")
        labels = tuple(str(x) for x in bundle["source_labels"].tolist()) if "source_labels" in bundle else ()
        target_indices = tuple(int(x) for x in bundle["target_indices"].tolist()) if "target_indices" in bundle else (0, 1)
        artifact_indices = tuple(int(x) for x in bundle["artifact_indices"].tolist()) if "artifact_indices" in bundle else ()
        provenance = {
            key.removeprefix("provenance_"): str(np.asarray(bundle[key]).item())
            for key in bundle.files
            if key.startswith("provenance_")
        }
        model = ForwardModel(
            leadfield=np.asarray(bundle["leadfield"], dtype=float),
            channel_names=tuple(str(x) for x in bundle["channel_names"].tolist()),
            source_labels=labels,
            target_indices=target_indices,
            artifact_indices=artifact_indices,
            provenance=provenance,
        )
    return model.validate()
