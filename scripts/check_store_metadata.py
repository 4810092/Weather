#!/usr/bin/env python3
"""Validate production store locale coverage and current text limits."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_LOCALES = {
    "en-US", "ru-RU", "ar", "es-ES", "fr-FR", "de-DE", "pt-PT",
    "zh-CN", "ja-JP", "ko-KR", "hi-IN", "tr-TR", "uz-UZ",
}
LIMITS = {
    "title": 30,
    "subtitle": 30,
    "short_description": 80,
    "keywords": 100,
    "description": 4000,
    "release_notes": 500,
}


def main() -> int:
    metadata = json.loads((ROOT / "store/metadata.json").read_text())
    failures: list[str] = []
    if set(metadata) != EXPECTED_LOCALES:
        failures.append(
            f"locale set differs: missing={sorted(EXPECTED_LOCALES - set(metadata))}, "
            f"extra={sorted(set(metadata) - EXPECTED_LOCALES)}"
        )
    for locale, fields in metadata.items():
        if set(fields) != set(LIMITS):
            failures.append(f"{locale}: expected exactly {sorted(LIMITS)}")
            continue
        for field, limit in LIMITS.items():
            value = fields[field].strip()
            if not value:
                failures.append(f"{locale}:{field}: empty")
            if len(value) > limit:
                failures.append(f"{locale}:{field}: {len(value)} > {limit}")
        lowered = " ".join(fields.values()).lower()
        for forbidden in ("ai weather", "most accurate", "самый точный"):
            if forbidden in lowered:
                failures.append(f"{locale}: forbidden unsupported claim {forbidden!r}")

    if failures:
        print("Store metadata check failed:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print(f"Store metadata passed: {len(metadata)} complete locales.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
