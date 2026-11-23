"""Neurosync low-channel P300 speller prototype."""

from .data import EEGDataset, load_npz, save_npz
from .decoder import DecoderConfig, decode_dataset
from .model import DiagonalLDA, ShrinkageLDA
from .preprocessing import preprocess_epochs
from .quality import ContactQualityGate, QualityAssessment
from .evaluation import NonInferiorityResult, SafeMetrics, assess_noninferiority, safe_metrics
from .calibration import DecisionCalibration, TemperatureCalibration, calibrate_decision_oof
from .channel_selection import forward_select_channels, biophysically_regularized_channel_selection
from .geometry import (
    ObservabilityReport,
    _psd_eigh,
    average_reference_operator,
    whitened_unit_signatures,
    absolute_cosine_ambiguity,
    compute_observability_certificate,
    audit_single_channel_dropout,
    get_canonical_p300_proxy,
    get_canonical_p300_leadfield,
)
from .spatial import TemplateSpatialFilter, SubspaceWhitenedSpatialFilter
from .forward_model import ForwardModel, load_forward_model

__all__ = [
    "EEGDataset",
    "load_npz",
    "save_npz",
    "DecoderConfig",
    "decode_dataset",
    "DiagonalLDA",
    "ShrinkageLDA",
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
    "forward_select_channels",
    "biophysically_regularized_channel_selection",
    "ObservabilityReport",
    "_psd_eigh",
    "average_reference_operator",
    "whitened_unit_signatures",
    "absolute_cosine_ambiguity",
    "compute_observability_certificate",
    "audit_single_channel_dropout",
    "get_canonical_p300_proxy",
    "get_canonical_p300_leadfield",
    "TemplateSpatialFilter",
    "SubspaceWhitenedSpatialFilter",
    "ForwardModel",
    "load_forward_model",
]

