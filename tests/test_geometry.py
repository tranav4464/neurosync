import unittest
import numpy as np

from neurosync_p300.geometry import (
    _psd_eigh,
    average_reference_operator,
    whitened_unit_signatures,
    absolute_cosine_ambiguity,
    compute_observability_certificate,
    get_canonical_p300_proxy,
    get_canonical_p300_leadfield,
)


class TestGeometry(unittest.TestCase):
    def test_psd_eigh_rank_deficient(self):
        # Create rank-deficient covariance (rank 3 in 4D)
        A = np.random.default_rng(42).standard_normal((4, 3))
        cov = A @ A.T
        u_r, lambda_r = _psd_eigh(cov, rcond=1e-5)
        self.assertEqual(len(lambda_r), 3)
        self.assertEqual(u_r.shape, (4, 3))
        # Reconstruction within tolerance
        reconstructed = u_r @ np.diag(lambda_r) @ u_r.T
        np.testing.assert_allclose(cov, reconstructed, atol=1e-5)

    def test_average_reference_projection(self):
        proj = average_reference_operator(4)
        v = np.array([1.0, 2.0, 3.0, 4.0])
        ref_v = proj @ v
        self.assertAlmostEqual(float(np.mean(ref_v)), 0.0, places=6)

    def test_observability_certificate(self):
        channels = ["Pz", "CPz", "Oz", "Fz"]
        leadfield = get_canonical_p300_leadfield(channels)
        cov = np.eye(4)
        report = compute_observability_certificate(leadfield, cov)
        self.assertGreater(report.certificate, 0.0)
        self.assertLessEqual(report.certificate, 1.0)
        self.assertGreaterEqual(report.worst_case_ambiguity, 0.0)
        self.assertLessEqual(report.worst_case_ambiguity, 1.0)
        self.assertEqual(report.supported_rank, 4)

    def test_proxy_alias_is_explicit_and_backward_compatible(self):
        channels = ["Pz", "CPz", "Oz", "Fz"]
        np.testing.assert_allclose(
            get_canonical_p300_proxy(channels),
            get_canonical_p300_leadfield(channels),
        )


if __name__ == "__main__":
    unittest.main()
