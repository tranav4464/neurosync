"""Low-dependency EEG preprocessing for the prototype."""

from __future__ import annotations

import numpy as np


def _interval_indices(
    sampling_rate: float,
    n_samples: int,
    start_seconds: float,
    end_seconds: float,
    pre_stimulus_seconds: float,
) -> tuple[int, int]:
    start = int(round((start_seconds + pre_stimulus_seconds) * sampling_rate))
    end = int(round((end_seconds + pre_stimulus_seconds) * sampling_rate))
    start = max(0, min(n_samples - 1, start))
    end = max(start + 1, min(n_samples, end))
    return start, end


def _fft_bandpass(
    epochs: np.ndarray,
    sampling_rate: float,
    low_hz: float,
    high_hz: float,
    notch_hz: float | None,
    notch_width_hz: float,
) -> np.ndarray:
    """Apply a transparent frequency-domain filter.

    It is intentionally conservative and dependency-light. For a production
    clinical pipeline, validate filter phase, edge handling, and artifact
    rejection against the chosen amplifier and hardware montage.
    """

    if not 0 <= low_hz < high_hz <= sampling_rate / 2:
        raise ValueError("filter frequencies must satisfy 0 <= low < high <= Nyquist")
    spectrum = np.fft.rfft(epochs, axis=-1)
    frequencies = np.fft.rfftfreq(epochs.shape[-1], d=1.0 / sampling_rate)
    keep = (frequencies >= low_hz) & (frequencies <= high_hz)
    if notch_hz is not None:
        keep &= np.abs(frequencies - notch_hz) > notch_width_hz / 2
    spectrum *= keep[None, None, :]
    return np.fft.irfft(spectrum, n=epochs.shape[-1], axis=-1)


def preprocess_epochs(
    epochs: np.ndarray,
    sampling_rate: float,
    *,
    pre_stimulus_seconds: float = 0.2,
    baseline_seconds: tuple[float, float] = (-0.2, 0.0),
    low_hz: float = 0.5,
    high_hz: float = 20.0,
    notch_hz: float | None = None,
    notch_width_hz: float = 2.0,
) -> np.ndarray:
    """Baseline-correct and band-limit ``(epochs, channels, samples)`` data."""

    data = np.asarray(epochs, dtype=float).copy()
    if data.ndim != 3:
        raise ValueError("epochs must have shape (n_epochs, n_channels, n_samples)")
    start, end = _interval_indices(
        sampling_rate,
        data.shape[-1],
        baseline_seconds[0],
        baseline_seconds[1],
        pre_stimulus_seconds,
    )
    data -= data[..., start:end].mean(axis=-1, keepdims=True)
    filtered = _fft_bandpass(data, sampling_rate, low_hz, high_hz, notch_hz, notch_width_hz)
    # Finite-window FFT filtering can reintroduce a small DC offset through
    # edge ringing, so enforce the baseline reference once more afterward.
    filtered -= filtered[..., start:end].mean(axis=-1, keepdims=True)
    return filtered

