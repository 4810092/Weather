#!/usr/bin/env python3
"""Fail-closed security policy for the canonical signed-candidate workflow."""

from __future__ import annotations

import hashlib
import re


WORKFLOW_SHA256 = "879b5f99db38df7d140b8c6bb0cfcd42f05421d43b3f34a4b7883c8c18db7632"
FORBIDDEN_GRADLE_VERIFICATION_OVERRIDES = (
    "--write-verification-metadata",
    "--dependency-verification",
    "org.gradle.dependency.verification",
)
RELEASE_SOURCE_PATHS = (
    "androidSurfaceContract",
    "app",
    "shared",
    "wearApp",
    "iosApp",
    "build.gradle.kts",
    "settings.gradle.kts",
    "gradle.properties",
    "gradle",
    "gradlew",
    "gradlew.bat",
)
RELEASE_GENERATED_PATHS = (
    ":(exclude)androidSurfaceContract/build/**",
    ":(exclude)app/build/**",
    ":(exclude)shared/build/**",
    ":(exclude)wearApp/build/**",
    ":(exclude)iosApp/build/**",
    ":(exclude)**/.cxx/**",
    ":(exclude)**/.externalNativeBuild/**",
    ":(exclude)**/.DS_Store",
    ":(exclude)iosApp/**/xcuserdata/**",
    ":(exclude)iosApp/**/DerivedData/**",
)
REPOSITORY_GUARD = (
    "github.repository == '4810092/Weather' && "
    "github.ref == 'refs/heads/master'"
)
SIGNING_GUARD = REPOSITORY_GUARD + " && needs.build-unsigned.result == 'success'"
APPROVED_ACTIONS = {
    "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1",
    "actions/setup-java": "dd06d9cba3e5552c54d9f8ea23572deb30010f7c",
    "actions/setup-python": "ece7cb06caefa5fff74198d8649806c4678c61a1",
    "gradle/actions/setup-gradle": "9c971963bec38e04b3d30dcc455b5382be2fdbfb",
    "actions/upload-artifact": "043fb46d1a93c77aae656e7c1c64a875d1fc6a0a",
    "actions/download-artifact": "3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c",
}
EXPECTED_ACTION_COUNTS = {
    "actions/checkout": 2,
    "actions/setup-java": 2,
    "actions/setup-python": 2,
    "gradle/actions/setup-gradle": 1,
    "actions/upload-artifact": 2,
    "actions/download-artifact": 1,
}
SECRET_BINDINGS = {
    "NIMBO_ANDROID_KEYSTORE_B64": "NIMBO_ANDROID_UPLOAD_KEYSTORE_B64",
    "NIMBO_ANDROID_STORE_PASSWORD": "NIMBO_ANDROID_UPLOAD_STORE_PASSWORD",
    "NIMBO_ANDROID_KEY_PASSWORD": "NIMBO_ANDROID_UPLOAD_KEY_PASSWORD",
    "NIMBO_APPLE_P12_B64": "NIMBO_APPLE_DISTRIBUTION_P12_B64",
    "NIMBO_APPLE_P12_PASSWORD": "NIMBO_APPLE_DISTRIBUTION_P12_PASSWORD",
    "NIMBO_APPLE_APP_PROFILE_B64": "NIMBO_APPLE_APP_PROFILE_B64",
    "NIMBO_APPLE_WIDGET_PROFILE_B64": "NIMBO_APPLE_WIDGET_PROFILE_B64",
    "NIMBO_APPLE_WATCH_PROFILE_B64": "NIMBO_APPLE_WATCH_PROFILE_B64",
}
SECRET_STEP_NAMES = {
    "Decode protected signing material outside the checkout",
    "Upload-sign Android phone and Wear bundles",
    "Install ephemeral Apple identity and exact profiles",
}
SECRET_STEP_ENVS = {
    "Decode protected signing material outside the checkout": [
        (
            "NIMBO_ANDROID_KEYSTORE_B64",
            "NIMBO_ANDROID_UPLOAD_KEYSTORE_B64",
        ),
        (
            "NIMBO_APPLE_P12_B64",
            "NIMBO_APPLE_DISTRIBUTION_P12_B64",
        ),
        ("NIMBO_APPLE_APP_PROFILE_B64", "NIMBO_APPLE_APP_PROFILE_B64"),
        ("NIMBO_APPLE_WIDGET_PROFILE_B64", "NIMBO_APPLE_WIDGET_PROFILE_B64"),
        ("NIMBO_APPLE_WATCH_PROFILE_B64", "NIMBO_APPLE_WATCH_PROFILE_B64"),
    ],
    "Upload-sign Android phone and Wear bundles": [
        (
            "NIMBO_ANDROID_STORE_PASSWORD",
            "NIMBO_ANDROID_UPLOAD_STORE_PASSWORD",
        ),
        (
            "NIMBO_ANDROID_KEY_PASSWORD",
            "NIMBO_ANDROID_UPLOAD_KEY_PASSWORD",
        ),
    ],
    "Install ephemeral Apple identity and exact profiles": [
        (
            "NIMBO_APPLE_P12_PASSWORD",
            "NIMBO_APPLE_DISTRIBUTION_P12_PASSWORD",
        ),
    ],
}
BUILD_STEP_INVENTORY = [
    ("uses", "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1"),
    ("uses", "actions/setup-java@dd06d9cba3e5552c54d9f8ea23572deb30010f7c"),
    ("uses", "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1"),
    ("uses", "gradle/actions/setup-gradle@9c971963bec38e04b3d30dcc455b5382be2fdbfb"),
    ("name", "Resolve exact release source and unsigned staging paths"),
    ("name", "Validate and seal exact release inputs"),
    ("name", "Build exact-source Android phone and Wear bundles"),
    ("name", "Build exact-source unsigned Apple archive"),
    ("name", "Verify exact release inputs remained sealed"),
    ("name", "Package inert unsigned build outputs"),
    ("uses", "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a"),
    ("name", "Remove unsigned build clone"),
]
SIGN_STEP_INVENTORY = [
    ("uses", "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1"),
    ("uses", "actions/setup-java@dd06d9cba3e5552c54d9f8ea23572deb30010f7c"),
    ("uses", "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1"),
    ("uses", "actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c"),
    ("name", "Validate and unpack inert unsigned inputs"),
    ("name", "Fetch pinned Bundletool"),
    ("name", "Decode protected signing material outside the checkout"),
    ("name", "Upload-sign Android phone and Wear bundles"),
    ("name", "Install ephemeral Apple identity and exact profiles"),
    ("name", "Export and retain distribution-signed Apple build 6"),
    ("name", "Destroy signing material before byte verification"),
    ("name", "Byte-verify the complete signed candidate"),
    ("uses", "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a"),
    ("name", "Destroy ephemeral signing material"),
]
BUILD_ACTION_STEP_SHA256 = [
    "34acf24a5d811131306562912e4c531943c77e84521386b52e487a94012dfb91",
    "dcc5a242142f07133cff6aa7d84c0b2701cb05fa4bd0bc8bca60a640470fcfef",
    "68d8c78fc03544c83d10de90b661200da54135d5b13e5c09129e276eeec0f83e",
    "f20e72094b208a255e173807f2ae783a60e4735c8ec46973c31354533b2a37aa",
    "c064477d9afaac14ad4839d44fd7599f8c88aaedd60b09ee39d8e3b2b1a2bbd1",
]
SIGN_ACTION_STEP_SHA256 = [
    "34acf24a5d811131306562912e4c531943c77e84521386b52e487a94012dfb91",
    "dcc5a242142f07133cff6aa7d84c0b2701cb05fa4bd0bc8bca60a640470fcfef",
    "68d8c78fc03544c83d10de90b661200da54135d5b13e5c09129e276eeec0f83e",
    "6c10ee9ea85054e7903d406a87ad58351a0a84d295fdb7b8e59296a59da50e63",
    "c7a5e71576651099391a847844b2b8e051a8b6fb487340b445fc845ba742b509",
]
REVIEWED_VERIFIER_SHA256 = {
    "verify_signed_candidate.py": "1294eec2eb8a0c0a1ff928bf2963a46dcbc600b42eaa840c53f3c5ec537956fa",
    "release_artifact_verifier.py": "8b99c81951002b19cb6d0c096871e36f222ec2df6fac762603442e194fc41a99",
}
BUILD_RUN_SHA256 = {
    "Resolve exact release source and unsigned staging paths": "e7f591227861f1cb074317294a06906ff7da5e27e8c7c022f42e7a2244aef940",
    "Validate and seal exact release inputs": "37d37396443480fa2e7ab29160867b13441a393d4d9eca9cd4e3a6ee9792dc2b",
    "Build exact-source Android phone and Wear bundles": "4434b4ee00d860ab3c1777257197196d1933e55cfb5704d34a911d42c302e1dd",
    "Build exact-source unsigned Apple archive": "2cbd799de05ca85a6f7027b3efacbe6706ee7ba8d5fe885f25a02f6f20f1c249",
    "Verify exact release inputs remained sealed": "bf482cff97dddc861c853a9047bdb6f8c6284f6d381d026125d1f7fbfd3362d8",
    "Package inert unsigned build outputs": "4fed4cdb3bf2d514f0c4f57468527629a28466288e5dd71ea64cee150260051e",
    "Remove unsigned build clone": "e76ab6f50b0eab2675461657cb4d3ce9e767cd4c481ca5206ac97222680a3ee5",
}
SIGN_RUN_SHA256 = {
    "Validate and unpack inert unsigned inputs": "4b9e8b6524645706abf760aa18d3e4e44688cd4a4d59afc3615a442aa1f2c2fc",
    "Fetch pinned Bundletool": "8654644e5fab003fd6b3e98bd8b61d3e9f1f7f1bf76fa290458095bc9875cc79",
    "Decode protected signing material outside the checkout": "f2485c2e40ade88500f2b583a7226a970553dce44a851b4c4ba92de6b35bc9ac",
    "Upload-sign Android phone and Wear bundles": "fced7db2bc082b396bd326021a2a0adcc860932d32aa1a63c271d8141f23a9bc",
    "Install ephemeral Apple identity and exact profiles": "5bf3e03c335a87af253341b5dbfdfc7d3f9797b222e312de5711f81c197885cb",
    "Export and retain distribution-signed Apple build 6": "f5b3856c45e8f6cb549ce7b70d8dd99cde92122944d979f19e9c4fc3aecd7b64",
    "Destroy signing material before byte verification": "45dd4b27dfd0b392bb498ab79fd8a4e171b145cd3a0d7d77a67e09f1b78402e7",
    "Byte-verify the complete signed candidate": "2bc8d28ce2b7638fd92f247f4954ae38861e7086fb9d484b687148a47b4a743e",
    "Destroy ephemeral signing material": "ccdb26d408ad203b3dfaab235be7081bb15b073f86099e729260d50bf083309c",
}


