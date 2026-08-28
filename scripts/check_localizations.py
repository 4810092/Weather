#!/usr/bin/env python3
"""Fail when a production locale has invalid, blank, or incompatible resources."""

from __future__ import annotations

from collections import Counter
import re
import sys
from pathlib import Path
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

ROOT = Path(__file__).resolve().parents[1]
RESOURCE_ROOT = ROOT / "shared/src/commonMain/composeResources"
PRODUCTION_LOCALES = (
    "ar", "de", "es", "fr", "hi", "ja", "ko", "pt", "ru", "tr", "uz", "zh-rCN",
)
IOS_LOCALE_DIRECTORIES = {
    "en": "en.lproj",
    "ar": "ar.lproj",
    "de": "de.lproj",
    "es": "es.lproj",
    "fr": "fr.lproj",
    "hi": "hi.lproj",
    "ja": "ja.lproj",
    "ko": "ko.lproj",
    "pt": "pt.lproj",
    "ru": "ru.lproj",
    "tr": "tr.lproj",
    "uz": "uz.lproj",
    "zh-rCN": "zh-Hans.lproj",
}
ANDROID_SURFACE_ROOTS = (
    ROOT / "app/src/main/res",
    ROOT / "wearApp/src/main/res",
)
IOS_SURFACE_ROOT = ROOT / "iosApp/NimboSurfaces"

# Android and Apple both use printf-style placeholders. Escaped %% is not an
# argument. Retaining the complete token makes position and conversion type
# part of the translation contract, while Counter preserves multiplicity.
PRINTF_PLACEHOLDER = re.compile(
    r"(?<!%)%(?!%)(?:\d+\$)?[-+#0 ']*(?:\d+|\*)?"
    r"(?:\.(?:\d+|\*))?(?:hh|h|ll|l|q|L|z|t|j)?[@a-zA-Z]"
)

PlaceholderSignature = tuple[tuple[str, int], ...]
ResourceSignature = tuple[str, PlaceholderSignature]


def normalized_text(node: Element) -> str:
    return " ".join("".join(node.itertext()).split())


def placeholder_signature(value: str) -> PlaceholderSignature:
    return tuple(sorted(Counter(PRINTF_PLACEHOLDER.findall(value)).items()))


def resource_signature(node: Element, path: Path, name: str) -> ResourceSignature:
    if node.tag == "string":
        text = normalized_text(node)
        if not text:
            raise ValueError(f"{path}: {name}: blank string value")
        return node.tag, placeholder_signature(text)

    items = [child for child in node if child.tag == "item"]
    if not items:
        raise ValueError(f"{path}: {name}: plurals must contain at least one item")
    quantities: set[str] = set()
    item_signatures: list[Counter[str]] = []
    for item in items:
        quantity = item.attrib.get("quantity")
        if not quantity:
            raise ValueError(f"{path}: {name}: plural item is missing quantity")
        if quantity in quantities:
            raise ValueError(f"{path}: {name}: duplicate plural quantity {quantity}")
        quantities.add(quantity)
        text = normalized_text(item)
        if not text:
            raise ValueError(f"{path}: {name}[{quantity}]: blank plural value")
        item_signatures.append(Counter(PRINTF_PLACEHOLDER.findall(text)))

    # Plural categories legitimately vary by locale, and some singular/dual
    # forms spell the number out. The maximum multiplicity in any one variant
    # still catches a duplicated or changed formatting argument without adding
    # counts across language-specific categories.
    tokens = {token for signature in item_signatures for token in signature}
    placeholders = tuple(
        sorted(
            (token, max(signature[token] for signature in item_signatures))
            for token in tokens
        )
    )
    return node.tag, placeholders


def read(path: Path) -> dict[str, ResourceSignature]:
    try:
        root = ElementTree.parse(path).getroot()
    except (ElementTree.ParseError, OSError) as error:
        raise ValueError(f"{path}: invalid Android XML: {error}") from error
    if root.tag != "resources":
        raise ValueError(f"{path}: expected <resources> root, found <{root.tag}>")

    resources: dict[str, ResourceSignature] = {}
    for node in root:
        name = node.attrib.get("name")
        if not name or node.tag not in {"string", "plurals"}:
            continue
        if name in resources:
            raise ValueError(f"{path}: duplicate resource {name}")
        resources[name] = resource_signature(node, path, name)
    return resources


