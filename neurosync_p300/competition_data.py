"""Importer for BCI Competition III Dataset II ASCII P300 files.

The official subject archives store 64-channel signals as a large text matrix.
This loader reads only a requested montage, which makes sparse-headset
replication practical without loading the whole 64-channel array into memory.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .data import EEGDataset


# Official one-based channel assignments from the competition documentation.
COMPETITION_CHANNELS = {
    "Fz": 34, "Cz": 11, "CPz": 18, "Pz": 51,
    "POz": 58, "Oz": 62, "P3": 49, "P4": 53,
}


def _load_event_matrix(path: Path) -> np.ndarray:
    # ASCII files are samples × character epochs; transpose to trials × samples.
    values = np.loadtxt(path, dtype=np.int16)
    if values.ndim != 2:
        raise ValueError(f"unexpected event matrix shape in {path}")
    return values.T


def _load_selected_signal(
    path: Path,
    *,
    n_trials: int,
    n_samples: int,
    channel_numbers: list[int],
) -> np.ndarray:
    """Read requested one-based channels from trial-major Competition ASCII."""

    requested = {channel - 1: index for index, channel in enumerate(channel_numbers)}
    data = np.full((n_trials, len(channel_numbers), n_samples), np.nan, dtype=np.float32)
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle):
            trial, channel_index = divmod(line_number, 64)
            if trial >= n_trials:
                break
            output_channel = requested.get(channel_index)
            if output_channel is None:
                continue
            values = np.fromstring(line, sep=" ", dtype=np.float32)
            if len(values) != n_samples:
                raise ValueError(f"unexpected sample count on line {line_number + 1} in {path}")
            data[trial, output_channel] = values
    if np.isnan(data).any():
        raise ValueError("requested channel data were not fully populated")
    return data


def load_competition_iii_train_ascii(
    directory: str | Path,
    *,
    channel_names: tuple[str, ...] = ("Fz", "Cz", "CPz", "Pz", "POz", "Oz", "P3", "P4"),
    pre_stimulus_seconds: float = 0.2,
    epoch_seconds: float = 0.7,
) -> EEGDataset:
    """Convert labeled Subject_*_Train ASCII files into the common EEG format.

    Each flash becomes one epoch.  The first valid 0→1 flashing transition is
    treated as stimulus onset; a 200 ms pre-window is retained when available.
    Near-boundary flashes are excluded and their count is saved as metadata.
    """

    root = Path(directory)
    signal_path = root / "Subject_A_Train_Signal.txt"
    if not signal_path.exists():
        matches = list(root.glob("Subject_*_Train_Signal.txt"))
        if len(matches) != 1:
            raise FileNotFoundError("expected one Subject_*_Train_Signal.txt file")
        signal_path = matches[0]
    prefix = signal_path.name.replace("_Signal.txt", "")
    flashing = _load_event_matrix(root / f"{prefix}_Flashing.txt")
    codes = _load_event_matrix(root / f"{prefix}_StimulusCode.txt")
    labels = _load_event_matrix(root / f"{prefix}_StimulusType.txt")
    if flashing.shape != codes.shape or codes.shape != labels.shape:
        raise ValueError("Competition event matrices have inconsistent shapes")

    requested_numbers = []
    for name in channel_names:
        if name not in COMPETITION_CHANNELS:
            raise ValueError(f"unsupported Competition channel name: {name}")
        requested_numbers.append(COMPETITION_CHANNELS[name])
    signals = _load_selected_signal(
        signal_path,
        n_trials=flashing.shape[0],
        n_samples=flashing.shape[1],
        channel_numbers=requested_numbers,
    )

    sampling_rate = 240.0
    pre_samples = int(round(pre_stimulus_seconds * sampling_rate))
    post_samples = int(round(epoch_seconds * sampling_rate))
    epochs: list[np.ndarray] = []
    event_labels: list[int] = []
    event_codes: list[str] = []
    trial_ids: list[int] = []
    repetitions: list[int] = []
    excluded = 0
    for trial in range(flashing.shape[0]):
        starts = np.flatnonzero((flashing[trial] == 1) & np.r_[True, flashing[trial, :-1] == 0])
        code_counts: dict[int, int] = {}
        for start in starts:
            code = int(codes[trial, start])
            if not 1 <= code <= 12:
                continue
            left, right = start - pre_samples, start + post_samples
            if left < 0 or right > signals.shape[-1]:
                excluded += 1
                continue
            code_counts[code] = code_counts.get(code, 0) + 1
            epochs.append(signals[trial, :, left:right])
            event_labels.append(int(labels[trial, start] == 1))
            event_codes.append(str(code))
            trial_ids.append(trial)
            repetitions.append(code_counts[code])
    if not epochs:
        raise ValueError("no valid flash epochs were extracted")
    target_chars_path = root / f"{prefix}_TargetChar.txt"
    raw_target_chars = target_chars_path.read_text(encoding="utf-8").split() if target_chars_path.exists() else []
    target_chars = [chr(int(value)) if value.lstrip("-").isdigit() else value for value in raw_target_chars]
    return EEGDataset(
        epochs=np.stack(epochs),
        labels=np.asarray(event_labels, dtype=int),
        symbols=np.asarray(event_codes),
        trial_ids=np.asarray(trial_ids, dtype=int),
        repetitions=np.asarray(repetitions, dtype=int),
        channel_names=list(channel_names),
        sampling_rate=sampling_rate,
        metadata={
            "source": "BCI Competition III Dataset II",
            "source_directory": str(root),
            "paradigm": "6x6 row-column P300 speller",
            "pre_stimulus_seconds": pre_stimulus_seconds,
            "epoch_seconds_post_stimulus": epoch_seconds,
            "excluded_boundary_flashes": excluded,
            "target_characters": target_chars,
            "competition_channel_numbers": requested_numbers,
        },
    ).validate()
