#!/usr/bin/env python3
"""Action-time CLI for the Nimbo signed release artifact gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from scripts.release_artifact_verifier import (
        load_manifest,
        validate_manifest_artifact_contract,
        verification_summary,
        verify_manifest_artifacts,
    )
except ModuleNotFoundError:
    from release_artifact_verifier import (  # type: ignore[no-redef]
        load_manifest,
        validate_manifest_artifact_contract,
        verification_summary,
        verify_manifest_artifacts,
    )


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Verify real signed AAB/IPA bytes for every verified-current "
            "artifact; blocked artifacts are checked contract-only."
        )
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "store/upload-manifest-1.1.0.json",
    )
    parser.add_argument(
        "--artifact-root",
        type=Path,
        help=(
            "Staged external directory containing the three manifest filenames, "
            "Nimbo.xcarchive, and ExportOptions.plist"
        ),
    )
    parser.add_argument(
        "--bundletool-jar",
        type=Path,
        help="Pinned bundletool-all JAR used for Android identity validation",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print a machine-readable verification summary",
    )
    parser.add_argument(
        "--contract-only",
        action="store_true",
        help=(
            "Validate only public schema, source, evidence, and atomic manifest "
            "state; never inspect or attest to private artifact bytes"
        ),
    )
    parser.add_argument(
        "--print-source-revision",
        action="store_true",
        help=(
            "Print only the statically validated manifest source revision for "
            "a subsequent build invocation"
        ),
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_args()
    failures: list[str] = []
    manifest = load_manifest(arguments.manifest, failures)
    if arguments.contract_only or arguments.print_source_revision:
        results = validate_manifest_artifact_contract(ROOT, manifest, failures)
        if arguments.json:
            print(
                json.dumps(
                    {
                        artifact_id: {
                            "contract_valid": result.contract_valid,
                            "source_sync": result.source_sync,
                        }
                        for artifact_id, result in results.items()
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
        if failures:
            for failure in failures:
                print(
                    f"release artifact contract validation failed: {failure}",
                    file=sys.stderr,
                )
            return 1
        if arguments.print_source_revision:
            print(manifest["source_revision"])
            return 0
        if not arguments.json:
            print(
                "Release artifact contract validation passed: static state only; "
                "artifact bytes were not inspected."
            )
        return 0

    results = verify_manifest_artifacts(
        ROOT,
        manifest,
        failures,
        artifact_root=arguments.artifact_root,
        bundletool_jar=arguments.bundletool_jar,
    )
    if arguments.json:
        print(json.dumps(verification_summary(results), indent=2, sort_keys=True))
    if failures:
        for failure in failures:
            print(f"release artifact verification failed: {failure}", file=sys.stderr)
        return 1
    verified = sum(result.byte_verified for result in results.values())
    blocked = sum(result.source_sync == "blocked" for result in results.values())
    if not arguments.json:
        print(
            f"Release artifact verification passed: {verified} byte-verified, "
            f"{blocked} fail-closed blocked."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
