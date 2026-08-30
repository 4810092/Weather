#!/usr/bin/env python3
"""Fail closed when hosted Android instrumentation results are missing or empty."""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path


def _integer_attribute(element: ET.Element, name: str, path: Path) -> int:
    raw = element.get(name)
    if raw is None:
        if name == "tests":
            return len(element.findall(".//testcase"))
        child_name = {
            "failures": "failure",
            "errors": "error",
            "skipped": "skipped",
        }[name]
        return len(element.findall(f".//{child_name}"))
    try:
        value = int(raw)
    except ValueError as error:
        raise ValueError(f"{path}: invalid {name} count {raw!r}") from error
    if value < 0:
        raise ValueError(f"{path}: negative {name} count {value}")
    return value


def verify_results(root: Path, expected_tests: int) -> tuple[int, tuple[Path, ...]]:
    if expected_tests <= 0:
        raise ValueError("expected_tests must be positive")
    if not root.is_dir():
        raise ValueError(f"instrumentation result directory is missing: {root}")

    result_files = tuple(
        sorted(path for path in root.rglob("TEST-*.xml") if path.is_file())
    )
    if not result_files:
        raise ValueError(f"no TEST-*.xml instrumentation results found under {root}")

    totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
    for path in result_files:
        try:
            document = ET.parse(path).getroot()
        except (ET.ParseError, OSError) as error:
            raise ValueError(
                f"cannot parse instrumentation result {path}: {error}"
            ) from error
        suites = (
            [document]
            if document.tag.endswith("testsuite")
            else list(document.findall("testsuite"))
        )
        if not suites:
            raise ValueError(f"{path}: no testsuite element")
        for suite in suites:
            for name in totals:
                totals[name] += _integer_attribute(suite, name, path)

    if totals["tests"] != expected_tests:
        raise ValueError(
            f"expected exactly {expected_tests} instrumentation tests, found {totals['tests']}"
        )
    for name in ("failures", "errors", "skipped"):
        if totals[name] != 0:
            raise ValueError(f"instrumentation results contain {totals[name]} {name}")
    return totals["tests"], result_files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--expected-tests", type=int, required=True)
    args = parser.parse_args()
    try:
        test_count, files = verify_results(args.root, args.expected_tests)
    except ValueError as error:
        print(f"Android UI result verification failed: {error}")
        return 1
    print(
        "Android UI result verification passed: "
        f"{test_count} tests in {len(files)} XML file(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
