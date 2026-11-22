"""Small supervised spatial filter for P300 signal-to-noise enhancement.

This is an interpretable xDAWN-inspired ablation, not a claim of a full
xDAWN implementation.  It learns channel mixtures that maximize the
target-minus-nontarget template energy relative to residual channel noise.
"""

from __future__ import annotations

import numpy as np


class TemplateSpatialFilter:
    """Regularized supervised spatial filter fit on training epochs only."""

    def __init__(self, *, n_components: int = 3, ridge: float = 0.10):
        self.n_components = int(n_components)
        self.ridge = float(ridge)

    def fit(self, epochs: np.ndarray, labels: np.ndarray) -> "TemplateSpatialFilter":
        data = np.asarray(epochs, dtype=float)
        y = np.asarray(labels, dtype=int)
        if data.ndim != 3 or len(data) != len(y):
            raise ValueError("epochs must be (epochs, channels, samples) with matching labels")
        if set(np.unique(y)) != {0, 1}:
            raise ValueError("both target and non-target epochs are required")
        if not 1 <= self.n_components <= data.shape[1]:
            raise ValueError("n_components must fit the input channels")

        class_means = [data[y == label].mean(axis=0) for label in (0, 1)]
        template = class_means[1] - class_means[0]
        signal_cov = template @ template.T / template.shape[1]

        residuals = np.concatenate([data[y == label] - class_means[label] for label in (0, 1)], axis=0)
        noise_cov = np.einsum("ect,edt->cd", residuals, residuals) / (residuals.shape[0] * residuals.shape[2])
        scale = float(np.trace(noise_cov) / noise_cov.shape[0])
        noise_cov += np.eye(noise_cov.shape[0]) * max(scale * self.ridge, 1e-8)

        values, vectors = np.linalg.eigh(noise_cov)
        inverse_sqrt = vectors @ np.diag(1.0 / np.sqrt(np.maximum(values, 1e-10))) @ vectors.T
        whitened_signal = inverse_sqrt @ signal_cov @ inverse_sqrt
        _, directions = np.linalg.eigh(whitened_signal)
        filters = (inverse_sqrt @ directions[:, ::-1][:, : self.n_components]).T
        # Unit-norm components make downstream regularization more stable.
        self.filters_ = filters / np.maximum(np.linalg.norm(filters, axis=1, keepdims=True), 1e-10)
        return self

    def transform(self, epochs: np.ndarray) -> np.ndarray:
        if not hasattr(self, "filters_"):
            raise RuntimeError("fit the spatial filter before transforming")
        data = np.asarray(epochs, dtype=float)
        if data.ndim != 3 or data.shape[1] != self.filters_.shape[1]:
            raise ValueError("epochs have incompatible channel shape")
        return np.einsum("kc,ect->ekt", self.filters_, data)
