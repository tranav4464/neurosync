from __future__ import annotations

import unittest

import numpy as np

from neurosync_p300.channel_selection import forward_select_channels, stability_select_channels
from neurosync_p300.calibration import calibrate_decision_oof, calibrate_temperature_oof
from neurosync_p300.benchmark import benchmark_wet_reference_vs_casp
from neurosync_p300.bigp3bci_data import _rising_edges, _trial_blocks
from neurosync_p300.bigp3bci_benchmark import _roc_auc
from neurosync_p300.decoder import DecodedTrial, DecoderConfig, decode_dataset, summarize_decoding
from neurosync_p300.evaluation import assess_noninferiority, safe_metrics
from neurosync_p300.features import extract_features
from neurosync_p300.model import DiagonalLDA, ShrinkageLDA
from neurosync_p300.preprocessing import preprocess_epochs
from neurosync_p300.quality import ContactQualityGate, QualityAssessment, apply_channel_quality
from neurosync_p300.spatial import TemplateSpatialFilter
from neurosync_p300.feature_selection import StandardizedMeanFeatureSelector
from neurosync_p300.synthetic import generate_synthetic_dataset, inject_contact_artifacts


class CoreTests(unittest.TestCase):
    def test_preprocessing_preserves_shape_and_removes_baseline(self):
        dataset = generate_synthetic_dataset(n_trials=2, repetitions=2, seed=1)
        clean = preprocess_epochs(dataset.epochs, dataset.sampling_rate)
        self.assertEqual(clean.shape, dataset.epochs.shape)
        baseline_samples = int(round(0.2 * dataset.sampling_rate))
        baseline = clean[..., :baseline_samples].mean(axis=-1)
        self.assertLess(float(np.mean(np.abs(baseline))), 0.12)

    def test_lda_learns_a_separable_signal(self):
        rng = np.random.default_rng(2)
        X = rng.normal(size=(100, 1))
        y = np.array([0] * 50 + [1] * 50)
        X[50:, 0] += 2.5
        model = DiagonalLDA().fit(X, y)
        self.assertGreater(float(np.mean(model.predict(X) == y)), 0.90)

    def test_shrinkage_lda_uses_correlated_features(self):
        rng = np.random.default_rng(2026)
        y = np.repeat([0, 1], 80)
        latent = rng.normal(size=(160, 1))
        X = np.hstack([latent + rng.normal(scale=0.2, size=(160, 1)) for _ in range(6)])
        X[y == 1, :3] += 0.9
        model = ShrinkageLDA(shrinkage=0.10).fit(X, y)
        self.assertGreater(float(np.mean(model.predict(X) == y)), 0.75)

    def test_channel_selection_returns_compact_set(self):
        dataset = generate_synthetic_dataset(n_trials=18, repetitions=3, seed=3, electrode_type="dry")
        clean = preprocess_epochs(dataset.epochs, dataset.sampling_rate)
        selection = forward_select_channels(
            clean,
            dataset.labels,
            dataset.trial_ids,
            dataset.channel_names,
            dataset.sampling_rate,
            min_channels=4,
            max_channels=6,
            seed=3,
        )
        self.assertGreaterEqual(len(selection.indices), 4)
        self.assertLessEqual(len(selection.indices), 6)
        self.assertEqual(len(set(selection.indices)), len(selection.indices))

    def test_stability_channel_selection_returns_compact_set(self):
        dataset = generate_synthetic_dataset(n_trials=6, repetitions=3, seed=33, electrode_type="dry")
        clean = preprocess_epochs(dataset.epochs, dataset.sampling_rate)
        selection = stability_select_channels(
            clean, dataset.labels, dataset.trial_ids, dataset.channel_names,
            dataset.sampling_rate, channels=4,
        )
        self.assertEqual(len(selection.indices), 4)
        self.assertEqual(len(set(selection.indices)), 4)

    def test_template_spatial_filter_reduces_channel_dimension(self):
        dataset = generate_synthetic_dataset(n_trials=12, repetitions=3, seed=31, electrode_type="dry")
        clean = preprocess_epochs(dataset.epochs, dataset.sampling_rate)
        spatial = TemplateSpatialFilter(n_components=3).fit(clean, dataset.labels)
        transformed = spatial.transform(clean)
        self.assertEqual(transformed.shape, (len(clean), 3, dataset.n_samples))
        self.assertTrue(np.isfinite(transformed).all())

    def test_template_spatial_filter_is_fit_on_training_signal(self):
        rng = np.random.default_rng(52)
        labels = np.array([0] * 30 + [1] * 30)
        epochs = rng.normal(size=(60, 4, 40))
        epochs[labels == 1, 2, 15:25] += 1.5
        spatial = TemplateSpatialFilter(n_components=2).fit(epochs, labels)
        transformed = spatial.transform(epochs)
        # A supervised projection should retain a target/non-target difference.
        difference = transformed[labels == 1].mean(axis=(0, 2)) - transformed[labels == 0].mean(axis=(0, 2))
        self.assertGreater(float(np.max(np.abs(difference))), 0.10)

    def test_bigp3bci_status_helpers_preserve_trial_boundaries(self):
        pulses = np.array([0, 1, 1, 0, 0, 1, 0])
        self.assertListEqual(_rising_edges(pulses).tolist(), [1, 5])
        targets = np.array([0, 7, 7, 0, 3, 3, 3, 0])
        self.assertListEqual(_trial_blocks(targets), [(1, 3, 7), (4, 7, 3)])

    def test_bigp3bci_auc_handles_perfect_and_tied_scores(self):
        self.assertEqual(_roc_auc(np.array([0, 0, 1, 1]), np.array([0.1, 0.2, 0.8, 0.9])), 1.0)
        self.assertEqual(_roc_auc(np.array([0, 0, 1, 1]), np.ones(4)), 0.5)

    def test_sparse_feature_selector_uses_training_ranked_features(self):
        rng = np.random.default_rng(32)
        features = rng.normal(size=(20, 8))
        labels = np.array([0] * 10 + [1] * 10)
        features[labels == 1, 3] += 3.0
        selector = StandardizedMeanFeatureSelector(max_features=3).fit(features, labels)
        transformed = selector.transform(features)
        self.assertEqual(transformed.shape, (20, 3))
        self.assertIn(3, selector.indices_)

    def test_decoder_can_accumulate_symbol_evidence(self):
        train = generate_synthetic_dataset(n_trials=20, repetitions=4, seed=4, electrode_type="wet")
        test = generate_synthetic_dataset(n_trials=5, repetitions=4, seed=5, electrode_type="wet")
        train_clean = preprocess_epochs(train.epochs, train.sampling_rate)
        test_clean = preprocess_epochs(test.epochs, test.sampling_rate)
        train_features = extract_features(train_clean, train.sampling_rate)
        test_features = extract_features(test_clean, test.sampling_rate)
        model = DiagonalLDA().fit(train_features, train.labels)
        decoded = decode_dataset(
            model,
            test_features,
            test,
            config=DecoderConfig(min_repetitions=2, max_repetitions=4, stability_repetitions=2),
        )
        metrics = summarize_decoding(decoded)
        self.assertEqual(len(decoded), test.trial_count)
        self.assertGreaterEqual(metrics["accuracy"], 0.40)

    def test_contact_quality_drops_for_injected_artifacts(self):
        dataset = generate_synthetic_dataset(n_trials=10, repetitions=3, seed=8, electrode_type="dry")
        corrupted = inject_contact_artifacts(dataset, fraction=0.30, seed=9)
        gate = ContactQualityGate().fit(dataset.epochs, dataset.sampling_rate)
        clean_quality = gate.assess(dataset.epochs, dataset.sampling_rate)
        corrupted_quality = gate.assess(corrupted.epochs, corrupted.sampling_rate)
        self.assertLess(float(np.mean(corrupted_quality.epoch_quality)), float(np.mean(clean_quality.epoch_quality)))
        clean = preprocess_epochs(dataset.epochs, dataset.sampling_rate)
        features = extract_features(clean, dataset.sampling_rate)
        weighted = apply_channel_quality(features, clean_quality.channel_quality)
        self.assertEqual(features.shape, weighted.shape)

    def test_low_quality_data_requests_headset_reseat(self):
        train = generate_synthetic_dataset(n_trials=12, repetitions=3, seed=10)
        test = generate_synthetic_dataset(n_trials=3, repetitions=3, seed=11)
        train_features = extract_features(preprocess_epochs(train.epochs, train.sampling_rate), train.sampling_rate)
        test_features = extract_features(preprocess_epochs(test.epochs, test.sampling_rate), test.sampling_rate)
        model = DiagonalLDA().fit(train_features, train.labels)
        bad_quality = QualityAssessment(
            channel_quality=np.zeros((len(test.epochs), test.n_channels)),
            epoch_quality=np.zeros(len(test.epochs)),
            low_frequency_ratio=np.zeros((len(test.epochs), test.n_channels)),
            line_noise_ratio=np.zeros((len(test.epochs), test.n_channels)),
            peak_to_peak=np.zeros((len(test.epochs), test.n_channels)),
        )
        decoded = decode_dataset(
            model,
            test_features,
            test,
            config=DecoderConfig(min_repetitions=2, max_repetitions=3, reseat_after_bad_repetitions=2),
            quality=bad_quality,
        )
        self.assertTrue(all(item.action == "RESEAT_HEADSET" for item in decoded))

    def test_oof_temperature_calibration_returns_declared_candidate(self):
        dataset = generate_synthetic_dataset(n_trials=12, repetitions=3, seed=12)
        features = extract_features(preprocess_epochs(dataset.epochs, dataset.sampling_rate), dataset.sampling_rate)
        calibration = calibrate_temperature_oof(features, dataset.labels, dataset.trial_ids, symbols=dataset.symbols)
        self.assertIn(calibration.temperature, calibration.candidates_tested)
        self.assertGreaterEqual(calibration.validation_log_loss, 0.0)

    def test_oof_decision_calibration_returns_bounded_thresholds(self):
        dataset = generate_synthetic_dataset(n_trials=12, repetitions=3, seed=15)
        features = extract_features(preprocess_epochs(dataset.epochs, dataset.sampling_rate), dataset.sampling_rate)
        calibration = calibrate_decision_oof(features, dataset.labels, dataset.trial_ids, dataset.symbols)
        self.assertGreaterEqual(calibration.confidence_threshold, 0.0)
        self.assertLessEqual(calibration.confidence_threshold, 1.0)
        self.assertGreaterEqual(calibration.coverage, 0.0)

    def test_noninferiority_uses_accepted_output_not_raw_abstention(self):
        reference = [
            DecodedTrial(i, "A", 3, 0.9, 0.5, False, {"A": 1.0}, action="ACCEPT", true_symbol="A")
            for i in range(10)
        ]
        candidate = [
            DecodedTrial(i, "A", 3, 0.9, 0.5, False, {"A": 1.0}, action="ACCEPT", true_symbol="A")
            for i in range(10)
        ]
        result = assess_noninferiority(reference, candidate, margin=0.05, bootstrap_samples=100, seed=1)
        self.assertEqual(result.conclusion, "NON_INFERIOR")
        metric = safe_metrics(candidate)
        self.assertEqual(metric.correct_accept_rate, 1.0)

    def test_paired_benchmark_returns_a_bounded_conclusion(self):
        train = generate_synthetic_dataset(n_trials=12, repetitions=3, seed=13, electrode_type="wet")
        test = generate_synthetic_dataset(n_trials=4, repetitions=3, seed=14, electrode_type="wet")
        report = benchmark_wet_reference_vs_casp(
            train,
            test,
            train,
            test,
            fixed_repetitions=3,
            noninferiority_margin=0.10,
        )
        self.assertIn(report["noninferiority"]["conclusion"], {"NON_INFERIOR", "INCONCLUSIVE_OR_NOT_NONINFERIOR"})


if __name__ == "__main__":
    unittest.main()

