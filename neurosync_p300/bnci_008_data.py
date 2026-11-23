"""Loader for BNCI 2014-008: eight ALS participants using a P300 speller."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .data import EEGDataset


BNCI_008_CHANNELS = ("Fz", "Cz", "Pz", "Oz", "P3", "P4", "PO7", "PO8")
MATRIX = ("ABCDEF", "GHIJKL", "MNOPQR", "STUVWX", "YZ1234", "56789_")


def _character_from_codes(row_code: int, column_code: int) -> str:
    return MATRIX[row_code - 1][column_code - 7]


def load_bnci_008_mat(
    path: str | Path,
    *,
    pre_stimulus_seconds: float = 0.2,
    post_stimulus_seconds: float = 0.8,
) -> EEGDataset:
    """Load one official subject MAT file and epoch every intensification.

    The source stores class and stimulus codes as sample-wise step functions.
    We detect each non-zero block onset and preserve the official 35 character
    order: characters 0--14 are calibration and 15--34 are feedback/testing.
    """
    try:
        from scipy.io import loadmat
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError("BNCI MAT loading requires scipy; install the public-data extra") from exc

    source = Path(path)
    raw = loadmat(source, squeeze_me=True, struct_as_record=False)["data"]
    signal = np.asarray(raw.X, dtype=np.float32)
    class_step = np.asarray(raw.y, dtype=int)
    stimulus_step = np.asarray(raw.y_stim, dtype=int)
    trial_starts = np.asarray(raw.trial, dtype=int) - 1  # MATLAB to Python
    channel_names = [str(value) for value in np.asarray(raw.channels).tolist()]
    if signal.ndim != 2 or signal.shape[1] != len(channel_names):
        raise ValueError("unexpected BNCI 008 signal/channel shape")
    if len(signal) != len(class_step) or len(signal) != len(stimulus_step):
        raise ValueError("BNCI 008 sample arrays have inconsistent lengths")

    sampling_rate = 256.0
    pre = int(round(pre_stimulus_seconds * sampling_rate))
    post = int(round(post_stimulus_seconds * sampling_rate))
    onsets = np.flatnonzero(
        (stimulus_step > 0)
        & np.r_[True, stimulus_step[1:] != stimulus_step[:-1]]
    )
    trial_ends = np.r_[trial_starts[1:], len(signal)]
    epochs: list[np.ndarray] = []
    labels: list[int] = []
    symbols: list[str] = []
    trial_ids: list[int] = []
    repetitions: list[int] = []
    targets: list[str] = []
    excluded = 0
    for trial_id, (trial_start, trial_end) in enumerate(zip(trial_starts, trial_ends)):
        current = onsets[(onsets >= trial_start) & (onsets < trial_end)]
        counts: dict[int, int] = {}
        target_codes: set[int] = set()
        for onset in current:
            code = int(stimulus_step[onset])
            is_target = int(class_step[onset] == 2)
            if is_target:
                target_codes.add(code)
            left, right = int(onset) - pre, int(onset) + post
            if left < 0 or right > len(signal):
                excluded += 1
                continue
            counts[code] = counts.get(code, 0) + 1
            epochs.append(signal[left:right].T)
            labels.append(is_target)
            symbols.append(str(code))
            trial_ids.append(trial_id)
            repetitions.append(counts[code])
        rows = sorted(code for code in target_codes if 1 <= code <= 6)
        columns = sorted(code for code in target_codes if 7 <= code <= 12)
        if len(rows) != 1 or len(columns) != 1:
            raise ValueError(f"trial {trial_id} does not identify one target row and column")
        targets.append(_character_from_codes(rows[0], columns[0]))

    dataset = EEGDataset(
        epochs=np.stack(epochs),
        labels=np.asarray(labels),
        symbols=np.asarray(symbols),
        trial_ids=np.asarray(trial_ids),
        repetitions=np.asarray(repetitions),
        channel_names=channel_names,
        sampling_rate=sampling_rate,
        metadata={
            "source": "BNCI 2014-008",
            "source_file": source.name,
            "population": "ALS",
            "official_calibration_trials": list(range(15)),
            "official_feedback_trials": list(range(15, 35)),
            "target_characters": targets,
            "excluded_boundary_events": excluded,
            "age": str(raw.age),
            "gender": str(raw.gender),
            "alsfrs": str(raw.ALSfrs),
            "als_onset": str(raw.onsetALS),
        },
    )
    return dataset.validate()
