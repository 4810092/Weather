from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "check_store_previews", ROOT / "scripts/check_store_previews.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

PACKAGE = Path("store/previews/growth-2026-08")


class StorePreviewCheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg is None:
            raise RuntimeError("ffmpeg is required for the store-preview tests")
        cls._fixture_directory = tempfile.TemporaryDirectory()
        fixture_root = Path(cls._fixture_directory.name)
        cls._videos: dict[str, bytes] = {}
        cls._facts: dict[str, dict[str, Any]] = {}
        for platform, extension, width in (
            ("apple", ".mov", 886),
            ("google", ".mp4", 1080),
        ):
            path = fixture_root / f"{platform}{extension}"
            subprocess.run(
                [
                    ffmpeg,
                    "-y",
                    "-v",
                    "error",
                    "-f",
                    "lavfi",
                    "-i",
                    f"color=black:s={width}x1920:r=1:d=20",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "ultrafast",
                    "-crf",
                    "40",
                    "-pix_fmt",
                    "yuv420p",
                    "-movflags",
                    "+faststart",
                    "-an",
                    str(path),
                ],
                check=True,
                capture_output=True,
                timeout=60,
            )
            facts, failures = MODULE._probe_video(path)
            if facts is None or failures:
                raise AssertionError(f"real fixture probe failed: {failures}")
            cls._videos[platform] = path.read_bytes()
            cls._facts[platform] = facts

    @classmethod
    def tearDownClass(cls) -> None:
        cls._fixture_directory.cleanup()

    def _copy_package(self, root: Path) -> Path:
        source_dir = ROOT / PACKAGE
        target_dir = root / PACKAGE
        target_dir.mkdir(parents=True)
        for name in (
            "manifest.json",
            "storyboard.md",
            "captions-en-US.srt",
            "captions-ru-RU.srt",
            "captions-uz-UZ.srt",
        ):
            (target_dir / name).write_bytes((source_dir / name).read_bytes())
        for relative in (MODULE.UPLOAD_MANIFEST, MODULE.QUALITY_GATES):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / relative).read_bytes())
        return target_dir

    @staticmethod
    def _box(name: bytes, payload: bytes) -> bytes:
        return struct.pack(">I4s", len(payload) + 8, name) + payload

    def _fake_box_video(self, marker: str) -> bytes:
        return b"".join(
            (
                self._box(b"ftyp", b"isom\x00\x00\x02\x00isomiso2"),
                self._box(b"moov", marker.encode("utf-8")),
                self._box(b"mdat", (marker * 2).encode("utf-8")),
            )
        )

    @staticmethod
    def _write_manifest(package: Path, manifest: dict[str, Any]) -> None:
        (package / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def _make_ready_package(self, root: Path) -> tuple[Path, dict[str, Any]]:
        package = self._copy_package(root)
        manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
        manifest["status"] = "ready"
        manifest["blocking_gates"] = []

        gate_path = root / MODULE.QUALITY_GATES
        gates = json.loads(gate_path.read_text(encoding="utf-8"))
        for gate_id in MODULE.REQUIRED_PREVIEW_GATES:
            gates["gates"][gate_id]["status"] = "pass"
        gate_path.write_text(json.dumps(gates, indent=2) + "\n", encoding="utf-8")

        upload_path = root / MODULE.UPLOAD_MANIFEST
        upload = json.loads(upload_path.read_text(encoding="utf-8"))
        for platform, artifact_key in (
            ("apple", "apple"),
            ("google", "android_phone"),
        ):
            artifact = upload["artifacts"][artifact_key]
            artifact["source_sync"] = "verified-current"
            artifact["sha256"] = hashlib.sha256(platform.encode()).hexdigest()
            for field in ("signing_evidence", "physical_qa_evidence"):
                relative = f"evidence/{platform}-{field}.md"
                artifact[field] = relative
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("verified test evidence\n", encoding="utf-8")
        upload_path.write_text(json.dumps(upload, indent=2) + "\n", encoding="utf-8")

        for locale, payload in manifest["locales"].items():
            for master_key, platform, extension in (
                ("apple_master", "apple", ".mov"),
                ("google_master", "google", ".mp4"),
            ):
                marker = f"{platform}-{locale}"
                video = self._videos[platform]
                facts = self._facts[platform]
                output_digest = hashlib.sha256(video).hexdigest()
                source_digest = hashlib.sha256(f"source-{marker}".encode()).hexdigest()
                master = payload[master_key]
                output_name = f"nimbo-{platform}-{locale}{extension}"
                output_relative = str(PACKAGE / output_name)
                evidence_name = f"nimbo-{platform}-{locale}.evidence.json"
                evidence_relative = str(PACKAGE / evidence_name)
                (package / output_name).write_bytes(video)
                master.update(
                    {
                        "file": output_relative,
                        "sha256": output_digest,
                        "source_recording_sha256": source_digest,
                        "capture_evidence": evidence_relative,
                    }
                )
                is_apple = platform == "apple"
                evidence = {
                    "schema_version": 1,
                    "platform": platform,
                    "locale": locale,
                    "candidate_identity": manifest["candidate_identity"][platform],
                    "device": "iPhone 15" if is_apple else "Pixel 8",
                    "os": "iOS 18.6" if is_apple else "Android 16",
                    "capture_date": "2026-08-29",
                    "source_recording_sha256": source_digest,
                    "output_sha256": output_digest,
                    "duration_seconds": 20,
                    "resolution": {
                        "width": facts["width"],
                        "height": facts["height"],
                    },
                    "codec": facts["codec"],
                    "fps": facts["fps"],
                    "bitrate_kbps": facts["bitrate_kbps"],
                    "reviewer": "QA Reviewer",
                }
                (package / evidence_name).write_text(
                    json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
                )
        self._write_manifest(package, manifest)
        return package, manifest

    def test_committed_capture_plan_passes(self) -> None:
        self.assertEqual(MODULE.validate(ROOT), [])

    def test_capture_blocked_plan_does_not_require_media_tools(self) -> None:
        with mock.patch.object(MODULE.shutil, "which", return_value=None):
            self.assertEqual(MODULE.validate(ROOT), [])

    def test_real_decodeable_ready_package_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_ready_package(root)
            self.assertEqual(MODULE.validate(root), [])

    def test_box_only_fake_video_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package, manifest = self._make_ready_package(root)
            master = manifest["locales"]["en-US"]["google_master"]
            output_path = root / master["file"]
            output_path.write_bytes(self._fake_box_video("not-video"))
            digest = hashlib.sha256(output_path.read_bytes()).hexdigest()
            master["sha256"] = digest
            evidence_path = root / master["capture_evidence"]
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            evidence["output_sha256"] = digest
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
            self._write_manifest(package, manifest)

            failures = MODULE.validate(root)
            self.assertTrue(
                any(
                    "expected exactly one decodable video stream, found 0" in item
                    for item in failures
                )
            )

    def test_blank_caption_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target_dir = self._copy_package(root)
            path = target_dir / "captions-en-US.srt"
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "Find the best time to go outside", ""
                ),
                encoding="utf-8",
            )
            failures = MODULE.validate(root)
            self.assertTrue(any("invalid cue" in failure for failure in failures))

    def test_srt_masquerading_as_mov_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package, manifest = self._make_ready_package(root)
            master = manifest["locales"]["en-US"]["apple_master"]
            output_path = root / master["file"]
            output_path.write_bytes((package / "captions-en-US.srt").read_bytes())
            digest = hashlib.sha256(output_path.read_bytes()).hexdigest()
            master["sha256"] = digest
            evidence_path = root / master["capture_evidence"]
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            evidence["output_sha256"] = digest
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
            self._write_manifest(package, manifest)

            failures = MODULE.validate(root)
            self.assertTrue(
                any("not a valid ISO-BMFF container" in failure for failure in failures)
            )

    def test_ready_manifest_with_blocking_gate_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package, manifest = self._make_ready_package(root)
            manifest["blocking_gates"] = ["physical capture not approved"]
            self._write_manifest(package, manifest)

            failures = MODULE.validate(root)
            self.assertIn("ready manifest must have no blocking gates", failures)

    def test_malformed_evidence_schema_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, manifest = self._make_ready_package(root)
            master = manifest["locales"]["en-US"]["apple_master"]
            evidence_path = root / master["capture_evidence"]
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            evidence.pop("reviewer")
            evidence["free_form_notes"] = "not allowed by the strict schema"
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

            failures = MODULE.validate(root)
            self.assertTrue(
                any(
                    "capture evidence schema mismatch" in failure
                    for failure in failures
                )
            )

    def test_mismatched_evidence_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, manifest = self._make_ready_package(root)
            master = manifest["locales"]["en-US"]["google_master"]
            evidence_path = root / master["capture_evidence"]
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            evidence["locale"] = "ru-RU"
            evidence["candidate_identity"] = {"version": "0.0.0", "version_code": 1}
            evidence["resolution"] = {"width": 1920, "height": 1080}
            evidence["output_sha256"] = "0" * 64
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

            failures = MODULE.validate(root)
            self.assertTrue(any("locale mismatch" in failure for failure in failures))
            self.assertTrue(
                any("candidate identity mismatch" in failure for failure in failures)
            )
            self.assertTrue(
                any(
                    "evidence output SHA-256 mismatch" in failure
                    for failure in failures
                )
            )
            self.assertTrue(any("must be portrait" in failure for failure in failures))

    def test_measured_media_facts_must_match_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, manifest = self._make_ready_package(root)
            master = manifest["locales"]["en-US"]["google_master"]
            evidence_path = root / master["capture_evidence"]
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            evidence["duration_seconds"] = 19
            evidence["resolution"] = {"width": 1078, "height": 1920}
            evidence["codec"] = "hevc"
            evidence["fps"] = 2
            evidence["bitrate_kbps"] += 1
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

            failures = MODULE.validate(root)
            self.assertTrue(
                any(
                    "measured video duration differs" in failure for failure in failures
                )
            )
            self.assertTrue(
                any(
                    "measured video resolution differs" in failure
                    for failure in failures
                )
            )
            self.assertTrue(
                any("measured video codec differs" in failure for failure in failures)
            )
            self.assertTrue(
                any("measured video fps differs" in failure for failure in failures)
            )
            self.assertTrue(
                any("measured video bitrate differs" in failure for failure in failures)
            )

    def test_candidate_identity_must_match_upload_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package, manifest = self._make_ready_package(root)
            manifest["candidate_identity"]["apple"]["build"] = "999"
            self._write_manifest(package, manifest)

            failures = MODULE.validate(root)
            self.assertIn(
                "Apple preview build differs from the upload manifest", failures
            )

    def test_ready_preview_rejects_non_pass_canonical_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_ready_package(root)
            gate_path = root / MODULE.QUALITY_GATES
            gates = json.loads(gate_path.read_text(encoding="utf-8"))
            gates["gates"]["ios_crash_gate"]["status"] = "blocked"
            gate_path.write_text(json.dumps(gates), encoding="utf-8")

            failures = MODULE.validate(root)
            self.assertTrue(
                any(
                    "canonical non-pass preview gates" in failure
                    for failure in failures
                )
            )
            self.assertIn(
                "ready preview still has non-pass canonical quality gates", failures
            )

    def test_blocked_preview_requires_exact_canonical_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self._copy_package(root)
            manifest = json.loads(
                (package / "manifest.json").read_text(encoding="utf-8")
            )
            manifest["blocking_gates"].remove("ios_crash_gate")
            self._write_manifest(package, manifest)

            failures = MODULE.validate(root)
            self.assertTrue(
                any(
                    "canonical non-pass preview gates" in failure
                    for failure in failures
                )
            )

    def test_ready_preview_requires_verified_current_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_ready_package(root)
            upload_path = root / MODULE.UPLOAD_MANIFEST
            upload = json.loads(upload_path.read_text(encoding="utf-8"))
            upload["artifacts"]["android_phone"]["source_sync"] = "blocked"
            upload_path.write_text(json.dumps(upload), encoding="utf-8")

            failures = MODULE.validate(root)
            self.assertIn(
                "google ready preview requires a verified-current artifact", failures
            )


if __name__ == "__main__":
    unittest.main()
