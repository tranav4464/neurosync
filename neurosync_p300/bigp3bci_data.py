"""Conservative EDF event extractor for the bigP3BCI resource.

bigP3BCI studies use different stimulus layouts.  This adapter extracts EEG
epochs and their published target/non-target labels without pretending that a
study's ``StimulusCode`` is compatible with NeuroSync's 6x6 row/column
decoder.  A protocol-specific decoder must be added only after that study's
display and code semantics have been verified.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .data import EEGDataset


_REQUIRED_STATUS = ("StimulusBegin", "StimulusType", "CurrentTarget")


def _rising_edges(signal: np.ndarray) -> np.ndarray:
    values = np.asarray(signal)
    # At index i, compare the current status value with sample i-1.
    return np.flatnonzero((values > 0) & np.r_[True, values[:-1] <= 0])


def _trial_blocks(current_target: np.ndarray) -> list[tuple[int, int, int]]:
    """Return nonzero current-target blocks as (start, end, target-id)."""
    values = np.asarray(current_target, dtype=int)
    starts = np.flatnonzero((values > 0) & np.r_[True, values[:-1] <= 0])
    blocks: list[tuple[int, int, int]] = []
    for start in starts:
        after = np.flatnonzero(values[start:] != values[start])
        end = int(start + after[0]) if len(after) else len(values)
        blocks.append((int(start), end, int(values[start])))
    return blocks


def audit_bigp3bci_events(dataset: EEGDataset) -> dict:
    """Audit generic event invariants without imposing a row/column model."""
    trials = np.unique(dataset.trial_ids)
    per_trial = []
    for trial in trials:
        mask = dataset.trial_ids == trial
        per_trial.append({
            "trial": int(trial),
            "event_count": int(mask.sum()),
            "target_event_count": int(dataset.labels[mask].sum()),
            "unique_stimulus_codes": int(len(np.unique(dataset.symbols[mask]))),
        })
    return {
        "passed": bool(len(trials) > 0 and all(item["event_count"] > 0 for item in per_trial)),
        "observed_trials": int(len(trials)),
        "observed_events": int(len(dataset.epochs)),
        "per_trial": per_trial,
        "decoder_compatibility": "Not assumed: this extractor does not map bigP3BCI codes to a 6x6 row/column speller.",
    }


def load_bigp3bci_edf(
    path: str | Path,
    *,
    pre_stimulus_seconds: float = 0.2,
    post_stimulus_seconds: float = 0.8,
) -> EEGDataset:
    """Extract labeled EEG epochs from one bigP3BCI EDF recording.

    The returned ``symbols`` are the source ``StimulusCode`` values when that
    channel is present, otherwise a stable event index.  They must not be
    passed to the 6x6 character decoder without a study-specific mapping.
    """
    try:
        import pyedflib
    except ImportError as exc:  # pragma: no cover - dependency specific
        raise ImportError("bigP3BCI EDF loading requires pyedflib") from exc

    source = Path(path)
    reader = pyedflib.EdfReader(str(source))
    try:
        names = [str(name) for name in reader.getSignalLabels()]
        indices = {name: index for index, name in enumerate(names)}
        missing = [name for name in _REQUIRED_STATUS if name not in indices]
        if missing:
            raise ValueError(f"missing required bigP3BCI status channels: {missing}")
        eeg_names = [name for name in names if name.startswith("EEG_")]
        if not eeg_names:
            raise ValueError("no EEG_* channels found")
        eeg_indices = [indices[name] for name in eeg_names]
        sampling_rates = np.asarray([reader.getSampleFrequency(index) for index in eeg_indices], dtype=float)
        if not np.allclose(sampling_rates, sampling_rates[0], rtol=1e-6):
            raise ValueError("EEG channels do not share a sampling rate")
        sampling_rate = float(sampling_rates[0])
        eeg = np.stack([reader.readSignal(index) for index in eeg_indices], axis=0).astype(np.float32)
        stimulus_begin = reader.readSignal(indices["StimulusBegin"])
        stimulus_type = reader.readSignal(indices["StimulusType"])
        current_target = reader.readSignal(indices["CurrentTarget"])
        stimulus_code = (
            reader.readSignal(indices["StimulusCode"])
            if "StimulusCode" in indices else None
        )
    finally:
        reader.close()

    onsets = _rising_edges(stimulus_begin)
    blocks = _trial_blocks(current_target)
    pre = int(round(pre_stimulus_seconds * sampling_rate))
    post = int(round(post_stimulus_seconds * sampling_rate))
    epochs: list[np.ndarray] = []
    labels: list[int] = []
    symbols: list[str] = []
    trial_ids: list[int] = []
    repetitions: list[int] = []
    excluded = 0
    trial_targets: list[int] = []
    for trial_id, (start, end, target) in enumerate(blocks):
        trial_targets.append(target)
        counts: dict[str, int] = {}
        for event_index, onset in enumerate(onsets[(onsets >= start) & (onsets < end)]):
            left, right = int(onset) - pre, int(onset) + post
            if left < 0 or right > eeg.shape[1]:
                excluded += 1
                continue
            code = str(int(stimulus_code[onset])) if stimulus_code is not None else str(event_index)
            counts[code] = counts.get(code, 0) + 1
            epochs.append(eeg[:, left:right])
            labels.append(int(stimulus_type[onset] > 0))
            symbols.append(code)
            trial_ids.append(trial_id)
            repetitions.append(counts[code])
    if not epochs:
        raise ValueError("no valid bigP3BCI stimulus epochs were extracted")
    dataset = EEGDataset(
        epochs=np.stack(epochs), labels=np.asarray(labels), symbols=np.asarray(symbols),
        trial_ids=np.asarray(trial_ids), repetitions=np.asarray(repetitions),
        channel_names=eeg_names, sampling_rate=sampling_rate,
        metadata={
            "source": "bigP3BCI 1.0.0", "source_file": source.name,
            "source_target_ids": trial_targets,
            "excluded_boundary_events": excluded,
            "paradigm_boundary": "Protocol-specific stimulus coding; no 6x6 row/column assumption.",
        },
    ).validate()
    dataset.metadata["event_table_audit"] = audit_bigp3bci_events(dataset)
    return dataset
