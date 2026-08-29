#!/usr/bin/env python3
"""Fail closed when the audited Google Play UZ draft drifts.

This is a repository drift guard, not a substitute for runtime, Console, or
store-review evidence. The dated evidence file explains the bounded audit.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIT_DOC = ROOT / "growth/quality/google-play-uz-public-claims-parity-2026-08-30.md"
METADATA = ROOT / "store/metadata.json"
LISTING_ID = "google-play-uz-country-listing"
EXPECTED_LISTING_SHA256 = "3464949ecf2d23acacac5942fc5ef8b9a0955c888db3e36a76f4d47bd44519e6"
EXPECTED_LISTING_ROUTING = {
    "localization_refs": ["en-US", "ru-RU"],
    "overrides": {},
    "creative_set": "growth-2026-08",
    "experiment": None,
    "marketing_url": "https://nimbo.uz/",
    "support_url": "https://nimbo.uz/support/",
    "privacy_url": "https://nimbo.uz/privacy/",
}

EXPECTED_ASSET_SHA256 = {
    "store/assets/google-play/icon-512.png": "adecfc4a6b4443c067460ba5eacc2b977f2e6305f737d83b03fac538df224010",
    "store/assets/google-play/feature-graphic-uz-UZ-1024x500.jpg": "a3ef85c4d6518ccaa93848617bef4868164e19eff79ea7160060d56ffef44437",
    "store/assets/google-play/feature-graphic-ru-RU-1024x500.jpg": "768eac2539ceb9f2c5bea22a19ab0598a8b8efba6a92a1b22dd1289a283d5bc0",
    "store/creatives/growth-2026-08/google-play/uz-UZ/01-best-time.png": "5b4ba6ae3793ddf51a5a26a7874eb19882f42897b1f44a5e164b4a54b9384e97",
    "store/creatives/growth-2026-08/google-play/uz-UZ/02-recent-comparison.png": "cab2803966dfe5e9dc09ba9d9c4397de287bb5f8d157327bea383fe9667507f7",
    "store/creatives/growth-2026-08/google-play/uz-UZ/03-timeline.png": "879250a251057bad8e5931385c1d07425a9b43ce9099d1ce9765816c02dc88c2",
    "store/creatives/growth-2026-08/google-play/uz-UZ/04-details.png": "9b614b93a6473cb503f6827851760a8513cba8f62eb2915cb5a13df27484800c",
    "store/creatives/growth-2026-08/google-play/uz-UZ/05-offline-privacy.png": "43e7d88baac450463429494733cf2ee0952720d078625716d29ee57f67494c10",
    "store/creatives/growth-2026-08/google-play/uz-UZ/06-watch.png": "60ec3d11324760df8007d3acbf5db88009f204b58571de3212b20b906b79c861",
    "store/creatives/growth-2026-08/google-play/ru-RU/01-best-time.png": "5c87a51acfa7ddd7b89b0c7190387cd077672be925924ece0aa20f02f537fb9d",
    "store/creatives/growth-2026-08/google-play/ru-RU/02-recent-comparison.png": "6ab6cb1ad4ebdefc2e1e69a69bb728bcb40da2397d472778372611a4aed97331",
    "store/creatives/growth-2026-08/google-play/ru-RU/03-timeline.png": "b619b7d04c471fa6da553a839551da43f527f585851943a6e28811119989485c",
    "store/creatives/growth-2026-08/google-play/ru-RU/04-details.png": "a87df24b4441e2614ecf82c5a882268602814839911020ae722dbf1229063d47",
    "store/creatives/growth-2026-08/google-play/ru-RU/05-offline-privacy.png": "6c46b340380ffb400cf9ac7de24a97fe68625b878f3511097616b8cf44058e9c",
    "store/creatives/growth-2026-08/google-play/ru-RU/06-watch.png": "91b0e743f4ee23b24c6dac1ad95eaf38aac69677d35cf39e7a8903d3b344eac0",
    "store/screenshots/google-play/wear-os-uz-UZ/01-current.png": "76d79459e88830f2f39000fda34ca1ddd15877eba29bd143fe7a1a07c80c714c",
    "store/screenshots/google-play/wear-os-ru-RU/01-current.png": "60944c367cfdf41c47226cf3f60dfa8b918827a4674e33db531abb67a03cfc47",
}

AUDIT_MARKERS = (
    "Status: **CLAIM PARITY PASS; CONSOLE SUBMISSION HOLD**.",
    "Nimbo Weather: Ob-havo",
    "growth/reports/google-play-uz-title-opportunity-2026-08-30.md",
    "**Public 1.0.2 claim parity: PASS.**",
    "**Custom-listing Console submission: HOLD.**",
    "798cfe33b636cbe6a291ef0125abc193dbd1549e31c7daf50b261a0105c322ca",
    "aeecf509e977036f9af3f0d48c55e80413619a3fa5ea6061fa9f070f73ba2b91",
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256_bytes(encoded)


def audited_listing(metadata: dict[str, Any]) -> dict[str, Any] | None:
    listings = metadata.get("listings")
    if not isinstance(listings, list):
        return None
    for listing in listings:
        if isinstance(listing, dict) and listing.get("id") == LISTING_ID:
            return listing
    return None


def validate_metadata(metadata: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    listing = audited_listing(metadata)
    if listing is None:
        return [f"missing listing {LISTING_ID}"]
    if listing.get("platform") != "google-play":
        failures.append("audited listing must remain google-play")
    if listing.get("storefront") != "UZ":
        failures.append("audited listing must remain UZ-only")
    if listing.get("listing_type") != "custom-listing":
        failures.append("audited listing must remain a custom listing")
    for field, expected in EXPECTED_LISTING_ROUTING.items():
        if listing.get(field) != expected:
            failures.append(
                f"audited listing {field} drifted: expected {expected!r}, "
                f"found {listing.get(field)!r}"
            )
    if listing.get("custom_product_page") is not None:
        failures.append("audited Google listing cannot gain a custom product page")
    custom = listing.get("custom_listing")
    if not isinstance(custom, dict):
        failures.append("audited custom_listing is missing or invalid")
        return failures
    if custom.get("status") != "draft":
        failures.append("audited listing must remain draft in repository input")
    if custom.get("targeting") != {
        "type": "country",
        "country_targets": ["UZ"],
    }:
        failures.append("audited listing targeting drifted from country UZ")
    actual_hash = canonical_sha256(custom)
    if actual_hash != EXPECTED_LISTING_SHA256:
        failures.append(
            "Google Play UZ listing payload changed after the public-claims audit: "
            f"expected {EXPECTED_LISTING_SHA256}, found {actual_hash}"
        )
    return failures


def validate_assets(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    for relative, expected_hash in EXPECTED_ASSET_SHA256.items():
        path = root / relative
        if not path.is_file():
            failures.append(f"missing audited asset: {relative}")
            continue
        actual_hash = sha256_bytes(path.read_bytes())
        if actual_hash != expected_hash:
            failures.append(
                f"audited asset changed: {relative}: expected {expected_hash}, "
                f"found {actual_hash}"
            )
    return failures


def validate_audit_text(text: str) -> list[str]:
    return [
        f"audit evidence missing marker: {marker}"
        for marker in AUDIT_MARKERS
        if marker not in text
    ]


def validate(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    metadata_path = root / METADATA.relative_to(ROOT)
    audit_path = root / AUDIT_DOC.relative_to(ROOT)
    if not metadata_path.is_file():
        failures.append("missing store/metadata.json")
    else:
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            failures.append(f"cannot read store/metadata.json: {error}")
        else:
            if not isinstance(metadata, dict):
                failures.append("store/metadata.json must contain an object")
            else:
                failures.extend(validate_metadata(metadata))
    failures.extend(validate_assets(root))
    if not audit_path.is_file():
        failures.append(
            "missing growth/quality/google-play-uz-public-claims-parity-2026-08-30.md"
        )
    else:
        try:
            audit_text = audit_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            failures.append(f"cannot read public-claims audit: {error}")
        else:
            failures.extend(validate_audit_text(audit_text))
    return failures


def main() -> int:
    failures = validate()
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    print("Google Play UZ public-claims parity drift guard passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
