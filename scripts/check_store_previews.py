#!/usr/bin/env python3
"""Validate the fail-closed store-preview package and caption timing."""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import struct
import subprocess
import sys
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path("store/previews/growth-2026-08/manifest.json")
UPLOAD_MANIFEST = Path("store/upload-manifest-1.1.0.json")
QUALITY_GATES = Path("growth/quality/gates.json")
EXPECTED_LOCALES = {"en-US", "ru-RU", "uz-UZ"}
REQUIRED_PREVIEW_GATES = {
    "android_physical_smoke",
    "ios_crash_gate",
    "ios_physical_smoke",
    "open_meteo_promotion_clearance",
    "release_artifact_source_sync",
    "store_policy_console_clearance",
}
PLATFORMS = {
    "apple_master": ("apple", ".mov"),
    "google_master": ("google", ".mp4"),
}
EVIDENCE_FIELDS = {
    "schema_version",
    "platform",
    "locale",
    "candidate_identity",
    "device",
    "os",
    "capture_date",
    "source_recording_sha256",
    "output_sha256",
    "duration_seconds",
    "resolution",
    "codec",
    "fps",
    "bitrate_kbps",
    "reviewer",
}
TIMECODE = re.compile(
    r"(?P<start>\d{2}:\d{2}:\d{2},\d{3}) --> "
    r"(?P<end>\d{2}:\d{2}:\d{2},\d{3})"
)
SHA256 = re.compile(r"^[0-9a-f]{64}$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MEDIA_COMMAND_TIMEOUT_SECONDS = 120


def milliseconds(value: str) -> int:
    hours, minutes, rest = value.split(":")
    seconds, millis = rest.split(",")
    return (
        int(hours) * 3_600_000
        + int(minutes) * 60_000
        + int(seconds) * 1_000
        + int(millis)
    )


def parse_srt(path: Path) -> list[tuple[int, int, str]]:
    cues: list[tuple[int, int, str]] = []
    blocks = re.split(r"\n\s*\n", path.read_text(encoding="utf-8").strip())
    for expected_index, block in enumerate(blocks, start=1):
        lines = block.splitlines()
        if len(lines) < 3 or lines[0] != str(expected_index):
            raise ValueError(f"{path}: invalid cue sequence {expected_index}")
        timing = TIMECODE.fullmatch(lines[1])
        if timing is None:
            raise ValueError(f"{path}: invalid cue timing {lines[1]!r}")
        caption = "\n".join(lines[2:]).strip()
        if not caption:
            raise ValueError(f"{path}: blank cue {expected_index}")
        cues.append(
            (
                milliseconds(timing.group("start")),
                milliseconds(timing.group("end")),
                caption,
            )
        )
    return cues


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and SHA256.fullmatch(value) is not None


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _package_path(root: Path, value: object) -> Path | None:
    if not isinstance(value, str):
        return None
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        return None
    return root / relative


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _iso_bmff_failure(path: Path) -> str | None:
    """Return why a file is not a structurally valid ISO-BMFF media container."""

    try:
        file_size = path.stat().st_size
        with path.open("rb") as stream:
            offset = 0
            boxes: list[tuple[bytes, int]] = []
            while offset < file_size:
                if file_size - offset < 8:
                    return "trailing bytes do not form an ISO-BMFF box"
                stream.seek(offset)
                header = stream.read(8)
                box_size, box_type = struct.unpack(">I4s", header)
                header_size = 8
                if box_size == 1:
                    extended = stream.read(8)
                    if len(extended) != 8:
                        return "truncated extended ISO-BMFF box size"
                    box_size = struct.unpack(">Q", extended)[0]
                    header_size = 16
                elif box_size == 0:
                    box_size = file_size - offset
                if box_size < header_size or offset + box_size > file_size:
                    return "invalid ISO-BMFF box size"
                boxes.append((box_type, box_size))
                offset += box_size
    except OSError as error:
        return str(error)

    box_types = [box_type for box_type, _ in boxes]
    if not box_types or box_types[0] != b"ftyp":
        return "first ISO-BMFF box must be ftyp"
    required = {b"ftyp", b"moov", b"mdat"}
    missing = sorted(value.decode("ascii") for value in required - set(box_types))
    if missing:
        return f"missing required ISO-BMFF boxes: {', '.join(missing)}"
    sizes = {box_type: size for box_type, size in boxes if box_type in required}
    if sizes[b"ftyp"] < 16 or sizes[b"moov"] <= 8 or sizes[b"mdat"] <= 8:
        return "ftyp, moov, and mdat boxes must contain payload data"
    return None


def _positive_float(value: object) -> float | None:
    try:
        parsed = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) and parsed > 0 else None


