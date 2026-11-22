"""Feature extraction shared by channel selection, training, and decoding."""

from __future__ import annotations

import numpy as np


def extract_features(
    epochs: np.ndarray,
    sampling_rate: float,
    *,
    window_seconds: tuple[float, float] = (0.25, 0.60),
    pre_stimulus_seconds: float = 0.2,
    downsample: int = 4,
) -> np.ndarray:
    """Extract raw and pooled P300 features for each epoch.

    The downsampled waveform preserves time-resolved information.  Three
    non-overlapping pooled amplitudes (early, peak, late) are appended for
    every channel.  Pooling is fixed before fitting and reduces variance in
    the broad P300 complex without learning from the test session.
    """

    data = np.asarray(epochs, dtype=float)
    if data.ndim != 3:
        raise ValueError("epochs must have shape (n_epochs, n_channels, n_samples)")
    if downsample < 1:
        raise ValueError("downsample must be >= 1")
    start = int(round((window_seconds[0] + pre_stimulus_seconds) * sampling_rate))
    end = int(round((window_seconds[1] + pre_stimulus_seconds) * sampling_rate))
    start = max(0, min(data.shape[-1] - 1, start))
    end = max(start + 1, min(data.shape[-1], end))
    window = data[..., start:end:downsample]
    waveform_features = window.reshape(window.shape[0], -1)

    # P300 morphology is broad, so pooled windows provide a low-variance
    # complement to the sampled waveform.  Bounds are relative to the
    # stimulus and safely clipped for shorter recordings.
    pooled = []
    for pool_start, pool_end in ((0.25, 0.35), (0.35, 0.48), (0.48, 0.60)):
        left = int(round((pool_start + pre_stimulus_seconds) * sampling_rate))
        right = int(round((pool_end + pre_stimulus_seconds) * sampling_rate))
        left = max(0, min(data.shape[-1] - 1, left))
        right = max(left + 1, min(data.shape[-1], right))
        pooled.append(data[..., left:right].mean(axis=-1))
    pooled_features = np.concatenate(pooled, axis=1)
    return np.concatenate([waveform_features, pooled_features], axis=1)

