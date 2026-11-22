"""Small supervised spatial filter for P300 signal-to-noise enhancement.

This is an interpretable xDAWN-inspired ablation, not a claim of a full
xDAWN implementation.  It learns channel mixtures that maximize the
target-minus-nontarget template energy relative to residual channel noise.
"""

from __future__ import annotations

import numpy as np

from .geometry import _psd_eigh


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


class SubspaceWhitenedSpatialFilter:
    """Supervised spatial filter regularized by rank-deficient noise-subspace whitening.

    Brings Observable Geometry's spectral truncation (_psd_eigh) into spatial filtering,
    safely handling ill-conditioned covariance matrices arising from dry-electrode impedance
    spikes or average-referencing without eigenvalue explosion.
    """

    def __init__(self, *, n_components: int = 3, rcond: float = 1e-5):
        self.n_components = int(n_components)
        self.rcond = float(rcond)

    def fit(self, epochs: np.ndarray, labels: np.ndarray) -> "SubspaceWhitenedSpatialFilter":
        data = np.asarray(epochs, dtype=float)
        y = np.asarray(labels, dtype=int)
        if data.ndim != 3 or len(data) != len(y):
            raise ValueError("epochs must be (epochs, channels, samples) with matching labels")
        if set(np.unique(y)) != {0, 1}:
            raise ValueError("both target and non-target epochs are required")

        class_means = [data[y == label].mean(axis=0) for label in (0, 1)]
        template = class_means[1] - class_means[0]
        signal_cov = template @ template.T / template.shape[1]

        residuals = np.concatenate([data[y == label] - class_means[label] for label in (0, 1)], axis=0)
        noise_cov = np.einsum("ect,edt->cd", residuals, residuals) / (residuals.shape[0] * residuals.shape[2])

        # Supported noise subspace decomposition via Observable Geometry
        u_r, lambda_r = _psd_eigh(noise_cov, rcond=self.rcond)
        whitening_op = u_r / np.sqrt(lambda_r)[np.newaxis, :]  # shape (m, r)

        # Signal covariance projected into supported whitened subspace
        whitened_signal = whitening_op.T @ signal_cov @ whitening_op
        ev_sig, dir_sig = np.linalg.eigh(0.5 * (whitened_signal + whitened_signal.T))

        k = min(self.n_components, len(lambda_r))
        # Top eigenvectors in whitened subspace
        top_directions = dir_sig[:, ::-1][:, :k]
        filters = (whitening_op @ top_directions).T
        self.filters_ = filters / np.maximum(np.linalg.norm(filters, axis=1, keepdims=True), 1e-10)
        return self

    def transform(self, epochs: np.ndarray) -> np.ndarray:
        if not hasattr(self, "filters_"):
            raise RuntimeError("fit the spatial filter before transforming")
        data = np.asarray(epochs, dtype=float)
        if data.ndim != 3 or data.shape[1] != self.filters_.shape[1]:
            raise ValueError("epochs have incompatible channel shape")
        return np.einsum("kc,ect->ekt", self.filters_, data)

