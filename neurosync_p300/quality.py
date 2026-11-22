"""Contact-quality and artifact screening for NeuroSync CASP.

CASP (Contact-Aware Adaptive Sparse P300) does not assume every electrode is
equally trustworthy on every flash.  This module learns normal channel metrics
from calibration data and returns transparent quality weights for later data.
It is an engineering quality gate, not a clinical impedance measurement.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class QualityAssessment:
    """Per-epoch channel and aggregate quality scores in the range [0, 1]."""

    channel_quality: np.ndarray  # (epochs, channels)
    epoch_quality: np.ndarray  # (epochs,)
    low_frequency_ratio: np.ndarray
    line_noise_ratio: np.ndarray
    peak_to_peak: np.ndarray

    def select_channels(self, indices: list[int]) -> "QualityAssessment":
        channel_quality = self.channel_quality[:, indices]
        return QualityAssessment(
            channel_quality=channel_quality,
            epoch_quality=np.mean(channel_quality, axis=1),
            low_frequency_ratio=self.low_frequency_ratio[:, indices],
            line_noise_ratio=self.line_noise_ratio[:, indices],
            peak_to_peak=self.peak_to_peak[:, indices],
        )


def _band_power(data: np.ndarray, sampling_rate: float, low: float, high: float) -> np.ndarray:
    spectrum = np.fft.rfft(data, axis=-1)
    power = np.abs(spectrum) ** 2
    frequencies = np.fft.rfftfreq(data.shape[-1], d=1.0 / sampling_rate)
    mask = (frequencies >= low) & (frequencies <= high)
    if not np.any(mask):
        return np.zeros(data.shape[:2], dtype=float)
    return power[..., mask].mean(axis=-1)


class ContactQualityGate:
    """Calibration-fitted signal-quality model for sparse EEG channels.

    The gate scores three observable warning signals: elevated low-frequency
    power (drift/contact movement), line-noise ratio, and unusually large
    peak-to-peak excursions (transient artifact). It deliberately does not
    claim to measure physical impedance unless an amplifier supplies it.
    """

    def __init__(
        self,
        *,
        low_band: tuple[float, float] = (0.1, 4.0),
        reference_band: tuple[float, float] = (0.5, 20.0),
        line_hz: float = 50.0,
        line_half_width_hz: float = 1.0,
        max_z: float = 6.0,
    ):
        self.low_band = low_band
        self.reference_band = reference_band
        self.line_hz = line_hz
        self.line_half_width_hz = line_half_width_hz
        self.max_z = max_z
        self.fitted = False

    def _metrics(self, epochs: np.ndarray, sampling_rate: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        data = np.asarray(epochs, dtype=float)
        if data.ndim != 3:
            raise ValueError("epochs must have shape (n_epochs, n_channels, n_samples)")
        baseline = _band_power(data, sampling_rate, *self.reference_band) + 1e-12
        low_ratio = _band_power(data, sampling_rate, *self.low_band) / baseline
        line_ratio = _band_power(
            data,
            sampling_rate,
            self.line_hz - self.line_half_width_hz,
            self.line_hz + self.line_half_width_hz,
        ) / baseline
        peak_to_peak = np.ptp(data, axis=-1)
        return low_ratio, line_ratio, peak_to_peak

    def fit(self, epochs: np.ndarray, sampling_rate: float) -> "ContactQualityGate":
        metrics = self._metrics(epochs, sampling_rate)
        self.center_ = np.stack([np.median(metric, axis=0) for metric in metrics])
        mad = np.stack([np.median(np.abs(metric - center), axis=0) for metric, center in zip(metrics, self.center_)])
        self.scale_ = np.maximum(1.4826 * mad, 1e-8)
        self.fitted = True
        return self

    def assess(self, epochs: np.ndarray, sampling_rate: float) -> QualityAssessment:
        if not self.fitted:
            raise RuntimeError("fit the quality gate using calibration data before assessment")
        metrics = self._metrics(epochs, sampling_rate)
        z_scores = []
        for metric, center, scale in zip(metrics, self.center_, self.scale_):
            # Only unusually high values are evidence of this class of artifact.
            z_scores.append(np.clip((metric - center) / scale, 0.0, self.max_z))
        combined = 0.50 * z_scores[0] + 0.20 * z_scores[1] + 0.30 * z_scores[2]
        channel_quality = np.exp(-combined)
        return QualityAssessment(
            channel_quality=channel_quality,
            epoch_quality=np.mean(channel_quality, axis=1),
            low_frequency_ratio=metrics[0],
            line_noise_ratio=metrics[1],
            peak_to_peak=metrics[2],
        )


def apply_channel_quality(features: np.ndarray, channel_quality: np.ndarray) -> np.ndarray:
    """Down-weight flattened channel features using the square-root of quality.

    The square root preserves a usable signal in moderately degraded channels
    while strongly reducing channels flagged by the contact-quality gate.
    """

    X = np.asarray(features, dtype=float)
    quality = np.asarray(channel_quality, dtype=float)
    if X.ndim != 2 or quality.ndim != 2 or len(X) != len(quality):
        raise ValueError("features and channel_quality must have matching epoch rows")
    if X.shape[1] % quality.shape[1] != 0:
        raise ValueError("feature count must be divisible by the number of channels")
    samples_per_channel = X.shape[1] // quality.shape[1]
    reshaped = X.reshape(len(X), quality.shape[1], samples_per_channel)
    return (reshaped * np.sqrt(np.clip(quality, 0.0, 1.0))[..., None]).reshape(X.shape)