def read_directory(path: Path) -> dict[str, ResourceSignature]:
    resources: dict[str, ResourceSignature] = {}
    for xml_path in sorted(path.glob("*.xml")):
        for name, signature in read(xml_path).items():
            if name in resources:
                raise ValueError(f"duplicate resource {name} in {path}")
            resources[name] = signature
    return resources


def compare_resources(
    canonical: dict[str, ResourceSignature],
    translated: dict[str, ResourceSignature],
    label: str,
) -> list[str]:
    failures: list[str] = []
    missing = sorted(canonical.keys() - translated.keys())
    extra = sorted(translated.keys() - canonical.keys())
    if missing:
        failures.append(f"{label}: missing {', '.join(missing)}")
    if extra:
        failures.append(f"{label}: unknown {', '.join(extra)}")
    for key in sorted(canonical.keys() & translated.keys()):
        if canonical[key] != translated[key]:
            failures.append(
                f"{label}:{key}: expected type/placeholders {canonical[key]}, "
                f"found {translated[key]}"
            )
    return failures


class _AppleStringsParser:
    def __init__(self, content: str, label: str) -> None:
        self.content = content.removeprefix("\ufeff")
        self.label = label
        self.index = 0

    def error(self, message: str) -> ValueError:
        line = self.content.count("\n", 0, self.index) + 1
        previous_newline = self.content.rfind("\n", 0, self.index)
        column = self.index - previous_newline
        return ValueError(f"{self.label}:{line}:{column}: {message}")

    def skip_ignored(self) -> None:
        while self.index < len(self.content):
            if self.content[self.index].isspace():
                self.index += 1
                continue
            if self.content.startswith("//", self.index):
                newline = self.content.find("\n", self.index + 2)
                self.index = len(self.content) if newline < 0 else newline + 1
                continue
            if self.content.startswith("/*", self.index):
                end = self.content.find("*/", self.index + 2)
                if end < 0:
                    raise self.error("unterminated block comment")
                self.index = end + 2
                continue
            break

    def expect(self, token: str) -> None:
        if not self.content.startswith(token, self.index):
            raise self.error(f"expected {token!r}")
        self.index += len(token)

    def parse_string(self) -> str:
        if self.index >= len(self.content) or self.content[self.index] != '"':
            raise self.error("expected quoted string value")
        self.index += 1
        value: list[str] = []
        simple_escapes = {
            '"': '"',
            "'": "'",
            "?": "?",
            "\\": "\\",
            "a": "\a",
            "b": "\b",
            "f": "\f",
            "n": "\n",
            "r": "\r",
            "t": "\t",
            "v": "\v",
        }
        while self.index < len(self.content):
            character = self.content[self.index]
            self.index += 1
            if character == '"':
                return "".join(value)
            if character in "\r\n":
                raise self.error("unescaped newline in quoted string")
            if character != "\\":
                value.append(character)
                continue
            if self.index >= len(self.content):
                raise self.error("unterminated escape sequence")
            escaped = self.content[self.index]
            self.index += 1
            if escaped in simple_escapes:
                value.append(simple_escapes[escaped])
                continue
            if escaped in {"u", "U"}:
                digits = self.content[self.index : self.index + 4]
                if len(digits) != 4 or not all(
                    character in "0123456789abcdefABCDEF" for character in digits
                ):
                    raise self.error("invalid four-digit Unicode escape")
                value.append(chr(int(digits, 16)))
                self.index += 4
                continue
            if escaped in "01234567":
                digits = escaped
                while (
                    len(digits) < 3
                    and self.index < len(self.content)
                    and self.content[self.index] in "01234567"
                ):
                    digits += self.content[self.index]
                    self.index += 1
                value.append(chr(int(digits, 8)))
                continue
            raise self.error(f"unsupported escape sequence \\{escaped}")
        raise self.error("unterminated quoted string")

    def parse(self) -> dict[str, str]:
        entries: dict[str, str] = {}
        self.skip_ignored()
        while self.index < len(self.content):
            key = self.parse_string()
            if not key.strip():
                raise self.error("blank key")
            self.skip_ignored()
            self.expect("=")
            self.skip_ignored()
            value = self.parse_string()
            if not value.strip():
                raise self.error(f"{key}: blank string value")
            self.skip_ignored()
            self.expect(";")
            if key in entries:
                raise self.error(f"duplicate key {key!r}")
            entries[key] = value
            self.skip_ignored()
        return entries