def _top_level_block(lines: list[str], key: str) -> list[str] | None:
    header = f"{key}:"
    matches = [index for index, line in enumerate(lines) if line == header]
    if len(matches) != 1:
        return None
    start = matches[0] + 1
    end = len(lines)
    for index in range(start, len(lines)):
        line = lines[index]
        if line and not line.startswith((" ", "#")):
            end = index
            break
    return lines[start:end]


def _job_blocks(lines: list[str]) -> tuple[list[str], dict[str, list[str]]]:
    jobs = _top_level_block(lines, "jobs")
    if jobs is None:
        return [], {}
    headers: list[tuple[int, str]] = []
    for index, line in enumerate(jobs):
        match = re.fullmatch(r"  ([a-z][a-z0-9-]*):", line)
        if match:
            headers.append((index, match.group(1)))
    result: dict[str, list[str]] = {}
    names: list[str] = []
    for position, (index, name) in enumerate(headers):
        end = headers[position + 1][0] if position + 1 < len(headers) else len(jobs)
        names.append(name)
        result[name] = jobs[index + 1 : end]
    return names, result


def _step_block(job: list[str], name: str) -> list[str] | None:
    header = f"      - name: {name}"
    matches = [index for index, line in enumerate(job) if line == header]
    if len(matches) != 1:
        return None
    start = matches[0]
    end = len(job)
    for index in range(start + 1, len(job)):
        if job[index].startswith("      - "):
            end = index
            break
    return job[start:end]


