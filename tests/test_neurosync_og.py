from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from neurosync_p300.forward_model import ForwardModel, load_forward_model
from neurosync_p300.geometry import get_canonical_p300_proxy
from neurosync_p300.session import train_and_decode
from neurosync_p300.synthetic import generate_synthetic_dataset


class NeuroSyncOGTests(unittest.TestCase):
    def test_forward_model_alignment_is_name_safe(self):
        model = ForwardModel(
            leadfield=np.arange(12, dtype=float).reshape(3, 4),
            channel_names=("Fz", "Cz", "Pz"),
            source_labels=("P3b", "P3a", "ocular", "muscle"),
        ).validate()
        aligned = model.align(["Pz", "Fz"])
        np.testing.assert_array_equal(aligned, model.leadfield[[2, 0]])
        with self.assertRaises(ValueError):
            model.align(["Oz"])

    def test_forward_model_npz_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forward.npz"
            np.savez(
                path,
                leadfield=np.eye(4),
                channel_names=np.asarray(["Fz", "Cz", "Pz", "Oz"]),
                source_labels=np.asarray(["P3b", "P3a", "ocular", "muscle"]),
                provenance_model=np.asarray("template-BEM"),
            )
            loaded = load_forward_model(path)
            self.assertEqual(loaded.provenance["model"], "template-BEM")
            self.assertEqual(loaded.leadfield.shape, (4, 4))

    def test_end_to_end_external_geometry_path(self):
        train = generate_synthetic_dataset(n_trials=16, repetitions=3, seed=51)
        test = generate_synthetic_dataset(n_trials=4, repetitions=3, seed=52)
        model = ForwardModel(
            leadfield=get_canonical_p300_proxy(train.channel_names),
            channel_names=tuple(train.channel_names),
            provenance={"model": "test-only-proxy"},
        )
        result = train_and_decode(
            train,
            test,
            min_channels=4,
            max_channels=4,
            forward_model=model,
            calibrate_temperature=False,
        )
        self.assertEqual(len(result.selection.indices), 4)
        self.assertEqual(result.selection.geometry_source, "test-only-proxy")
        self.assertTrue(all(0.0 <= item.mean_evidence_weight <= 1.0 for item in result.decoded))


if __name__ == "__main__":
    unittest.main()
