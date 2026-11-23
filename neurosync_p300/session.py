"""End-to-end training and decoding for recorded NPZ sessions."""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from .channel_selection import (
    ChannelSelectionResult,
    biophysically_regularized_channel_selection,
    forward_select_channels,
)
from .data import EEGDataset
from .decoder import DecodedTrial, DecoderConfig, decode_dataset, summarize_decoding
from .features import extract_features
from .model import DiagonalLDA
from .preprocessing import preprocess_epochs
from .quality import ContactQualityGate, apply_channel_quality
from .calibration import DecisionCalibration, calibrate_decision_oof
from .spatial import TemplateSpatialFilter
from .feature_selection import StandardizedMeanFeatureSelector
from .forward_model import ForwardModel


@dataclass
class SessionResult:
    selection: ChannelSelectionResult
    model: DiagonalLDA
    decoded: list[DecodedTrial]
    metrics: dict[str, float]
    calibration: DecisionCalibration | None = None


def train_and_decode(
    train: EEGDataset,
    test: EEGDataset,
    *,
    min_channels: int = 4,
    max_channels: int = 6,
    decoder_config: DecoderConfig | None = None,
    fixed_repetitions: int | None = None,
    contact_aware: bool = True,
    quality_weighting: bool = False,
    spatial_filter_components: int = 0,
    sparse_feature_count: int = 0,
    calibrate_temperature: bool = True,
    forward_model: ForwardModel | None = None,
) -> SessionResult:
    """Preprocess, select channels, fit LDA, and decode a held-out session."""

    train.validate()
    test.validate()
    if train.channel_names != test.channel_names:
        raise ValueError("train and test channel names/order must match")
    if train.sampling_rate != test.sampling_rate:
        raise ValueError("train and test sampling rates must match")

    train_clean = preprocess_epochs(train.epochs, train.sampling_rate)
    test_clean = preprocess_epochs(test.epochs, test.sampling_rate)
    train_quality_full = None
    test_quality_full = None
    if contact_aware:
        quality_gate = ContactQualityGate().fit(train.epochs, train.sampling_rate)
        train_quality_full = quality_gate.assess(train.epochs, train.sampling_rate)
        test_quality_full = quality_gate.assess(test.epochs, test.sampling_rate)
    if forward_model is not None:
        aligned_leadfield = forward_model.validate().align(train.channel_names)
        channel_reliability = (
            np.median(train_quality_full.channel_quality, axis=0)
            if train_quality_full is not None
            else np.ones(train.n_channels)
        )
        selection = biophysically_regularized_channel_selection(
            train_clean,
            train.labels,
            train.trial_ids,
            train.channel_names,
            train.sampling_rate,
            leadfield=aligned_leadfield,
            channel_reliability=channel_reliability,
            geometry_source=forward_model.provenance.get("model", "external_forward_model"),
            target_indices=list(forward_model.target_indices),
            artifact_indices=list(forward_model.artifact_indices) or None,
            min_channels=min_channels,
            max_channels=max_channels,
        )
        selected_leadfield = aligned_leadfield[selection.indices, :]
    else:
        selection = forward_select_channels(
            train_clean,
            train.labels,
            train.trial_ids,
            train.channel_names,
            train.sampling_rate,
            min_channels=min_channels,
            max_channels=max_channels,
        )
        selected_leadfield = None
    selected_train = train_clean[:, selection.indices, :]
    selected_test = test_clean[:, selection.indices, :]
    if spatial_filter_components:
        component_count = min(spatial_filter_components, len(selection.indices))
        spatial_filter = TemplateSpatialFilter(n_components=component_count).fit(selected_train, train.labels)
        selected_train = spatial_filter.transform(selected_train)
        selected_test = spatial_filter.transform(selected_test)
    train_features = extract_features(selected_train, train.sampling_rate)
    test_features = extract_features(selected_test, test.sampling_rate)
    if sparse_feature_count:
        selector = StandardizedMeanFeatureSelector(max_features=min(sparse_feature_count, train_features.shape[1]))
        train_features = selector.fit(train_features, train.labels).transform(train_features)
        test_features = selector.transform(test_features)
    test_quality = None
    if contact_aware and train_quality_full is not None and test_quality_full is not None:
        train_quality = train_quality_full.select_channels(selection.indices)
        test_quality = test_quality_full.select_channels(selection.indices)
        if quality_weighting:
            if spatial_filter_components:
                train_features *= np.sqrt(train_quality.epoch_quality)[:, None]
                test_features *= np.sqrt(test_quality.epoch_quality)[:, None]
            else:
                train_features = apply_channel_quality(train_features, train_quality.channel_quality)
                test_features = apply_channel_quality(test_features, test_quality.channel_quality)
    calibration = None
    if calibrate_temperature:
        calibration = calibrate_decision_oof(
            train_features,
            train.labels,
            train.trial_ids,
            train.symbols,
        )
        decoder_config = replace(
            decoder_config or DecoderConfig(),
            temperature=calibration.temperature,
            confidence_threshold=calibration.confidence_threshold,
            margin_threshold=calibration.margin_threshold,
        )
    model = DiagonalLDA(shrinkage=0.20).fit(train_features, train.labels)
    selected_test = test.select_channels(selection.indices)
    decoded = decode_dataset(
        model,
        test_features,
        selected_test,
        config=decoder_config,
        fixed_repetitions=fixed_repetitions,
        quality=test_quality,
        leadfield=selected_leadfield,
        target_indices=list(forward_model.target_indices) if forward_model is not None else None,
        artifact_indices=(list(forward_model.artifact_indices) or None) if forward_model is not None else None,
    )
    return SessionResult(selection, model, decoded, summarize_decoding(decoded), calibration)