def _literal_run(step: list[str]) -> list[str] | None:
    matches = [index for index, line in enumerate(step) if line == "        run: |"]
    if len(matches) != 1:
        return None
    return [line[10:] for line in step[matches[0] + 1 :] if line.strip()]


def _anonymous_action_steps(job: list[str]) -> list[list[str]]:
    starts = [index for index, line in enumerate(job) if line.startswith("      - ")]
    result: list[list[str]] = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(job)
        step = job[start:end]
        if step[0].startswith("      - uses:"):
            result.append(step)
    return result


def _step_env_block(step: list[str]) -> list[str] | None:
    matches = [index for index, line in enumerate(step) if line == "        env:"]
    if len(matches) != 1:
        return None
    start = matches[0]
    end = start + 1
    while end < len(step) and step[end].startswith("          "):
        end += 1
    return step[start:end]


def _step_inventory(job: list[str]) -> list[tuple[str, str]]:
    inventory: list[tuple[str, str]] = []
    for line in job:
        uses = re.fullmatch(r"      - uses: ([^\s#]+)", line)
        name = re.fullmatch(r"      - name: (.+)", line)
        if uses:
            inventory.append(("uses", uses.group(1)))
        elif name:
            inventory.append(("name", name.group(1)))
        elif line.startswith("      - "):
            inventory.append(("invalid", line.strip()))
    return inventory


