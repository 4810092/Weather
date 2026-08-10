#!/usr/bin/env python3
"""Fail when a production locale is missing a canonical resource or placeholder."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_ROOT = ROOT / "shared/src/commonMain/composeResources"
PRODUCTION_LOCALES = (
    "ar", "de", "es", "fr", "hi", "ja", "ko", "pt", "ru", "tr", "uz", "zh-rCN",
)
PLACEHOLDER = re.compile(r"%\d+\$[a-zA-Z]")


def read(path: Path) -> dict[str, tuple[str, set[str]]]:
    root = ElementTree.parse(path).getroot()
    resources: dict[str, tuple[str, set[str]]] = {}
    for node in root:
        name = node.attrib.get("name")
        if not name or node.tag not in {"string", "plurals"}:
            continue
        text = " ".join("".join(node.itertext()).split())
        resources[name] = (node.tag, set(PLACEHOLDER.findall(text)))
    return resources


def read_directory(path: Path) -> dict[str, tuple[str, set[str]]]:
    resources: dict[str, tuple[str, set[str]]] = {}
    for xml_path in sorted(path.glob("*.xml")):
        for name, signature in read(xml_path).items():
            if name in resources:
                raise ValueError(f"duplicate resource {name} in {path}")
            resources[name] = signature
    return resources


def main() -> int:
    canonical = read_directory(RESOURCE_ROOT / "values")
    failures: list[str] = []
    for locale in PRODUCTION_LOCALES:
        path = RESOURCE_ROOT / f"values-{locale}/strings.xml"
        if not path.exists():
            failures.append(f"{locale}: missing strings.xml")
            continue
        translated = read_directory(path.parent)
        missing = sorted(canonical.keys() - translated.keys())
        extra = sorted(translated.keys() - canonical.keys())
        if missing:
            failures.append(f"{locale}: missing {', '.join(missing)}")
        if extra:
            failures.append(f"{locale}: unknown {', '.join(extra)}")
        for key in canonical.keys() & translated.keys():
            if canonical[key] != translated[key]:
                failures.append(
                    f"{locale}:{key}: expected type/placeholders {canonical[key]}, "
                    f"found {translated[key]}"
                )

    if failures:
        print("Localization completeness failed:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print(
        f"Localization completeness passed: {len(canonical)} resources × "
        f"{len(PRODUCTION_LOCALES)} production overlays."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
