from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.verify_android_ui_results import verify_results


class AndroidUiResultVerifierTests(unittest.TestCase):
    def _write_result(self, root: Path, attributes: str) -> None:
        root.mkdir(parents=True, exist_ok=True)
        (root / "TEST-nimbo.xml").write_text(
            f'<testsuite name="nimbo" {attributes}>'
            + "".join(f'<testcase name="test{index}" />' for index in range(5))
            + "</testsuite>",
            encoding="utf-8",
        )

    def test_accepts_exact_green_suite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_result(root, 'tests="5" failures="0" errors="0" skipped="0"')
            tests, files = verify_results(root, expected_tests=5)
            self.assertEqual(tests, 5)
            self.assertEqual(len(files), 1)

    def test_rejects_missing_or_zero_test_suite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, "no TEST-"):
                verify_results(root, expected_tests=5)
            self._write_result(root, 'tests="0" failures="0" errors="0" skipped="0"')
            with self.assertRaisesRegex(ValueError, "expected exactly 5"):
                verify_results(root, expected_tests=5)

    def test_rejects_failure_error_or_skip(self) -> None:
        for field in ("failures", "errors", "skipped"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                values = {"failures": 0, "errors": 0, "skipped": 0}
                values[field] = 1
                self._write_result(
                    root,
                    f'tests="5" failures="{values["failures"]}" '
                    f'errors="{values["errors"]}" skipped="{values["skipped"]}"',
                )
                with self.assertRaisesRegex(ValueError, field):
                    verify_results(root, expected_tests=5)


if __name__ == "__main__":
    unittest.main()
