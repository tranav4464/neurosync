"""Small, interpretable classifiers suitable for a P300 prototype."""

from __future__ import annotations

import numpy as np


class DiagonalLDA:
    """Regularized diagonal Linear Discriminant Analysis.

    The classifier models target and non-target means but uses a diagonal
    pooled covariance. That keeps the six-channel prototype stable with few
    training trials and makes the feature weights inspectable.
    """

    def __init__(self, *, shrinkage: float = 0.15, class_prior: tuple[float, float] = (0.5, 0.5)):
        self.shrinkage = float(shrinkage)
        self.class_prior = np.asarray(class_prior, dtype=float)
        if self.shrinkage < 0 or self.shrinkage > 1:
            raise ValueError("shrinkage must be between 0 and 1")
        if np.any(self.class_prior <= 0):
            raise ValueError("class priors must be positive")
        self.fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray) -> "DiagonalLDA":
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=int)
        if X.ndim != 2 or len(X) != len(y):
            raise ValueError("X must be 2-D and have the same number of rows as y")
        if set(np.unique(y)) != {0, 1}:
            raise ValueError("both target and non-target examples are required")

        self.means_ = np.vstack([X[y == 0].mean(axis=0), X[y == 1].mean(axis=0)])
        variances = np.vstack([
            X[y == 0].var(axis=0, ddof=1),
            X[y == 1].var(axis=0, ddof=1),
        ])
        pooled = 0.5 * (variances[0] + variances[1])
        reference = float(np.median(pooled[pooled > 0])) if np.any(pooled > 0) else 1.0
        pooled = (1.0 - self.shrinkage) * pooled + self.shrinkage * reference
        self.variances_ = np.maximum(pooled, reference * 1e-5)
        self.weights_ = (self.means_[1] - self.means_[0]) / self.variances_
        self.intercept_ = (
            -0.5 * np.sum((self.means_[1] ** 2 - self.means_[0] ** 2) / self.variances_)
            + np.log(self.class_prior[1] / self.class_prior[0])
        )
        self.fitted = True
        return self

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        if not self.fitted:
            raise RuntimeError("fit the classifier before scoring")
        X = np.asarray(X, dtype=float)
        return X @ self.weights_ + self.intercept_

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        scores = np.clip(self.decision_function(X), -60, 60)
        probability_target = 1.0 / (1.0 + np.exp(-scores))
        return np.column_stack([1.0 - probability_target, probability_target])

    def predict(self, X: np.ndarray) -> np.ndarray:
        return (self.decision_function(X) >= 0).astype(int)

