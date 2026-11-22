"""Training-only sparse feature selection for a SWLDA-inspired ablation."""

from __future__ import annotations

import numpy as np


class StandardizedMeanFeatureSelector:
    """Keep features with the strongest standardized target/non-target shift.

    This deliberately small selector captures the feature-sparsity idea behind
    SWLDA without representing itself as a statistical SWLDA reproduction.
    It is fit only on a training partition and has no test-label access.
    """

    def __init__(self, *, max_features: int = 48):
        self.max_features = int(max_features)

    def fit(self, features: np.ndarray, labels: np.ndarray) -> "StandardizedMeanFeatureSelector":
        X = np.asarray(features, dtype=float)
        y = np.asarray(labels, dtype=int)
        if X.ndim != 2 or len(X) != len(y):
            raise ValueError("features must be 2-D with matching labels")
        if set(np.unique(y)) != {0, 1}:
            raise ValueError("both classes are required")
        if not 1 <= self.max_features <= X.shape[1]:
            raise ValueError("max_features must fit the feature dimension")
        target, non_target = X[y == 1], X[y == 0]
        pooled = 0.5 * (target.var(axis=0, ddof=1) + non_target.var(axis=0, ddof=1))
        effect = np.abs(target.mean(axis=0) - non_target.mean(axis=0)) / np.sqrt(np.maximum(pooled, 1e-10))
        self.indices_ = np.sort(np.argsort(effect)[::-1][: self.max_features])
        self.effect_sizes_ = effect[self.indices_]
        return self

    def transform(self, features: np.ndarray) -> np.ndarray:
        if not hasattr(self, "indices_"):
            raise RuntimeError("fit the feature selector before transforming")
        X = np.asarray(features, dtype=float)
        if X.ndim != 2:
            raise ValueError("features must be 2-D")
        return X[:, self.indices_]