def parse_apple_strings(content: str, label: str = "Apple strings") -> dict[str, str]:
    return _AppleStringsParser(content, label).parse()


def read_apple_strings(path: Path) -> dict[str, str]:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ValueError(f"{path}: cannot read Apple strings: {error}") from error
    return parse_apple_strings(content, str(path))


def compare_apple_strings(
    canonical: dict[str, str], translated: dict[str, str], label: str
) -> list[str]:
    failures: list[str] = []
    missing = sorted(canonical.keys() - translated.keys())
    extra = sorted(translated.keys() - canonical.keys())
    if missing:
        failures.append(f"{label}: missing {', '.join(missing)}")
    if extra:
        failures.append(f"{label}: unknown {', '.join(extra)}")
    for key in sorted(canonical.keys() & translated.keys()):
        expected = placeholder_signature(canonical[key])
        actual = placeholder_signature(translated[key])
        if expected != actual:
            failures.append(
                f"{label}:{key}: expected placeholders {expected}, found {actual}"
            )
    return failures


def main() -> int:
    failures: list[str] = []
    try:
        canonical = read_directory(RESOURCE_ROOT / "values")
    except ValueError as error:
        print(f"Localization completeness failed:\n- {error}", file=sys.stderr)
        return 1

    for locale in PRODUCTION_LOCALES:
        path = RESOURCE_ROOT / f"values-{locale}/strings.xml"
        if not path.exists():
            failures.append(f"{locale}: missing strings.xml")
            continue
        try:
            translated = read_directory(path.parent)
        except ValueError as error:
            failures.append(str(error))
            continue
        failures.extend(compare_resources(canonical, translated, locale))

    ios_root = ROOT / "iosApp/Nimbo"
    permission_key = "NSLocationWhenInUseUsageDescription"
    for locale, directory in IOS_LOCALE_DIRECTORIES.items():
        path = ios_root / directory / "InfoPlist.strings"
        if not path.exists():
            failures.append(f"iOS {locale}: missing {path.relative_to(ROOT)}")
            continue
        try:
            entries = read_apple_strings(path)
        except ValueError as error:
            failures.append(str(error))
            continue
        if permission_key not in entries:
            failures.append(f"iOS {locale}: missing localized {permission_key}")

    for root in ANDROID_SURFACE_ROOTS:
        try:
            canonical_surface = read_directory(root / "values")
        except ValueError as error:
            failures.append(str(error))
            continue
        for locale in PRODUCTION_LOCALES:
            path = root / f"values-{locale}/strings.xml"
            label = str(path.relative_to(ROOT))
            if not path.exists():
                failures.append(f"Android surface: missing {label}")
                continue
            try:
                translated = read_directory(path.parent)
            except ValueError as error:
                failures.append(str(error))
                continue
            failures.extend(compare_resources(canonical_surface, translated, label))

    canonical_apple_path = IOS_SURFACE_ROOT / "en.lproj/Localizable.strings"
    try:
        canonical_apple = read_apple_strings(canonical_apple_path)
    except ValueError as error:
        failures.append(str(error))
        canonical_apple = None
    if canonical_apple is not None:
        for locale, directory in IOS_LOCALE_DIRECTORIES.items():
            path = IOS_SURFACE_ROOT / directory / "Localizable.strings"
            label = str(path.relative_to(ROOT))
            if not path.exists():
                failures.append(f"Apple surfaces: missing {label}")
                continue
            try:
                translated = read_apple_strings(path)
            except ValueError as error:
                failures.append(str(error))
                continue
            failures.extend(compare_apple_strings(canonical_apple, translated, label))

    if failures:
        print("Localization completeness failed:", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print(
        f"Localization completeness passed: {len(canonical)} resources × "
        f"{len(PRODUCTION_LOCALES)} production overlays; "
        f"{len(IOS_LOCALE_DIRECTORIES)} iOS permission and surface localizations."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
