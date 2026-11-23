"""Geometry diagnostics for *measured* EEG forward models.

The linear-algebra routines in this module are valid for a supplied leadfield
and noise covariance. The bundled 10--20 table is a pedagogical montage
*proxy*, not an individual BEM/FEM forward model, impedance measurement, or
clinical safety certificate.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class ObservabilityReport:
    """Diagnostic report quantifying montage observability over P300 generators."""

    certificate: float  # O_cert in [0, 1]
    worst_case_ambiguity: float  # rho in [0, 1]
    min_residual: float  # sqrt(1 - rho^2)
    supported_rank: int
    resolution_fraction: float


def _psd_eigh(cov: np.ndarray, rcond: float = 1e-6) -> tuple[np.ndarray, np.ndarray]:
    """Eigendecomposition for symmetric positive semidefinite matrices with rank truncation.

    Safely handles rank deficiency from average referencing, common-mode rejection,
    and highly correlated dry-contact sensors.
    """
    cov = np.asarray(cov, dtype=float)
    if cov.ndim != 2 or cov.shape[0] != cov.shape[1]:
        raise ValueError("Covariance matrix must be square.")
    
    # Enforce symmetry
    cov = 0.5 * (cov + cov.T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    
    # Sort in descending order
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    # Threshold for positive support
    max_ev = max(float(eigenvalues[0]), 1e-12)
    threshold = max_ev * rcond
    support_mask = eigenvalues > threshold
    
    if not np.any(support_mask):
        # Fallback to rank-1 if entirely degenerate
        return np.ones((cov.shape[0], 1)) / np.sqrt(cov.shape[0]), np.array([1e-6])
        
    return eigenvectors[:, support_mask], eigenvalues[support_mask]


def average_reference_operator(n_channels: int) -> np.ndarray:
    """Return the average referencing projection matrix P = I - (1/m) 1 1^T."""
    return np.eye(n_channels) - (1.0 / n_channels) * np.ones((n_channels, n_channels))


def whitened_unit_signatures(leadfield: np.ndarray, cov: np.ndarray, rcond: float = 1e-6) -> tuple[np.ndarray, int]:
    """Project leadfield signatures into the supported noise covariance subspace and normalize to unit norm.

    Parameters
    ----------
    leadfield : np.ndarray
        Leadfield matrix of shape (n_channels, n_sources).
    cov : np.ndarray
        Sensor noise covariance of shape (n_channels, n_channels).

    Returns
    -------
    unit_signatures : np.ndarray
        Normalized whitened signatures of shape (supported_rank, n_sources).
    rank : int
        Supported rank of the noise covariance.
    """
    leadfield = np.asarray(leadfield, dtype=float)
    u_r, lambda_r = _psd_eigh(cov, rcond=rcond)
    supported_rank = len(lambda_r)
    
    # Whitened signatures: z = Lambda^(-1/2) * U^T * G
    whitening_filter = u_r / np.sqrt(lambda_r)[np.newaxis, :]  # shape (m, r)
    z = whitening_filter.T @ leadfield  # shape (r, n_sources)
    
    # Normalize onto unit sphere: u_i = z_i / ||z_i||_2
    norms = np.linalg.norm(z, axis=0, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    unit_signatures = z / norms
    return unit_signatures, supported_rank


def absolute_cosine_ambiguity(unit_signatures: np.ndarray) -> np.ndarray:
    """Compute pairwise absolute cosine similarity rho_ij = |u_i^T u_j| in [0, 1]."""
    sim = np.abs(unit_signatures.T @ unit_signatures)
    return np.clip(sim, 0.0, 1.0)


def compute_observability_certificate(
    leadfield: np.ndarray,
    noise_cov: np.ndarray,
    target_indices: list[int] | None = None,
    artifact_indices: list[int] | None = None,
    rcond: float = 1e-6,
) -> ObservabilityReport:
    """Calculate the Source Observability Certificate (O_cert) for a montage.

    Evaluates whether the sensor configuration G preserves biophysical distinction
    between target P300 generators and confounding artifact sources under noise cov.
    """
    leadfield = np.asarray(leadfield, dtype=float)
    n_channels, n_sources = leadfield.shape
    
    if target_indices is None:
        target_indices = [0, 1]  # Default to first dipoles (e.g. P3b, P3a)
    if artifact_indices is None:
        artifact_indices = [i for i in range(n_sources) if i not in target_indices]
        
    unit_sigs, rank = whitened_unit_signatures(leadfield, noise_cov, rcond=rcond)
    ambiguity_matrix = absolute_cosine_ambiguity(unit_sigs)
    
    # Cross-ambiguity between target generators and artifact generators
    if len(artifact_indices) > 0:
        cross_ambiguity = ambiguity_matrix[np.ix_(target_indices, artifact_indices)]
        worst_case_rho = float(np.max(cross_ambiguity))
    else:
        # If no artifacts designated, compute off-diagonal ambiguity between targets
        mask = ~np.eye(len(target_indices), dtype=bool)
        sub = ambiguity_matrix[np.ix_(target_indices, target_indices)]
        worst_case_rho = float(np.max(sub[mask])) if np.any(mask) else 0.0
        
    min_residual = float(np.sqrt(max(0.0, 1.0 - worst_case_rho ** 2)))
    
    # Approximate linear resolution matrix diagonal
    # R = (G^T C^+ G + alpha I)^(-1) G^T C^+ G
    u_r, lambda_r = _psd_eigh(noise_cov, rcond=rcond)
    cov_pinv = (u_r / lambda_r[np.newaxis, :]) @ u_r.T
    gt_cinv_g = leadfield.T @ cov_pinv @ leadfield
    alpha = float(np.trace(gt_cinv_g)) / n_sources * 0.1 + 1e-6
    res_matrix = np.linalg.inv(gt_cinv_g + alpha * np.eye(n_sources)) @ gt_cinv_g
    
    res_diag = np.clip(np.diag(res_matrix), 0.0, 1.0)
    target_res = float(np.mean(res_diag[target_indices]))
    
    # Certificate: resolution fraction penalized by cross-ambiguity
    certificate = float(np.clip(target_res * (1.0 - worst_case_rho), 0.0, 1.0))
    
    return ObservabilityReport(
        certificate=round(certificate, 4),
        worst_case_ambiguity=round(worst_case_rho, 4),
        min_residual=round(min_residual, 4),
        supported_rank=rank,
        resolution_fraction=round(target_res, 4),
    )


# Illustrative 10-20 montage prior for examples and tests. These values are
# not derived from an anatomical forward model.
# Source 0: Centroparietal P3b generator (bilateral temporoparietal / parietal)
# Source 1: Frontal P3a generator (anterior cingulate / medial prefrontal)
# Source 2: Ocular artifact generator (corneo-retinal blink dipole)
# Source 3: Temporalis muscle / lateral artifact generator
_CANONICAL_1020_COEFFICIENTS: dict[str, list[float]] = {
    # Channel: [P3b, P3a, Ocular, Temporalis]
    "Fz":   [ 0.15,  0.85,  0.92,  0.10 ],
    "Cz":   [ 0.65,  0.70,  0.35,  0.12 ],
    "Pz":   [ 0.95,  0.30,  0.08,  0.08 ],
    "Oz":   [ 0.70,  0.10, -0.05,  0.05 ],
    "CPz":  [ 0.88,  0.55,  0.18,  0.09 ],
    "C3":   [ 0.55,  0.45,  0.25,  0.45 ],
    "C4":   [ 0.55,  0.45,  0.25,  0.45 ],
    "P3":   [ 0.82,  0.22,  0.06,  0.30 ],
    "P4":   [ 0.82,  0.22,  0.06,  0.30 ],
    "PO7":  [ 0.65,  0.08, -0.04,  0.55 ],
    "PO8":  [ 0.65,  0.08, -0.04,  0.55 ],
    "F3":   [ 0.20,  0.72,  0.80,  0.40 ],
    "F4":   [ 0.20,  0.72,  0.80,  0.40 ],
    "T7":   [ 0.30,  0.15,  0.15,  0.90 ],
    "T8":   [ 0.30,  0.15,  0.15,  0.90 ],
}


def get_canonical_p300_proxy(channel_names: list[str]) -> np.ndarray:
    """Return an illustrative channel-name proxy, not a physical leadfield.

    Returns a matrix of shape ``(len(channel_names), 4)`` for code examples.
      Col 0: P3b (Parietal ERP target)
      Col 1: P3a (Frontal ERP target)
      Col 2: Ocular artifact (Blinks)
      Col 3: Temporalis muscle artifact
    """
    rows = []
    for name in channel_names:
        clean = name.strip()
        if clean in _CANONICAL_1020_COEFFICIENTS:
            rows.append(_CANONICAL_1020_COEFFICIENTS[clean])
        else:
            # Fallback estimation based on 10-20 naming heuristics
            if "P" in clean or "O" in clean:
                rows.append([0.75, 0.20, 0.05, 0.20])
            elif "F" in clean:
                rows.append([0.20, 0.75, 0.70, 0.20])
            else:
                rows.append([0.50, 0.50, 0.30, 0.30])
    return np.array(rows, dtype=float)


def get_canonical_p300_leadfield(channel_names: list[str]) -> np.ndarray:
    """Deprecated alias for :func:`get_canonical_p300_proxy`."""
    return get_canonical_p300_proxy(channel_names)
