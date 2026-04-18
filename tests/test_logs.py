from __future__ import annotations

from pathlib import Path
import unittest

from dependabot_rescue.logs import classify_logs
from dependabot_rescue.models import DependencyUpdate


FIXTURES = Path(__file__).parent / "fixtures"


class LogClassificationTests(unittest.TestCase):
    def test_classifies_import_and_test_failures(self) -> None:
        log_text = (FIXTURES / "python_import_error.log").read_text(encoding="utf-8")
        updates = [DependencyUpdate(package="requests", from_version="2.31.0", to_version="2.32.0")]

        signals = classify_logs([log_text], updates)

        categories = [signal.category for signal in signals]
        self.assertIn("import_error", categories)
        self.assertIn("removed_api", categories)
        self.assertIn("test_failure", categories)

    def test_returns_unknown_when_no_pattern_matches(self) -> None:
        signals = classify_logs(["Everything succeeded except a random shell exit."], [])

        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].category, "unknown")


if __name__ == "__main__":
    unittest.main()
