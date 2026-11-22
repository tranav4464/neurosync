"""Neurosync low-channel P300 speller prototype."""

from .data import EEGDataset, load_npz, save_npz
from .decoder import DecoderConfig, decode_dataset
from .model import DiagonalLDA
from .preprocessing import preprocess_epochs
from .quality import ContactQualityGate, QualityAssessment
from .evaluation import NonInferiorityResult, SafeMetrics, assess_noninferiority, safe_metrics
from .calibration import DecisionCalibration, TemperatureCalibration, calibrate_decision_oof

__all__ = [
    "EEGDataset",
    "load_npz",
    "save_npz",
    "DecoderConfig",
    "decode_dataset",
    "DiagonalLDA",
    "preprocess_epochs",
    "ContactQualityGate",
    "QualityAssessment",
    "NonInferiorityResult",
    "SafeMetrics",
    "assess_noninferiority",
    "safe_metrics",
    "DecisionCalibration",
    "TemperatureCalibration",
    "calibrate_decision_oof",
]

