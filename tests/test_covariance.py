from __future__ import annotations

import unittest

from heimdall.covariance import validate_covariance_3x3


class CovarianceTests(unittest.TestCase):
    def test_accepts_symmetric_positive_semidefinite_matrix(self) -> None:
        validate_covariance_3x3((1, 0, 0, 0, 1, 0, 0, 0, 1))

    def test_rejects_asymmetric_or_indefinite_matrix(self) -> None:
        with self.assertRaisesRegex(ValueError, "symmetric"):
            validate_covariance_3x3((1, 1, 0, 0, 1, 0, 0, 0, 1))
        with self.assertRaisesRegex(ValueError, "semidefinite"):
            validate_covariance_3x3((1, 2, 0, 2, 1, 0, 0, 0, 1))


if __name__ == "__main__":
    unittest.main()
