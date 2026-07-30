from __future__ import annotations

import unittest

from heimdall.hil_validation import HilTestPlan, HilTestResult, validate_hil_result


def plan() -> HilTestPlan:
    return HilTestPlan("hil-001", "device", "firmware", "certificate", "input", "expected", "environment", "safety")


class HilValidationTests(unittest.TestCase):
    def test_result_binds_hardware_configuration_to_plan(self) -> None:
        validate_hil_result(plan(), HilTestResult("hil-001", "device", "firmware", "certificate", "output", ("measurement",), True, "fixture only"))

    def test_mismatched_firmware_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "configuration"):
            validate_hil_result(plan(), HilTestResult("hil-001", "device", "other", "certificate", "output", ("measurement",), True, "fixture"))


if __name__ == "__main__":
    unittest.main()
