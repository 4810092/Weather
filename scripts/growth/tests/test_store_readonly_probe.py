from __future__ import annotations

import importlib.util
import os
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "store_readonly_probe", ROOT / "scripts/store-readonly-probe.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AppleProbeTest(unittest.TestCase):
    def _probe(self, bundle_id: str, records: list[dict]) -> tuple[str, str]:
        environment = {
            "NIMBO_ASC_KEY_ID": "test-key-id",
            "NIMBO_ASC_ISSUER_ID": "test-issuer-id",
        }
        with (
            mock.patch.dict(os.environ, environment, clear=True),
            mock.patch.object(MODULE, "secret_bytes", return_value=b"private-key"),
            mock.patch.object(MODULE, "jwt", return_value="test-token"),
            mock.patch.object(
                MODULE,
                "request_json",
                return_value=(200, {"data": records}),
            ),
        ):
            return MODULE.apple_probe(True, bundle_id)

    def test_exact_bundle_is_visible_among_prefix_similar_records(self) -> None:
        bundle_id = "uz.ganikhodjaev.steppeloom"
        result = self._probe(
            bundle_id,
            [
                {"attributes": {"bundleId": bundle_id}},
                {"attributes": {"bundleId": f"{bundle_id}.testflight"}},
            ],
        )

        self.assertEqual(result, ("ok", "authenticated; configured bundle is visible"))

    def test_prefix_similar_bundle_does_not_satisfy_exact_visibility(self) -> None:
        bundle_id = "uz.ganikhodjaev.steppeloom"
        result = self._probe(
            bundle_id,
            [{"attributes": {"bundleId": f"{bundle_id}.testflight"}}],
        )

        self.assertEqual(
            result,
            ("fail", "authenticated but exact app is not uniquely visible"),
        )

    def test_duplicate_exact_records_fail_closed(self) -> None:
        bundle_id = "uz.ganikhodjaev.steppeloom"
        record = {"attributes": {"bundleId": bundle_id}}

        self.assertEqual(
            self._probe(bundle_id, [record, record]),
            ("fail", "authenticated but exact app is not uniquely visible"),
        )


if __name__ == "__main__":
    unittest.main()
