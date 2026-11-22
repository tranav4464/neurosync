"""Paired wet-reference versus sparse-CASP benchmark utilities."""

from __future__ import annotations

from dataclasses import asdict

from .data import EEGDataset
from .decoder import DecoderConfig
from .evaluation import assess_noninferiority, as_dict, safe_metrics
from .session import train_and_decode


def _targets_by_trial(dataset: EEGDataset) -> dict[int, str]:
    dataset.validate()
    targets: dict[int, str] = {}
    for trial_id in set(dataset.trial_ids.tolist()):
        indices = dataset.trial_ids == trial_id
        target = set(dataset.symbols[indices][dataset.labels[indices] == 1].tolist())
        if len(target) != 1:
            raise ValueError("each benchmark trial must contain one unique labelled target symbol")
        targets[int(trial_id)] = str(next(iter(target)))
    return targets


def benchmark_wet_reference_vs_casp(
    wet_train: EEGDataset,
    wet_test: EEGDataset,
    sparse_train: EEGDataset,
    sparse_test: EEGDataset,
    *,
    fixed_repetitions: int = 6,
    noninferiority_margin: float = 0.05,
    spatial_filter_components: int = 0,
    sparse_feature_count: int = 0,
) -> dict:
    """Run a paired engineering comparison with a common trial endpoint.

    The wet arm uses every available wet channel; the CASP arm selects 4–6
    sparse channels and applies contact-aware gating. Test trials must have
    the same IDs and targets in both arms, typically from a counterbalanced
    within-person wet/dry recording protocol.
    """

    if _targets_by_trial(wet_test) != _targets_by_trial(sparse_test):
        raise ValueError("wet and sparse test sets must share trial IDs and target symbols")
    reference = train_and_decode(
        wet_train,
        wet_test,
        min_channels=wet_train.n_channels,
        max_channels=wet_train.n_channels,
        decoder_config=DecoderConfig(max_repetitions=fixed_repetitions),
        fixed_repetitions=fixed_repetitions,
        contact_aware=False,
    )
    casp = train_and_decode(
        sparse_train,
        sparse_test,
        min_channels=4,
        max_channels=min(6, sparse_train.n_channels),
        decoder_config=DecoderConfig(max_repetitions=fixed_repetitions),
        fixed_repetitions=fixed_repetitions,
        contact_aware=True,
        quality_weighting=False,
        spatial_filter_components=spatial_filter_components,
        sparse_feature_count=sparse_feature_count,
    )
    comparison = assess_noninferiority(
        reference.decoded,
        casp.decoded,
        margin=noninferiority_margin,
    )
    return {
        "comparison_type": "engineering-only paired non-inferiority screen",
        "reference": {
            "channels": reference.selection.names,
            "metrics": reference.metrics,
            "safe_metrics": as_dict(safe_metrics(reference.decoded)),
            "temperature": reference.calibration.temperature if reference.calibration else None,
        },
        "casp": {
            "channels": casp.selection.names,
            "metrics": casp.metrics,
            "safe_metrics": as_dict(safe_metrics(casp.decoded)),
            "temperature": casp.calibration.temperature if casp.calibration else None,
        },
        "noninferiority": asdict(comparison),
        "claim_boundary": "This comparison is not a clinical conclusion. It requires a pre-registered protocol, adequate sample size, and an independent held-out human cohort.",
    }