def validate_signed_candidate_workflow(text: str) -> list[str]:
    failures: list[str] = []
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != WORKFLOW_SHA256:
        failures.append("workflow bytes differ from the reviewed canonical policy")
    if text.startswith("\ufeff") or "\x00" in text or "\r" in text or "\t" in text:
        failures.append("workflow must use canonical UTF-8 LF text without tabs")
    lines = text.splitlines()
    if re.search(r"(?m)^\s*(?:<<:|[^#\n]*:\s*[\[{])", text):
        failures.append("flow mappings/lists and YAML merge keys are forbidden")
    if re.search(r"(?m)(?:^|\s)[&*][A-Za-z_][A-Za-z0-9_-]*", text):
        failures.append("YAML anchors and aliases are forbidden")

    top_level_keys = [
        match.group(1)
        for line in lines
        if (match := re.fullmatch(r"([a-z][a-z0-9_-]*):(?:.*)?", line))
    ]
    expected_top_level = ["name", "on", "permissions", "concurrency", "jobs"]
    if top_level_keys != expected_top_level:
        failures.append("top-level workflow keys or their order differ from policy")

    trigger = _top_level_block(lines, "on")
    if trigger != ["  workflow_dispatch:", ""]:
        failures.append("workflow trigger must be exactly manual workflow_dispatch")
    permissions = _top_level_block(lines, "permissions")
    if permissions != ["  contents: read", ""]:
        failures.append("top-level permissions must be exactly contents: read")
    concurrency = _top_level_block(lines, "concurrency")
    if concurrency != [
        "  group: signed-candidate-${{ github.ref }}",
        "  cancel-in-progress: false",
        "",
    ]:
        failures.append("workflow concurrency policy differs from canonical form")

    names, jobs = _job_blocks(lines)
    if names != ["build-unsigned", "sign-verify"]:
        failures.append("workflow must contain exactly build-unsigned and sign-verify")
        return failures
    build = jobs["build-unsigned"]
    signing = jobs["sign-verify"]
    build_inventory = _step_inventory(build)
    signing_inventory = _step_inventory(signing)
    if build_inventory != BUILD_STEP_INVENTORY:
        failures.append("unsigned build step inventory differs from policy")
    if signing_inventory != SIGN_STEP_INVENTORY:
        failures.append("signing step inventory differs from policy")
    if any(re.fullmatch(r"\s+uses:.*", line) for line in lines):
        failures.append("uses must appear only as a canonical anonymous step")
    for line in lines:
        if re.fullmatch(r"\s+run:.*", line) and line != "        run: |":
            failures.append("run blocks must use the canonical literal form")
    if f"    if: {REPOSITORY_GUARD}" not in build:
        failures.append("unsigned build job lacks the exact repository/master guard")
    if f"    if: {SIGNING_GUARD}" not in signing:
        failures.append("signing job lacks the exact repository/master/needs guard")
    if "    needs: build-unsigned" not in signing:
        failures.append("signing job must depend on build-unsigned")
    if "    environment: release-signing" not in signing:
        failures.append("signing job must use the release-signing environment")
    if any(line.startswith("    environment:") for line in build):
        failures.append("unsigned build job must not use an environment")
    for job_name, job in jobs.items():
        if any(line.startswith("    env:") for line in job):
            failures.append(f"{job_name} must not define job-level env")
        if any(line.startswith("    permissions:") for line in job):
            failures.append(f"{job_name} must not override permissions")
        if "    runs-on: macos-26" not in job:
            failures.append(f"{job_name} must use the standard macos-26 runner")
    if "secrets." in "\n".join(build) or "secrets[" in "\n".join(build):
        failures.append("unsigned build job must never reference secrets")
    build_text = "\n".join(build)
    if (
        build_text.count("git clone --quiet --no-local --no-checkout --no-tags")
        != 1
        or "git worktree add --detach" in build_text
        or build_text.count('[[ -d "$source_root/.git" ]]') != 1
        or build_text.count(
            '[[ ! -e "$source_root/.git/objects/info/alternates" ]]'
        )
        != 1
    ):
        failures.append(
            "unsigned build source must be an exact standalone non-local Git clone"
        )
    for forbidden_override in FORBIDDEN_GRADLE_VERIFICATION_OVERRIDES:
        if build_text.count(f"'{forbidden_override}'") != 2:
            failures.append(
                "release input gates must forbid every Gradle verification override"
            )
    if build_text.count('[[ "$grep_status" == "1" ]]') != 2:
        failures.append(
            "release input override scans must fail closed on Git errors"
        )
    if (
        build_text.count(
            'git diff --quiet --no-ext-diff "$NIMBO_SOURCE_REVISION" --'
        )
        != 2
        or build_text.count("git ls-files --others -z --") != 2
    ):
        failures.append(
            "release input gates must compare the complete source state before packaging"
        )
    if (
        build_text.count('["ls-files", "-v", "-z", "--"] + source_paths') != 2
        or build_text.count(
            '["ls-tree", "-r", "-z", "--full-tree", revision, "--"]'
        )
        != 2
        or build_text.count(
            '["hash-object", "--no-filters", "--"] + committed_paths'
        )
        != 2
        or build_text.count('marker != b"H"') != 2
        or build_text.count("unsafe release-source index flags") != 2
        or build_text.count(
            "actual release-source bytes differ from authority revision"
        )
        != 2
    ):
        failures.append(
            "release input gates must reject hidden index flags and hash actual source bytes"
        )
    signing_text = "\n".join(signing)
    if "python3 scripts/" in signing_text or 'python3 "$GITHUB_WORKSPACE/scripts/' in signing_text:
        failures.append(
            "signing job must not execute mutable repository Python directly"
        )
    pre_secret_validation = _step_block(
        signing, "Validate and unpack inert unsigned inputs"
    )
    pre_secret_text = (
        "\n".join(pre_secret_validation) if pre_secret_validation is not None else ""
    )
    if (
        pre_secret_text.count('("destination", "export")') != 1
        or "actual_export_options != export_options" not in pre_secret_text
        or "non-upload canonical contract" not in pre_secret_text
    ):
        failures.append(
            "pre-secret validation must enforce the canonical non-upload export options"
        )

    uses = [
        value
        for kind, value in build_inventory + signing_inventory
        if kind == "uses"
    ]
    observed_counts = {name: 0 for name in APPROVED_ACTIONS}
    for reference in uses:
        action, separator, revision = reference.rpartition("@")
        if not separator or APPROVED_ACTIONS.get(action) != revision:
            failures.append(f"action is not pinned to its approved commit: {reference}")
            continue
        observed_counts[action] += 1
    if observed_counts != EXPECTED_ACTION_COUNTS:
        failures.append(
            f"pinned action inventory differs: {observed_counts}"
        )
    for job_name, job, expected_digests in (
        ("unsigned build", build, BUILD_ACTION_STEP_SHA256),
        ("signing", signing, SIGN_ACTION_STEP_SHA256),
    ):
        action_steps = _anonymous_action_steps(job)
        actual_digests = [
            hashlib.sha256(("\n".join(step) + "\n").encode("utf-8")).hexdigest()
            for step in action_steps
        ]
        if actual_digests != expected_digests:
            failures.append(
                f"{job_name} action step blocks differ from policy"
            )

    if "continue-on-error:" in text:
        failures.append("continue-on-error is forbidden in the signing workflow")
    for forbidden in ("BASH_ENV", "SHELLOPTS", "BASHOPTS", "toJSON(secrets", "secrets["):
        if forbidden in text:
            failures.append(f"forbidden workflow construct: {forbidden}")
    for pattern in (
        r"(?mi)^\s*set\s+-[^\n]*x",
        r"(?mi)^\s*set\s+-o\s+(?:xtrace|verbose)",
        r"(?mi)\bbash\s+-(?:[^\s]*x|o\s+xtrace)",
        r"(?mi)\bxtrace\b",
    ):
        if re.search(pattern, text):
            failures.append("shell tracing is forbidden")
            break
    allowed_set_commands = {"set -euo pipefail", "set +e", "set +x"}
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("set ") and stripped not in allowed_set_commands:
            failures.append(f"non-canonical shell option command: {stripped}")

    for local_name, secret_name in SECRET_BINDINGS.items():
        expected = f"          {local_name}: ${{{{ secrets.{secret_name} }}}}"
        if lines.count(expected) != 1:
            failures.append(f"secret binding must occur exactly once: {local_name}")
    secret_references = re.findall(r"\$\{\{\s*secrets\.([A-Z0-9_]+)\s*\}\}", text)
    if sorted(secret_references) != sorted(SECRET_BINDINGS.values()):
        failures.append("secret reference inventory differs from the exact allowlist")

    for step_name in SECRET_STEP_NAMES:
        step = _step_block(signing, step_name)
        if step is None:
            failures.append(f"required secret-consuming step is missing: {step_name}")
            continue
        run = _literal_run(step)
        if run is None or run[:2] != ["set +x", "set -euo pipefail"]:
            failures.append(
                f"secret-consuming step must disable xtrace before strict mode: {step_name}"
            )
        expected_env = ["        env:"] + [
            f"          {local_name}: ${{{{ secrets.{secret_name} }}}}"
            for local_name, secret_name in SECRET_STEP_ENVS[step_name]
        ]
        if _step_env_block(step) != expected_env:
            failures.append(
                f"secret-consuming step env differs from policy: {step_name}"
            )
    for job_name, job, expected_hashes in (
        ("unsigned build", build, BUILD_RUN_SHA256),
        ("signing", signing, SIGN_RUN_SHA256),
    ):
        for step_name, expected_digest in expected_hashes.items():
            step = _step_block(job, step_name)
            if step is None or step.count("        shell: bash") != 1 or any(
                line.startswith("        shell:") and line != "        shell: bash"
                for line in step or []
            ):
                failures.append(
                    f"{job_name} run step shell differs from policy: {step_name}"
                )
            run = _literal_run(step) if step is not None else None
            actual_digest = (
                hashlib.sha256(("\n".join(run) + "\n").encode("utf-8")).hexdigest()
                if run is not None
                else None
            )
            if actual_digest != expected_digest:
                failures.append(f"{job_name} run block differs from policy: {step_name}")
    cleanup = _step_block(signing, "Destroy ephemeral signing material")
    if (
        sum(line == "        if: always()" for line in signing) != 1
        or cleanup is None
        or "        if: always()" not in cleanup
    ):
        failures.append("only the final signing cleanup step may use always()")
    if cleanup is None or signing[-len(cleanup) :] != cleanup:
        failures.append("signing cleanup must be the final step")

    required_markers = (
        "git clone --quiet --no-local --no-checkout --no-tags",
        "git worktree add --detach",
        "Validate and seal exact release inputs",
        "Verify exact release inputs remained sealed",
        "release inputs must not override Gradle dependency verification",
        "CODE_SIGNING_ALLOWED=NO",
        "base/root/META-INF/version-control-info.textproto",
        '("destination", "export")',
        "ExportOptions.plist differs from the non-upload canonical contract",
        "runpy.run_path(str(script), run_name=\"__main__\")",
        "--package-output \"$NIMBO_PACKAGE_ROOT/signed-candidate-bytes.tar.gz\"",
        "1294eec2eb8a0c0a1ff928bf2963a46dcbc600b42eaa840c53f3c5ec537956fa",
        "8b99c81951002b19cb6d0c096871e36f222ec2df6fac762603442e194fc41a99",
        "Destroy signing material before byte verification",
        "a099cfa1543f55593bc2ed16a70a7c67fe54b1747bb7301f37fdfd6d91028e29",
        "fd4d8668a7e0f4eb9f64a12b5f0ddec0075ccde31dad50a96e978926e0e743f1",
        "candidate-bytes-verified-not-manifest-promoted",
    )
    uncommented = "\n".join(line for line in lines if not line.lstrip().startswith("#"))
    for marker in required_markers:
        if marker not in uncommented:
            failures.append(f"workflow contract marker is missing: {marker}")
    for filename, digest in REVIEWED_VERIFIER_SHA256.items():
        if text.count(digest) != 2:
            failures.append(
                f"reviewed verifier digest pin count differs: {filename}"
            )
    if "-storepass" in text or "-keypass" in text:
        failures.append("Android passwords must not appear in command arguments")
    return failures
