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


class ShrinkageLDA:
    """Full-covariance LDA with diagonal shrinkage and stable linear solves.

    This captures correlated spatiotemporal ERP structure that diagonal LDA
    intentionally ignores.  Shrinkage keeps the model identifiable for sparse
    calibration sets without using test labels.
    """

    def __init__(self, *, shrinkage: float = 0.35, class_prior: tuple[float, float] = (0.5, 0.5)):
        self.shrinkage = float(shrinkage)
        self.class_prior = np.asarray(class_prior, dtype=float)
        if not 0.0 <= self.shrinkage <= 1.0:
            raise ValueError("shrinkage must be between 0 and 1")

    def fit(self, X: np.ndarray, y: np.ndarray) -> "ShrinkageLDA":
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=int)
        if X.ndim != 2 or len(X) != len(y) or set(np.unique(y)) != {0, 1}:
            raise ValueError("X must be 2-D with both binary classes")
        self.center_ = X.mean(axis=0)
        scale = X.std(axis=0, ddof=1)
        self.scale_ = np.maximum(scale, np.median(scale[scale > 0]) * 1e-4 if np.any(scale > 0) else 1.0)
        Z = (X - self.center_) / self.scale_
        self.means_ = np.vstack([Z[y == label].mean(axis=0) for label in (0, 1)])
        residuals = np.vstack([Z[y == label] - self.means_[label] for label in (0, 1)])
        covariance = residuals.T @ residuals / max(len(residuals) - 2, 1)
        diagonal = np.diag(np.diag(covariance))
        covariance = (1.0 - self.shrinkage) * covariance + self.shrinkage * diagonal
        ridge = max(float(np.trace(covariance) / covariance.shape[0]) * 1e-6, 1e-8)
        covariance += ridge * np.eye(covariance.shape[0])
        difference = self.means_[1] - self.means_[0]
        self.weights_ = np.linalg.solve(covariance, difference)
        self.intercept_ = (
            -0.5 * float((self.means_[1] + self.means_[0]) @ self.weights_)
            + float(np.log(self.class_prior[1] / self.class_prior[0]))
        )
        return self

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        if not hasattr(self, "weights_"):
            raise RuntimeError("fit the classifier before scoring")
        Z = (np.asarray(X, dtype=float) - self.center_) / self.scale_
        return Z @ self.weights_ + self.intercept_

    def predict(self, X: np.ndarray) -> np.ndarray:
        return (self.decision_function(X) >= 0).astype(int)

