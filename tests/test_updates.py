from __future__ import annotations

import json
from pathlib import Path
import unittest

from dependabot_rescue.providers import context_from_event_payload, context_from_manual_fields
from dependabot_rescue.updates import extract_updates


FIXTURES = Path(__file__).parent / "fixtures"


class UpdateExtractionTests(unittest.TestCase):
    def test_extracts_dependabot_update_from_event_payload(self) -> None:
        payload = json.loads((FIXTURES / "dependabot_event.json").read_text(encoding="utf-8"))
        context = context_from_event_payload(payload)

        updates = extract_updates(context)

        self.assertEqual(context.tool, "dependabot")
        self.assertEqual(len(updates), 1)
        self.assertEqual(updates[0].package, "requests")
        self.assertEqual(updates[0].from_version, "2.31.0")
        self.assertEqual(updates[0].to_version, "2.32.0")
        self.assertEqual(updates[0].ecosystem, "pip")

    def test_extracts_multiple_renovate_updates_from_body(self) -> None:
        body = (FIXTURES / "renovate_body.txt").read_text(encoding="utf-8")
        context = context_from_manual_fields(
            title="chore(deps): update dependency vitest to v2.0.1",
            body=body,
            author="renovate[bot]",
            branch="renovate/vitest-2.0.1",
        )

        updates = extract_updates(context)

        self.assertEqual(context.tool, "renovate")
        self.assertEqual({update.package for update in updates}, {"vitest", "@vitest/coverage-v8"})


if __name__ == "__main__":
    unittest.main()