def _positive_fps(stream: dict[str, Any]) -> float | None:
    for key in ("avg_frame_rate", "r_frame_rate"):
        value = stream.get(key)
        if not isinstance(value, str):
            continue
        try:
            parsed = float(Fraction(value))
        except (ValueError, ZeroDivisionError):
            continue
        if math.isfinite(parsed) and parsed > 0:
            return parsed
    return None


def _probe_video(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    """Probe and fully decode one candidate master, returning measured facts."""
    ffprobe = shutil.which("ffprobe")
    ffmpeg = shutil.which("ffmpeg")
    missing = [
        name
        for name, value in (("ffprobe", ffprobe), ("ffmpeg", ffmpeg))
        if value is None
    ]
    if missing:
        return None, ["required media tools are unavailable: " + ", ".join(missing)]

    try:
        probe = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_streams",
                "-show_format",
                "-of",
                "json",
                str(path),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=MEDIA_COMMAND_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return None, [f"ffprobe failed: {error}"]
    if probe.returncode != 0:
        detail = probe.stderr.strip() or f"exit {probe.returncode}"
        return None, [f"ffprobe rejected the media: {detail}"]
    try:
        payload = json.loads(probe.stdout)
    except json.JSONDecodeError as error:
        return None, [f"ffprobe returned invalid JSON: {error}"]
    if not isinstance(payload, dict):
        return None, ["ffprobe payload must be a JSON object"]

    streams = payload.get("streams")
    if not isinstance(streams, list):
        return None, ["ffprobe did not return a stream list"]
    video_streams = [
        stream
        for stream in streams
        if isinstance(stream, dict)
        and stream.get("codec_type") == "video"
        and not (
            isinstance(stream.get("disposition"), dict)
            and stream["disposition"].get("attached_pic") == 1
        )
    ]
    if len(video_streams) != 1:
        return None, [
            f"expected exactly one decodable video stream, found {len(video_streams)}"
        ]
    stream = video_streams[0]
    stream_index = stream.get("index")
    codec = stream.get("codec_name")
    width = stream.get("width")
    height = stream.get("height")
    if not _nonempty_string(codec):
        return None, ["video codec is missing"]
    if (
        not isinstance(stream_index, int)
        or isinstance(stream_index, bool)
        or stream_index < 0
    ):
        return None, ["video stream index is missing or invalid"]
    if (
        not isinstance(width, int)
        or isinstance(width, bool)
        or width <= 0
        or not isinstance(height, int)
        or isinstance(height, bool)
        or height <= 0
    ):
        return None, ["video resolution is missing or invalid"]

    format_payload = payload.get("format")
    media_format = format_payload if isinstance(format_payload, dict) else {}
    duration = _positive_float(stream.get("duration")) or _positive_float(
        media_format.get("duration")
    )
    fps = _positive_fps(stream)
    bitrate_bits = _positive_float(stream.get("bit_rate")) or _positive_float(
        media_format.get("bit_rate")
    )
    missing_facts = [
        name
        for name, value in (
            ("duration", duration),
            ("frame rate", fps),
            ("bitrate", bitrate_bits),
        )
        if value is None
    ]
    if missing_facts:
        return None, ["ffprobe omitted measured " + ", ".join(missing_facts)]

    try:
        decode = subprocess.run(
            [
                ffmpeg,
                "-v",
                "error",
                "-xerror",
                "-i",
                str(path),
                "-map",
                f"0:{stream_index}",
                "-f",
                "null",
                "-",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=MEDIA_COMMAND_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return None, [f"video decode failed: {error}"]
    if decode.returncode != 0:
        detail = decode.stderr.strip() or f"exit {decode.returncode}"
        return None, [f"video is not fully decodable: {detail}"]

    return {
        "codec": codec,
        "width": width,
        "height": height,
        "duration_seconds": duration,
        "fps": fps,
        "bitrate_kbps": max(1, round(bitrate_bits / 1000)),
    }, []


def _read_json_object(
    root: Path, relative: Path, label: str
) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        payload = json.loads((root / relative).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return None, [f"cannot read {label}: {error}"]
    if not isinstance(payload, dict):
        return None, [f"{label} must be a JSON object"]
    return payload, []


def _validate_release_context(
    root: Path,
    manifest: dict[str, Any],
    status: object,
) -> list[str]:
    """Bind preview identity and blockers to canonical release evidence."""
    failures: list[str] = []
    upload, upload_failures = _read_json_object(
        root, UPLOAD_MANIFEST, "preview upload manifest"
    )
    gates_payload, gate_failures = _read_json_object(
        root, QUALITY_GATES, "preview quality gates"
    )
    failures.extend(upload_failures)
    failures.extend(gate_failures)
    if upload is None or gates_payload is None:
        return failures

    identities = manifest.get("candidate_identity")
    identity_map = identities if isinstance(identities, dict) else {}
    apple_identity = identity_map.get("apple")
    google_identity = identity_map.get("google")
    apple = apple_identity if isinstance(apple_identity, dict) else {}
    google = google_identity if isinstance(google_identity, dict) else {}
    release = upload.get("release")
    artifacts = upload.get("artifacts")
    artifact_map = artifacts if isinstance(artifacts, dict) else {}
    apple_artifact = artifact_map.get("apple")
    android_artifact = artifact_map.get("android_phone")
    apple_upload = apple_artifact if isinstance(apple_artifact, dict) else {}
    android_upload = android_artifact if isinstance(android_artifact, dict) else {}

    if apple.get("version") != release or google.get("version") != release:
        failures.append("preview versions must match the upload-manifest release")
    if str(apple.get("build")) != str(apple_upload.get("build")):
        failures.append("Apple preview build differs from the upload manifest")
    if google.get("version_code") != android_upload.get("version_code"):
        failures.append("Google preview version code differs from the upload manifest")

    gates_value = gates_payload.get("gates")
    gates = gates_value if isinstance(gates_value, dict) else {}
    missing_gates = sorted(REQUIRED_PREVIEW_GATES - set(gates))
    if missing_gates:
        failures.append("quality gates omit preview gates: " + ", ".join(missing_gates))
    invalid_statuses = sorted(
        gate_id
        for gate_id in REQUIRED_PREVIEW_GATES & set(gates)
        if not isinstance(gates.get(gate_id), dict)
        or gates[gate_id].get("status") not in {"pass", "pending", "blocked"}
    )
    if invalid_statuses:
        failures.append(
            "preview quality gates have invalid status: " + ", ".join(invalid_statuses)
        )
    expected_blockers = {
        gate_id
        for gate_id in REQUIRED_PREVIEW_GATES
        if not isinstance(gates.get(gate_id), dict)
        or gates[gate_id].get("status") != "pass"
    }
    blockers = manifest.get("blocking_gates")
    declared_blockers = blockers if isinstance(blockers, list) else []
    canonical_declared = {
        value for value in declared_blockers if isinstance(value, str)
    }
    if len(canonical_declared) != len(declared_blockers):
        failures.append("blocking_gates must contain unique canonical string IDs")
    elif len(declared_blockers) != len(set(declared_blockers)):
        failures.append("blocking_gates must not contain duplicates")
    if canonical_declared != expected_blockers:
        failures.append(
            "blocking_gates must exactly match canonical non-pass preview gates; "
            f"expected {', '.join(sorted(expected_blockers)) or 'none'}"
        )

    if status == "ready":
        if expected_blockers:
            failures.append("ready preview still has non-pass canonical quality gates")
        for platform, artifact in (
            ("apple", apple_upload),
            ("google", android_upload),
        ):
            if artifact.get("source_sync") != "verified-current":
                failures.append(
                    f"{platform} ready preview requires a verified-current artifact"
                )
            if not _is_sha256(artifact.get("sha256")):
                failures.append(f"{platform} ready preview artifact SHA-256 is missing")
            for field in ("signing_evidence", "physical_qa_evidence"):
                evidence = _package_path(root, artifact.get(field))
                if evidence is None or not evidence.is_file():
                    failures.append(
                        f"{platform} ready preview artifact {field} is missing"
                    )
    return failures


def _validate_candidate_identities(manifest: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    identities = manifest.get("candidate_identity")
    if not isinstance(identities, dict) or set(identities) != {"apple", "google"}:
        return ["candidate_identity must contain exactly apple and google"]

    apple = identities.get("apple")
    if (
        not isinstance(apple, dict)
        or set(apple) != {"version", "build"}
        or not _nonempty_string(apple.get("version"))
        or not _nonempty_string(apple.get("build"))
    ):
        failures.append("apple candidate identity must contain version and build")

    google = identities.get("google")
    if (
        not isinstance(google, dict)
        or set(google) != {"version", "version_code"}
        or not _nonempty_string(google.get("version"))
        or not isinstance(google.get("version_code"), int)
        or isinstance(google.get("version_code"), bool)
        or google.get("version_code", 0) <= 0
    ):
        failures.append(
            "google candidate identity must contain version and positive version_code"
        )
    return failures


def _validate_export_contract(manifest: dict[str, Any]) -> list[str]:
    contract = manifest.get("export_contract")
    if not isinstance(contract, dict) or set(contract) != {"apple", "google"}:
        return ["export_contract must contain exactly apple and google"]
    failures: list[str] = []
    for platform in ("apple", "google"):
        payload = contract.get(platform)
        if not isinstance(payload, dict):
            failures.append(f"export_contract.{platform} must be an object")
            continue
        if not _nonempty_string(payload.get("video_codec")):
            failures.append(f"export_contract.{platform}.video_codec is required")
        max_fps = payload.get("max_fps")
        if not _is_number(max_fps) or max_fps <= 0:
            failures.append(f"export_contract.{platform}.max_fps must be positive")
    apple = contract.get("apple")
    if isinstance(apple, dict):
        for key in ("width", "height", "min_duration_seconds", "max_duration_seconds"):
            value = apple.get(key)
            if not _is_number(value) or value <= 0:
                failures.append(f"export_contract.apple.{key} must be positive")
    google = contract.get("google")
    if isinstance(google, dict) and google.get("orientation") != "portrait":
        failures.append("export_contract.google.orientation must be portrait")
    return failures


def _validate_evidence(
    evidence_path: Path,
    *,
    expected_platform: str,
    locale: str,
    manifest: dict[str, Any],
    master: dict[str, Any],
    output_digest: str,
    media_facts: dict[str, Any],
) -> list[str]:
    label = f"{locale}.{expected_platform}"
    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return [f"{label}: cannot read capture evidence JSON: {error}"]
    if not isinstance(evidence, dict):
        return [f"{label}: capture evidence must be a JSON object"]

    failures: list[str] = []
    if set(evidence) != EVIDENCE_FIELDS:
        missing = sorted(EVIDENCE_FIELDS - set(evidence))
        extra = sorted(set(evidence) - EVIDENCE_FIELDS)
        details = []
        if missing:
            details.append(f"missing {', '.join(missing)}")
        if extra:
            details.append(f"unexpected {', '.join(extra)}")
        failures.append(
            f"{label}: capture evidence schema mismatch ({'; '.join(details)})"
        )
    if evidence.get("schema_version") != 1:
        failures.append(f"{label}: capture evidence schema_version must be 1")
    if evidence.get("platform") != expected_platform:
        failures.append(f"{label}: capture evidence platform mismatch")
    if evidence.get("locale") != locale:
        failures.append(f"{label}: capture evidence locale mismatch")
    identities = manifest.get("candidate_identity")
    expected_identity = (
        identities.get(expected_platform) if isinstance(identities, dict) else None
    )
    if evidence.get("candidate_identity") != expected_identity:
        failures.append(f"{label}: capture evidence candidate identity mismatch")
    for field in ("device", "os", "reviewer"):
        if not _nonempty_string(evidence.get(field)):
            failures.append(f"{label}: capture evidence {field} must be non-empty")
    capture_date = evidence.get("capture_date")
    try:
        if not isinstance(capture_date, str) or not ISO_DATE.fullmatch(capture_date):
            raise ValueError
        date.fromisoformat(capture_date)
    except ValueError:
        failures.append(f"{label}: capture_date must be an ISO calendar date")

    source_hash = evidence.get("source_recording_sha256")
    output_hash = evidence.get("output_sha256")
    if not _is_sha256(source_hash) or source_hash != master.get(
        "source_recording_sha256"
    ):
        failures.append(f"{label}: source recording SHA-256 mismatch")
    if (
        not _is_sha256(output_hash)
        or output_hash != master.get("sha256")
        or output_hash != output_digest
    ):
        failures.append(f"{label}: evidence output SHA-256 mismatch")

    duration = evidence.get("duration_seconds")
    expected_duration = manifest.get("duration_seconds")
    if not _is_number(duration) or duration != expected_duration:
        failures.append(f"{label}: evidence duration does not match manifest")
    measured_duration = media_facts.get("duration_seconds")
    if (
        not _is_number(duration)
        or not _is_number(measured_duration)
        or not math.isclose(duration, measured_duration, abs_tol=0.05)
    ):
        failures.append(f"{label}: measured video duration differs from evidence")

    resolution = evidence.get("resolution")
    if not isinstance(resolution, dict) or set(resolution) != {"width", "height"}:
        failures.append(f"{label}: resolution must contain exactly width and height")
        width = height = None
    else:
        width = resolution.get("width")
        height = resolution.get("height")
        if (
            not isinstance(width, int)
            or isinstance(width, bool)
            or not isinstance(height, int)
            or isinstance(height, bool)
            or width <= 0
            or height <= 0
        ):
            failures.append(f"{label}: resolution dimensions must be positive integers")
    if width != media_facts.get("width") or height != media_facts.get("height"):
        failures.append(f"{label}: measured video resolution differs from evidence")

    contracts = manifest.get("export_contract")
    contract_value = (
        contracts.get(expected_platform) if isinstance(contracts, dict) else None
    )
    contract = contract_value if isinstance(contract_value, dict) else {}
    if evidence.get("codec") != contract.get("video_codec"):
        failures.append(f"{label}: evidence codec does not match export contract")
    if evidence.get("codec") != media_facts.get("codec"):
        failures.append(f"{label}: measured video codec differs from evidence")
    fps = evidence.get("fps")
    max_fps = contract.get("max_fps")
    if not _is_number(fps) or fps <= 0 or not _is_number(max_fps) or fps > max_fps:
        failures.append(f"{label}: evidence fps exceeds export contract")
    measured_fps = media_facts.get("fps")
    if (
        not _is_number(fps)
        or not _is_number(measured_fps)
        or not math.isclose(fps, measured_fps, abs_tol=0.01)
    ):
        failures.append(f"{label}: measured video fps differs from evidence")
    bitrate = evidence.get("bitrate_kbps")
    if not isinstance(bitrate, int) or isinstance(bitrate, bool) or bitrate <= 0:
        failures.append(f"{label}: bitrate_kbps must be a positive integer")
    if bitrate != media_facts.get("bitrate_kbps"):
        failures.append(f"{label}: measured video bitrate differs from evidence")

    if expected_platform == "apple":
        if width != contract.get("width") or height != contract.get("height"):
            failures.append(
                f"{label}: evidence resolution does not match Apple contract"
            )
        minimum = contract.get("min_duration_seconds")
        maximum = contract.get("max_duration_seconds")
        if (
            not _is_number(duration)
            or not _is_number(minimum)
            or not _is_number(maximum)
            or not minimum <= duration <= maximum
        ):
            failures.append(f"{label}: evidence duration violates Apple contract")
    elif contract.get("orientation") == "portrait" and (
        not isinstance(width, int) or not isinstance(height, int) or width >= height
    ):
        failures.append(f"{label}: evidence resolution must be portrait")
    return failures


def validate(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    path = root / MANIFEST
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"cannot read {MANIFEST}: {error}"]

    if not isinstance(manifest, dict):
        return ["manifest must be a JSON object"]
    if manifest.get("schema_version") != 3:
        failures.append("manifest schema_version must be 3")
    status = manifest.get("status")
    if status not in {"capture-blocked", "ready"}:
        failures.append("manifest status must be capture-blocked or ready")
    failures.extend(_validate_candidate_identities(manifest))
    failures.extend(_validate_export_contract(manifest))

    blocking_gates = manifest.get("blocking_gates")
    if not isinstance(blocking_gates, list) or not all(
        _nonempty_string(value) for value in blocking_gates
    ):
        failures.append("blocking_gates must be a list of non-empty strings")
    elif status == "ready" and blocking_gates:
        failures.append("ready manifest must have no blocking gates")
    elif status == "capture-blocked" and not blocking_gates:
        failures.append("capture-blocked manifest must list blocking gates")
    failures.extend(_validate_release_context(root, manifest, status))

    duration_seconds = manifest.get("duration_seconds")
    if (
        not isinstance(duration_seconds, int)
        or isinstance(duration_seconds, bool)
        or duration_seconds <= 0
    ):
        failures.append("duration_seconds must be a positive integer")
        duration_ms = 0
    else:
        duration_ms = duration_seconds * 1000
    clips = manifest.get("clips")
    if not isinstance(clips, list) or not clips:
        failures.append("manifest clips must be a non-empty list")
        clips = []
    expected_cues: list[tuple[int, int]] = []
    previous_end = 0
    for index, clip in enumerate(clips, start=1):
        if not isinstance(clip, dict):
            failures.append(f"clip {index} must be an object")
            continue
        start = clip.get("start_ms")
        end = clip.get("end_ms")
        if clip.get("sequence") != index or start != previous_end:
            failures.append(f"clip {index} sequence/timing is not contiguous")
        if not isinstance(end, int) or not isinstance(start, int) or end <= start:
            failures.append(f"clip {index} has invalid timing")
            continue
        if not _nonempty_string(clip.get("action")):
            failures.append(f"clip {index} has no genuine in-app action")
        expected_cues.append((start, end))
        previous_end = end
    if previous_end != duration_ms:
        failures.append("clip timeline does not match duration_seconds")

    locales = manifest.get("locales", {})
    if not isinstance(locales, dict) or set(locales) != EXPECTED_LOCALES:
        failures.append("preview package must contain EN, RU, and UZ locales")
        locales = {}
    for locale, payload in locales.items():
        if not isinstance(payload, dict):
            failures.append(f"{locale}: payload must be an object")
            continue
        caption_path = _package_path(root, payload.get("captions"))
        if caption_path is None or not caption_path.is_file():
            failures.append(f"{locale}: caption file is missing")
        else:
            try:
                cues = parse_srt(caption_path)
            except (OSError, UnicodeDecodeError, ValueError) as error:
                failures.append(str(error))
            else:
                if [(start, end) for start, end, _ in cues] != expected_cues:
                    failures.append(f"{locale}: caption timing differs from clips")
        for master_key, (platform, extension) in PLATFORMS.items():
            master = payload.get(master_key)
            if not isinstance(master, dict):
                failures.append(f"{locale}.{master_key}: missing master definition")
                continue
            file_path = _package_path(root, master.get("file"))
            evidence_path = _package_path(root, master.get("capture_evidence"))
            hashes = (master.get("sha256"), master.get("source_recording_sha256"))
            if file_path is None or file_path.suffix != extension:
                failures.append(
                    f"{locale}.{master_key}: output must use exact {extension} extension"
                )
            if status == "capture-blocked":
                if file_path is not None and file_path.exists():
                    failures.append(
                        f"{locale}.{master_key}: blocked master must be absent"
                    )
                if evidence_path is not None or any(
                    value is not None for value in hashes
                ):
                    failures.append(
                        f"{locale}.{master_key}: blocked evidence must be null"
                    )
                continue
            if status != "ready":
                continue
            if file_path is None or not file_path.is_file():
                failures.append(f"{locale}.{master_key}: ready master is missing")
                continue

            digest = _sha256_file(file_path)
            if master.get("sha256") != digest:
                failures.append(f"{locale}.{master_key}: output SHA-256 mismatch")
            if not all(_is_sha256(value) for value in hashes):
                failures.append(f"{locale}.{master_key}: capture hashes are incomplete")
            container_failure = _iso_bmff_failure(file_path)
            if container_failure is not None:
                failures.append(
                    f"{locale}.{master_key}: not a valid ISO-BMFF container: "
                    f"{container_failure}"
                )
            media_facts, media_failures = _probe_video(file_path)
            failures.extend(
                f"{locale}.{master_key}: {failure}" for failure in media_failures
            )
            if (
                evidence_path is None
                or evidence_path.suffix != ".json"
                or not evidence_path.is_file()
            ):
                failures.append(
                    f"{locale}.{master_key}: capture evidence JSON is missing"
                )
            else:
                failures.extend(
                    _validate_evidence(
                        evidence_path,
                        expected_platform=platform,
                        locale=locale,
                        manifest=manifest,
                        master=master,
                        output_digest=digest,
                        media_facts=media_facts or {},
                    )
                )

    storyboard = _package_path(root, manifest.get("storyboard"))
    if storyboard is None or not storyboard.is_file():
        failures.append("storyboard is missing")
    return failures


def main() -> int:
    failures = validate()
    if failures:
        print("Store preview check failed:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print("Store preview package passed: strict fail-closed preview contract is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
