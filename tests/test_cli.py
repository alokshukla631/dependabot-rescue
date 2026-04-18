from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).parent / "fixtures"


class CliTests(unittest.TestCase):
    def test_cli_renders_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "report.json"
            env = os.environ.copy()
            env["PYTHONPATH"] = str(REPO_ROOT / "src")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "dependabot_rescue.cli",
                    "analyze",
                    "--event-path",
                    str(FIXTURES / "dependabot_event.json"),
                    "--log-file",
                    str(FIXTURES / "python_import_error.log"),
                    "--format",
                    "json",
                    "--output",
                    str(output_path),
                ],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            report = output_path.read_text(encoding="utf-8")
            self.assertIn('"category": "import_error"', report)
            self.assertIn('"package": "requests"', report)


if __name__ == "__main__":
    unittest.main()
