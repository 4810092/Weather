#!/usr/bin/env python3
"""Shared helpers for growth scripts."""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[2]
GROWTH_ROOT = ROOT / "growth"

MODEL_VITAL_METRICS = frozenset(
    {
        "android_phone_model_crash_rate_pct",
        "android_phone_model_anr_rate_pct",
        "wear_model_crash_rate_pct",
        "wear_model_anr_rate_pct",
    }
)

POLICY_METRICS = frozenset(
    {
        "apple_policy_issues",
        "google_policy_issues",
    }
)

_NON_CONCRETE_DEVICES = frozenset(
    {
        "all",
        "android",
        "device",
        "model",
        "n/a",
        "na",
        "none",
        "phone",
        "summary",
        "unknown",
        "unspecified",
        "watch",
        "wear",
    }
)


def is_concrete_device(value: object) -> bool:
    """Return whether a dimension names an actual model rather than an aggregate."""

    normalized = str(value or "").strip().casefold()
    return bool(normalized) and normalized not in _NON_CONCRETE_DEVICES


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def config_fingerprint(config: Any) -> str:
    canonical = json.dumps(
        config,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"invalid ISO date {value!r}") from exc


def now_in(timezone_name: str) -> datetime:
    return datetime.now(tz=ZoneInfo(timezone_name))
