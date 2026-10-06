from pathlib import Path
import importlib.util
import tempfile
import unittest

from PIL import Image

SCRIPT = Path(__file__).resolve().parents[2] / "check_visual_regressions.py"
spec = importlib.util.spec_from_file_location("visual_regressions", SCRIPT)
visual = importlib.util.module_from_spec(spec)
spec.loader.exec_module(visual)


class VisualRegressionTest(unittest.TestCase):
    def test_exact_pixels_pass_but_changed_content_and_dimensions_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            expected, actual, diff = (root / name for name in ("expected.png", "actual.png", "diff.png"))
            Image.new("RGB", (100, 100), "white").save(expected)
            Image.new("RGB", (100, 100), "white").save(actual)
            self.assertTrue(visual.compare(expected, actual, diff)["passed"])
            changed = Image.new("RGB", (100, 100), "white")
            changed.paste("black", (20, 20, 50, 50))
            changed.save(actual)
            self.assertFalse(visual.compare(expected, actual, diff)["passed"])
            self.assertTrue(diff.exists())
            Image.new("RGB", (100, 101), "white").save(actual)
            self.assertFalse(visual.compare(expected, actual, diff)["passed"])
