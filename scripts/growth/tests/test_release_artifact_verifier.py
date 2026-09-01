from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import plistlib
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from datetime import datetime
from unittest import mock

from scripts.release_artifact_verifier import (
    ANDROID_PACKAGE_ID,
    APPLE_DISTRIBUTION_CERTIFICATE_SHA256,
    APPLE_TEAM_ID,
    EXPECTED_POLICY,
    StaticArtifactContractResult,
    VerificationResult,
    _validate_artifact_contract,
    _verify_current_artifact_bytes,
    validate_manifest_artifact_contract,
    validate_repository_source,
    validate_verification_policy,
    verify_manifest_artifacts,
    verify_signed_candidate_artifacts,
)


ROOT = Path(__file__).resolve().parents[3]


class ReleaseArtifactVerifierTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        (self.root / "app").mkdir()
        (self.root / "wearApp").mkdir()
        (self.root / "iosApp/Nimbo.xcodeproj").mkdir(parents=True)
        (self.root / "app/build.gradle.kts").write_text(
            'versionName = "1.1.0"\nversionCode = 8\n',
            encoding="utf-8",
        )
        (self.root / "wearApp/build.gradle.kts").write_text(
            'versionName = "1.1.0"\nversionCode = 1_000_008\n',
            encoding="utf-8",
        )
        (self.root / "iosApp/project.yml").write_text(
            "MARKETING_VERSION: 1.1.0\nCURRENT_PROJECT_VERSION: 6\n",
            encoding="utf-8",
        )
        (self.root / "iosApp/Nimbo.xcodeproj/project.pbxproj").write_text(
            "MARKETING_VERSION = 1.1.0;\nCURRENT_PROJECT_VERSION = 6;\n",
            encoding="utf-8",
        )
        for arguments in (
            ["init", "-q"],
            ["config", "user.email", "verifier@example.invalid"],
            ["config", "user.name", "Verifier Fixture"],
            ["add", "app", "wearApp", "iosApp"],
            ["commit", "-q", "-m", "fixture release source"],
        ):
            subprocess.run(
                ["git", *arguments],
                cwd=self.root,
                check=True,
                capture_output=True,
                text=True,
            )
        self.source_revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        self.quality_root = self.root / "growth/quality"
        self.quality_root.mkdir(parents=True)
        (self.quality_root / "source.md").write_text(
            f"source revision: {self.source_revision}\n",
            encoding="utf-8",
        )
        self.historical_hashes = {
            "android_phone": "a" * 64,
            "wear_os": "b" * 64,
            "apple": "c" * 64,
        }
        (self.quality_root / "historical-signing.md").write_text(
            "\n".join(self.historical_hashes.values()) + "\n",
            encoding="utf-8",
        )
        (self.quality_root / "historical-physical.md").write_text(
            "historical device result\n"
            + "\n".join(self.historical_hashes.values())
            + "\n",
            encoding="utf-8",
        )
        subprocess.run(
            ["git", "add", "growth/quality"],
            cwd=self.root,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-q", "-m", "fixture evidence"],
            cwd=self.root,
            check=True,
        )
        self.artifact_root = self.root / "artifacts"
        self.artifact_root.mkdir()
        self.bundletool = self.root / "bundletool-all.jar"
        self.bundletool.write_bytes(b"pinned test bundletool")
        self.bundletool_sha256 = hashlib.sha256(
            self.bundletool.read_bytes()
        ).hexdigest()
        self.android_certificate_der = b"fixture-android-certificate-der"
        self.android_certificate_sha256 = hashlib.sha256(
            self.android_certificate_der
        ).hexdigest()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def manifest(self, verified_artifact: str | None = None) -> dict:
        artifacts = {
            "android_phone": {
                "filename": "nimbo-phone-1.1.0-vc8.aab",
                "version_code": 8,
                "source_sync": "blocked",
                "sha256": None,
                "signing_evidence": None,
                "physical_qa_evidence": None,
                "source_sync_evidence": "growth/quality/source.md",
                "historical_candidate": {
                    "status": "historical-superseded",
                    "filename": "nimbo-phone-1.1.0-vc7.aab",
                    "version_code": 7,
                    "sha256": self.historical_hashes["android_phone"],
                    "signing_evidence": "growth/quality/historical-signing.md",
                    "physical_qa_evidence": "growth/quality/historical-physical.md",
                },
            },
            "wear_os": {
                "filename": "nimbo-wear-1.1.0-vc1000008.aab",
                "version_code": 1_000_008,
                "source_sync": "blocked",
                "sha256": None,
                "signing_evidence": None,
                "physical_qa_evidence": None,
                "source_sync_evidence": "growth/quality/source.md",
                "historical_candidate": {
                    "status": "historical-superseded",
                    "filename": "nimbo-wear-1.1.0-vc1000008.aab",
                    "version_code": 1_000_008,
                    "sha256": self.historical_hashes["wear_os"],
                    "signing_evidence": "growth/quality/historical-signing.md",
                    "physical_qa_evidence": None,
                },
            },
            "apple": {
                "filename": "Nimbo.ipa",
                "build": 6,
                "source_sync": "blocked",
                "sha256": None,
                "signing_evidence": None,
                "physical_qa_evidence": None,
                "source_sync_evidence": "growth/quality/source.md",
                "historical_candidate": {
                    "status": "historical-superseded",
                    "filename": "Nimbo.ipa",
                    "build": 5,
                    "sha256": self.historical_hashes["apple"],
                    "signing_evidence": "growth/quality/historical-signing.md",
                    "physical_qa_evidence": "growth/quality/historical-physical.md",
                },
            },
        }
        if verified_artifact is not None:
            artifacts[verified_artifact]["source_sync"] = "verified-current"
            artifacts[verified_artifact]["historical_candidate"] = None
            artifacts[verified_artifact]["signing_evidence"] = (
                f"growth/quality/current-{verified_artifact}.md"
            )
        return {
            "schema_version": 2,
            "release": "1.1.0",
            "source_revision": self.source_revision,
            "verification_policy": copy.deepcopy(EXPECTED_POLICY),
            "artifacts": artifacts,
        }

    def write_current_evidence(self, manifest: dict) -> None:
        written: list[str] = []
        for artifact_id, artifact in manifest["artifacts"].items():
            if artifact["source_sync"] != "verified-current":
                continue
            digest = artifact.get("sha256")
            if isinstance(digest, str):
                (self.root / artifact["signing_evidence"]).write_text(
                    f"verified artifact SHA-256: {digest}\n",
                    encoding="utf-8",
                )
                written.append(artifact["signing_evidence"])
        if written:
            subprocess.run(
                ["git", "add", "--", *written],
                cwd=self.root,
                check=True,
            )
            staged = subprocess.run(
                ["git", "diff", "--cached", "--quiet"],
                cwd=self.root,
                check=False,
            )
            if staged.returncode == 1:
                subprocess.run(
                    ["git", "commit", "-q", "-m", "fixture current evidence"],
                    cwd=self.root,
                    check=True,
                )

    def promote_all(self, manifest: dict, digest: str = "d" * 64) -> None:
        for artifact_id, artifact in manifest["artifacts"].items():
            artifact["source_sync"] = "verified-current"
            artifact["historical_candidate"] = None
            artifact["sha256"] = digest
            artifact["signing_evidence"] = (
                f"growth/quality/current-{artifact_id}.md"
            )
        self.write_current_evidence(manifest)

    def write_android_bundle(
        self,
        filename: str,
        *,
        revision: str | None = None,
    ) -> Path:
        path = self.artifact_root / filename
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("BundleConfig.pb", b"bundle config")
            archive.writestr("META-INF/NIMBO.SF", b"signature manifest")
            archive.writestr("META-INF/NIMBO.RSA", b"signature block")
            archive.writestr(
                "base/manifest/AndroidManifest.xml",
                b"compiled manifest placeholder",
            )
            archive.writestr(
                "base/root/META-INF/version-control-info.textproto",
                "repositories {\n"
                "  system: GIT\n"
                f'  revision: "{revision or self.source_revision}"\n'
                "}\n",
            )
            archive.writestr("base/dex/classes.dex", b"payload")
            if "phone" in filename:
                archive.writestr(
                    "BUNDLE-METADATA/com.android.tools.build.obfuscation/proguard.map",
                    self.android_mapping_text(),
                )
        return path

    @staticmethod
    def android_mapping_text() -> str:
        return (
            "# compiler: R8\n"
            "# compiler_version: 9.3.16\n"
            "# min_api: 24\n"
            "# common_typos_disable\n"
            '# {"id":"com.android.tools.r8.mapping","version":"2.2"}\n'
            "# pg_map_id: fixture-map-id\n"
            "# pg_map_hash: SHA-256 fixture-map-hash\n"
            "Example -> a:\n"
        )

    def write_android_mapping(self, manifest: dict) -> Path:
        filename = manifest["artifacts"]["android_phone"]["filename"]
        path = self.artifact_root / f"{Path(filename).stem}-mapping.txt"
        path.write_text(self.android_mapping_text(), encoding="utf-8")
        return path

    def write_apple_candidate(
        self,
        *,
        include_revision: bool = True,
        include_archive_app: bool = True,
    ) -> Path:
        payload_root = self.root / "apple-payload"
        app = payload_root / "Payload/Nimbo.app"
        products = (
            (
                app,
                {
                    "CFBundleIdentifier": "uz.ganikhodjaev.weather",
                    "CFBundleExecutable": "Nimbo",
                    "MinimumOSVersion": "15.0",
                    "DTPlatformName": "iphoneos",
                    "CFBundleSupportedPlatforms": ["iPhoneOS"],
                    "UIDeviceFamily": [1, 2],
                    "ITSAppUsesNonExemptEncryption": False,
                },
            ),
            (
                app / "PlugIns/NimboWidget.appex",
                {
                    "CFBundleIdentifier": "uz.ganikhodjaev.weather.widget",
                    "CFBundleExecutable": "NimboWidget",
                    "MinimumOSVersion": "15.0",
                    "DTPlatformName": "iphoneos",
                    "CFBundleSupportedPlatforms": ["iPhoneOS"],
                    "UIDeviceFamily": [1, 2],
                },
            ),
            (
                app / "Watch/NimboWatch.app",
                {
                    "CFBundleIdentifier": (
                        "uz.ganikhodjaev.weather.watchkitapp"
                    ),
                    "CFBundleExecutable": "NimboWatch",
                    "MinimumOSVersion": "10.0",
                    "DTPlatformName": "watchos",
                    "CFBundleSupportedPlatforms": ["WatchOS"],
                    "UIDeviceFamily": [4],
                    "WKApplication": True,
                    "WKCompanionAppBundleIdentifier": "uz.ganikhodjaev.weather",
                },
            ),
        )
        for bundle, values in products:
            bundle.mkdir(parents=True, exist_ok=True)
            info = {
                **values,
                "CFBundleShortVersionString": "1.1.0",
                "CFBundleVersion": "6",
            }
            if include_revision:
                info["NimboSourceRevision"] = self.source_revision
            (bundle / "Info.plist").write_bytes(plistlib.dumps(info))
            (bundle / str(values["CFBundleExecutable"])).write_bytes(b"mach-o")
            (bundle / "embedded.mobileprovision").write_bytes(b"profile")

        ipa = self.artifact_root / "Nimbo.ipa"
        with zipfile.ZipFile(ipa, "w") as archive:
            for source in sorted(payload_root.rglob("*")):
                if source.is_file():
                    archive.write(source, source.relative_to(payload_root).as_posix())

        archive_root = self.artifact_root / "Nimbo.xcarchive"
        archive_root.mkdir()
        archive_info = {
            "ApplicationProperties": {
                "CFBundleIdentifier": "uz.ganikhodjaev.weather",
                "CFBundleShortVersionString": "1.1.0",
                "CFBundleVersion": "6",
                "Team": APPLE_TEAM_ID,
            }
        }
        (archive_root / "Info.plist").write_bytes(plistlib.dumps(archive_info))
        if include_archive_app:
            shutil.copytree(
                app,
                archive_root / "Products/Applications/Nimbo.app",
            )
        for name, executable in (
            ("Nimbo.app.dSYM", "Nimbo"),
            ("NimboWidget.appex.dSYM", "NimboWidget"),
            ("NimboWatch.app.dSYM", "NimboWatch"),
        ):
            dwarf = (
                archive_root
                / "dSYMs"
                / name
                / "Contents/Resources/DWARF"
                / executable
            )
            dwarf.parent.mkdir(parents=True, exist_ok=True)
            dwarf.write_bytes(b"debug")
        (self.artifact_root / "ExportOptions.plist").write_bytes(
            plistlib.dumps(
                {
                    "destination": "export",
                    "method": "app-store-connect",
                    "signingCertificate": "Apple Distribution",
                    "signingStyle": "automatic",
                    "teamID": APPLE_TEAM_ID,
                    "uploadSymbols": True,
                    "manageAppVersionAndBuildNumber": False,
                    "provisioningProfiles": {
                        ANDROID_PACKAGE_ID: (
                            "iOS Team Store Provisioning Profile: "
                            + ANDROID_PACKAGE_ID
                        ),
                        f"{ANDROID_PACKAGE_ID}.watchkitapp": (
                            "iOS Team Store Provisioning Profile: "
                            f"{ANDROID_PACKAGE_ID}.watchkitapp"
                        ),
                        f"{ANDROID_PACKAGE_ID}.widget": (
                            "iOS Team Store Provisioning Profile: "
                            f"{ANDROID_PACKAGE_ID}.widget"
                        ),
                    },
                }
            )
        )
        return ipa

    @staticmethod
    def _apple_role(path: str) -> str:
        if "NimboWidget.appex" in path:
            return "widget"
        if "NimboWatch.app" in path:
            return "watch"
        return "app"

    def apple_runner(
        self,
        command: list[str],
        *,
        text: bool = True,
        timeout: int = 120,
        certificate_bytes: bytes = b"fixture-apple-certificate",
        expiration: datetime = datetime(2099, 1, 1),
        archive_uuid_mismatch: bool = False,
    ) -> subprocess.CompletedProcess:
        del timeout
        executable = Path(command[0]).name
        output: str | bytes = ""
        error: str | bytes = ""
        return_code = 0
        target = command[-1]
        is_archive_target = (
            "Nimbo.xcarchive/Products/Applications" in target
        )
        signing_certificate_bytes = (
            b"fixture-apple-development-certificate"
            if is_archive_target
            else certificate_bytes
        )
        role = self._apple_role(target)
        bundle_id = {
            "app": "uz.ganikhodjaev.weather",
            "widget": "uz.ganikhodjaev.weather.widget",
            "watch": "uz.ganikhodjaev.weather.watchkitapp",
        }[role]
        groups = (
            ["group.uz.ganikhodjaev.weather"]
            if role in {"app", "widget"}
            else []
        )

        if executable == "codesign" and any(
            argument.startswith("--extract-certificates=") for argument in command
        ):
            prefix_argument = next(
                argument
                for argument in command
                if argument.startswith("--extract-certificates=")
            )
            Path(f"{prefix_argument.split('=', 1)[1]}0").write_bytes(
                signing_certificate_bytes
            )
        elif executable == "codesign" and "--entitlements" in command:
            entitlements = {
                "application-identifier": f"{APPLE_TEAM_ID}.{bundle_id}",
                "com.apple.developer.team-identifier": APPLE_TEAM_ID,
                "get-task-allow": is_archive_target,
                "com.apple.security.application-groups": groups,
            }
            if not is_archive_target:
                entitlements["beta-reports-active"] = True
            output = plistlib.dumps(entitlements)
        elif executable == "codesign" and "-d" in command:
            authority = (
                "Apple Development: Fixture"
                if is_archive_target
                else "Apple Distribution: Fixture"
            )
            error = (
                f"Authority={authority} ({APPLE_TEAM_ID})\n"
                f"TeamIdentifier={APPLE_TEAM_ID}\n"
            )
        elif executable == "security":
            profile_entitlements = {
                "application-identifier": (
                    f"{APPLE_TEAM_ID}.*"
                    if is_archive_target and role == "watch"
                    else f"{APPLE_TEAM_ID}.{bundle_id}"
                ),
                "get-task-allow": is_archive_target,
                "com.apple.security.application-groups": groups,
            }
            if not is_archive_target:
                profile_entitlements["beta-reports-active"] = True
            profile = {
                "UUID": {
                    "app": "11111111-1111-1111-1111-111111111111",
                    "widget": "22222222-2222-2222-2222-222222222222",
                    "watch": "33333333-3333-3333-3333-333333333333",
                }[role],
                "Name": (
                    f"Fixture Development Profile: {bundle_id}"
                    if is_archive_target
                    else f"iOS Team Store Provisioning Profile: {bundle_id}"
                ),
                "TeamIdentifier": [APPLE_TEAM_ID],
                "ExpirationDate": expiration,
                "DeveloperCertificates": [signing_certificate_bytes],
                "Entitlements": profile_entitlements,
            }
            if is_archive_target:
                profile["ProvisionedDevices"] = ["fixture-device"]
            output = plistlib.dumps(profile)
        elif executable == "openssl":
            certificate_path = Path(command[command.index("-in") + 1])
            fingerprint = hashlib.sha256(
                certificate_path.read_bytes()
            ).hexdigest().upper()
            grouped = ":".join(
                fingerprint[index : index + 2]
                for index in range(0, len(fingerprint), 2)
            )
            output = f"sha256 Fingerprint={grouped}\n"
        elif executable == "xcrun" and "lipo" in command:
            output = "arm64 arm64_32\n" if role == "watch" else "arm64\n"
        elif executable == "xcrun" and "--uuid" in command:
            values = {
                "app": [("AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA", "arm64")],
                "widget": [("BBBBBBBB-BBBB-BBBB-BBBB-BBBBBBBBBBBB", "arm64")],
                "watch": [
                    ("CCCCCCCC-CCCC-CCCC-CCCC-CCCCCCCCCCCC", "arm64"),
                    ("DDDDDDDD-DDDD-DDDD-DDDD-DDDDDDDDDDDD", "arm64_32"),
                ],
            }[role]
            if (
                archive_uuid_mismatch
                and role == "app"
                and "Nimbo.xcarchive/Products/Applications" in target
            ):
                values = [("EEEEEEEE-EEEE-EEEE-EEEE-EEEEEEEEEEEE", "arm64")]
            output = "".join(
                f"UUID: {uuid} ({architecture}) {target}\n"
                for uuid, architecture in values
            )

        if text:
            if isinstance(output, bytes):
                output = output.decode("utf-8")
            if isinstance(error, bytes):
                error = error.decode("utf-8")
        else:
            if isinstance(output, str):
                output = output.encode("utf-8")
            if isinstance(error, str):
                error = error.encode("utf-8")
        return subprocess.CompletedProcess(command, return_code, output, error)

    def runner(
        self,
        command: list[str],
        *,
        text: bool = True,
        timeout: int = 120,
        jarsigner_output: str = "jar verified.",
        certificate: str | None = None,
        certificate_der: bytes | None = None,
        wear_required: bool = True,
    ) -> subprocess.CompletedProcess:
        del timeout
        if certificate is None:
            certificate = self.android_certificate_sha256
        if certificate_der is None:
            certificate_der = self.android_certificate_der
        executable = Path(command[0]).name
        if executable == "jarsigner":
            stdout = jarsigner_output
        elif executable == "keytool":
            if "-rfc" in command:
                stdout = (
                    "-----BEGIN CERTIFICATE-----\n"
                    "dGVzdC1jZXJ0aWZpY2F0ZQ==\n"
                    "-----END CERTIFICATE-----\n"
                )
            else:
                grouped = ":".join(
                    certificate[index : index + 2].upper()
                    for index in range(0, len(certificate), 2)
                )
                stdout = (
                    f"Certificate fingerprints:\n SHA256: {grouped}\n"
                    "Signature algorithm name: SHA256withRSA\n"
                    "Subject Public Key Algorithm: 2048-bit RSA key\n"
                )
        elif executable == "openssl" and "x509" in command:
            stdout = certificate_der
        elif executable == "openssl":
            stdout = "upload-certificate.pem: OK\n"
        elif executable == "java" and command[-1] == "version":
            stdout = "1.18.3\n"
        elif executable == "java" and "validate" in command:
            stdout = "App Bundle information\n"
        elif executable == "java" and "manifest" in command:
            is_wear = any("wear" in argument for argument in command)
            version_code = 1_000_008 if is_wear else 8
            min_sdk = 30 if is_wear else 24
            watch = (
                '<uses-feature android:name="android.hardware.type.watch" '
                f'android:required="{str(wear_required).lower()}"/>'
                if is_wear
                else ""
            )
            metadata = (
                '<application><meta-data '
                'android:name="com.google.android.wearable.standalone" '
                'android:value="false"/></application>'
                if is_wear
                else "<application/>"
            )
            stdout = (
                '<manifest xmlns:android="http://schemas.android.com/apk/res/android" '
                'package="uz.ganikhodjaev.weather" '
                f'android:versionCode="{version_code}" android:versionName="1.1.0">'
                f'<uses-sdk android:minSdkVersion="{min_sdk}" '
                'android:targetSdkVersion="36"/>'
                f"{watch}{metadata}</manifest>"
            )
        else:
            return subprocess.CompletedProcess(command, 1, "", "unexpected command")
        if text:
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")
            return subprocess.CompletedProcess(command, 0, stdout, "")
        if isinstance(stdout, str):
            stdout = stdout.encode()
        return subprocess.CompletedProcess(command, 0, stdout, b"")

    def verify_android(
        self,
        manifest: dict,
        *,
        jarsigner_output: str = "jar verified.",
        certificate: str | None = None,
        certificate_der: bytes | None = None,
        wear_required: bool = True,
    ) -> tuple[dict, list[str]]:
        failures: list[str] = []
        self.write_current_evidence(manifest)
        artifact_id = next(
            artifact_id
            for artifact_id, artifact in manifest["artifacts"].items()
            if artifact["source_sync"] == "verified-current"
        )

        def runner(command: list[str], **kwargs: object) -> subprocess.CompletedProcess:
            return self.runner(
                command,
                text=bool(kwargs.get("text", True)),
                timeout=int(kwargs.get("timeout", 120)),
                jarsigner_output=jarsigner_output,
                certificate=certificate,
                certificate_der=certificate_der,
                wear_required=wear_required,
            )

        with (
            mock.patch(
                "scripts.release_artifact_verifier.BUNDLETOOL_SHA256",
                self.bundletool_sha256,
            ),
            mock.patch(
                "scripts.release_artifact_verifier.ANDROID_UPLOAD_CERTIFICATE_SHA256",
                self.android_certificate_sha256,
            ),
        ):
            policy_valid = validate_verification_policy(manifest, failures)
            source_valid = validate_repository_source(
                self.root,
                manifest.get("source_revision"),
                failures,
            )
            contract_valid = _validate_artifact_contract(
                self.root,
                manifest,
                manifest["artifacts"],
                failures,
                enforce_atomic_promotion=False,
            )
            valid = policy_valid and source_valid and contract_valid
            result = (
                _verify_current_artifact_bytes(
                    artifact_id,
                    manifest["artifacts"][artifact_id],
                    manifest,
                    self.artifact_root,
                    self.bundletool,
                    failures,
                    runner,
                )
                if valid
                else VerificationResult(
                    artifact_id=artifact_id,
                    source_sync="verified-current",
                    byte_verified=False,
                )
            )
            results = {artifact_id: result}
        return results, failures

    def verify_apple(
        self,
        manifest: dict,
        *,
        expiration: datetime = datetime(2099, 1, 1),
        archive_uuid_mismatch: bool = False,
    ) -> tuple[dict, list[str]]:
        failures: list[str] = []
        self.write_current_evidence(manifest)
        artifact_id = "apple"
        certificate_bytes = b"fixture-apple-certificate"

        def runner(command: list[str], **kwargs: object) -> subprocess.CompletedProcess:
            return self.apple_runner(
                command,
                text=bool(kwargs.get("text", True)),
                timeout=int(kwargs.get("timeout", 120)),
                certificate_bytes=certificate_bytes,
                expiration=expiration,
                archive_uuid_mismatch=archive_uuid_mismatch,
            )

        with (
            mock.patch(
                "scripts.release_artifact_verifier.APPLE_DISTRIBUTION_CERTIFICATE_SHA256",
                hashlib.sha256(certificate_bytes).hexdigest(),
            ),
            mock.patch(
                "scripts.release_artifact_verifier._required_system_tool",
                side_effect=lambda path, owner, failures: str(path),
            ),
        ):
            policy_valid = validate_verification_policy(manifest, failures)
            source_valid = validate_repository_source(
                self.root,
                manifest.get("source_revision"),
                failures,
            )
            contract_valid = _validate_artifact_contract(
                self.root,
                manifest,
                manifest["artifacts"],
                failures,
                enforce_atomic_promotion=False,
            )
            valid = policy_valid and source_valid and contract_valid
            result = (
                _verify_current_artifact_bytes(
                    artifact_id,
                    manifest["artifacts"][artifact_id],
                    manifest,
                    self.artifact_root,
                    None,
                    failures,
                    runner,
                )
                if valid
                else VerificationResult(
                    artifact_id=artifact_id,
                    source_sync="verified-current",
                    byte_verified=False,
                )
            )
            results = {artifact_id: result}
        return results, failures

    def test_repository_manifest_passes_static_current_contract(self) -> None:
        manifest = json.loads(
            (ROOT / "store/upload-manifest-1.1.0.json").read_text(encoding="utf-8")
        )
        failures: list[str] = []

        results = validate_manifest_artifact_contract(ROOT, manifest, failures)

        self.assertEqual(failures, [])
        self.assertEqual(set(results), {"android_phone", "wear_os", "apple"})
        self.assertTrue(
            all(
                result.source_sync == "verified-current"
                for result in results.values()
            )
        )
        self.assertTrue(all(result.contract_valid for result in results.values()))
        self.assertTrue(
            all(not hasattr(result, "byte_verified") for result in results.values())
        )

    def test_static_contract_has_no_byte_verification_surface(self) -> None:
        manifest = self.manifest()
        failures: list[str] = []

        results = validate_manifest_artifact_contract(
            self.root,
            manifest,
            failures,
        )

        self.assertEqual(failures, [])
        self.assertTrue(all(result.contract_valid for result in results.values()))
        self.assertTrue(
            all(not hasattr(result, "byte_verified") for result in results.values())
        )

    def test_print_source_revision_uses_static_contract_only(self) -> None:
        from scripts import verify_release_artifacts as cli

        manifest = self.manifest()
        static_results = {
            artifact_id: StaticArtifactContractResult(
                artifact_id=artifact_id,
                source_sync="blocked",
                contract_valid=True,
            )
            for artifact_id in ("android_phone", "wear_os", "apple")
        }
        output = io.StringIO()
        with (
            mock.patch.object(cli, "load_manifest", return_value=manifest),
            mock.patch.object(
                cli,
                "validate_manifest_artifact_contract",
                return_value=static_results,
            ) as static_validator,
            mock.patch.object(
                cli,
                "verify_manifest_artifacts",
                side_effect=AssertionError("full byte verifier must not run"),
            ),
            mock.patch("sys.argv", ["verify_release_artifacts.py", "--print-source-revision"]),
            mock.patch("sys.stdout", output),
        ):
            exit_code = cli.main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(output.getvalue(), f"{self.source_revision}\n")
        static_validator.assert_called_once()

    def test_static_contract_accepts_only_atomic_current_promotion(self) -> None:
        for promoted in (1, 2):
            with self.subTest(promoted=promoted):
                manifest = self.manifest()
                for artifact_id in tuple(manifest["artifacts"])[:promoted]:
                    artifact = manifest["artifacts"][artifact_id]
                    artifact["source_sync"] = "verified-current"
                    artifact["historical_candidate"] = None
                    artifact["sha256"] = "d" * 64
                    artifact["signing_evidence"] = (
                        f"growth/quality/current-{artifact_id}.md"
                    )
                self.write_current_evidence(manifest)
                failures: list[str] = []

                results = validate_manifest_artifact_contract(
                    self.root,
                    manifest,
                    failures,
                )

                self.assertTrue(
                    any(
                        "release artifact promotion must be atomic" in failure
                        for failure in failures
                    )
                )
                self.assertTrue(
                    all(not result.contract_valid for result in results.values())
                )

        manifest = self.manifest()
        self.promote_all(manifest)
        failures = []

        results = validate_manifest_artifact_contract(
            self.root,
            manifest,
            failures,
        )

        self.assertEqual(failures, [])
        self.assertTrue(all(result.contract_valid for result in results.values()))

    def test_complete_blocked_manifest_can_verify_staged_signed_candidate(
        self,
    ) -> None:
        manifest = self.manifest()
        for artifact_id in ("android_phone", "wear_os"):
            self.write_android_bundle(manifest["artifacts"][artifact_id]["filename"])
        mapping_path = self.write_android_mapping(manifest)
        self.write_apple_candidate()
        failures: list[str] = []
        apple_certificate = b"fixture-apple-certificate"

        def candidate_runner(
            command: list[str], **kwargs: object
        ) -> subprocess.CompletedProcess:
            executable = Path(command[0]).name
            if executable in {"codesign", "security", "xcrun"} or (
                executable == "openssl" and "-fingerprint" in command
            ):
                return self.apple_runner(
                    command,
                    text=bool(kwargs.get("text", True)),
                    timeout=int(kwargs.get("timeout", 120)),
                    certificate_bytes=apple_certificate,
                )
            return self.runner(
                command,
                text=bool(kwargs.get("text", True)),
                timeout=int(kwargs.get("timeout", 120)),
            )

        with (
            mock.patch(
                "scripts.release_artifact_verifier.BUNDLETOOL_SHA256",
                self.bundletool_sha256,
            ),
            mock.patch(
                "scripts.release_artifact_verifier.ANDROID_UPLOAD_CERTIFICATE_SHA256",
                self.android_certificate_sha256,
            ),
            mock.patch(
                "scripts.release_artifact_verifier.APPLE_DISTRIBUTION_CERTIFICATE_SHA256",
                hashlib.sha256(apple_certificate).hexdigest(),
            ),
            mock.patch(
                "scripts.release_artifact_verifier._required_system_tool",
                side_effect=lambda path, owner, failures: str(path),
            ),
        ):
            verification = verify_signed_candidate_artifacts(
                self.root,
                manifest,
                failures,
                artifact_root=self.artifact_root,
                bundletool_jar=self.bundletool,
                runner=candidate_runner,
            )
        results = verification.artifacts

        self.assertEqual(failures, [])
        self.assertTrue(verification.byte_verified)
        self.assertEqual(set(results), {"android_phone", "wear_os", "apple"})
        self.assertTrue(all(result.byte_verified for result in results.values()))
        self.assertTrue(
            all(
                result.source_sync == "candidate-verified"
                for result in results.values()
            )
        )
        for artifact_id, result in results.items():
            expected = self.artifact_root / manifest["artifacts"][artifact_id][
                "filename"
            ]
            self.assertEqual(
                result.sha256,
                hashlib.sha256(expected.read_bytes()).hexdigest(),
            )
        self.assertEqual(
            verification.candidate_set["phone_mapping"]["sha256"],
            hashlib.sha256(mapping_path.read_bytes()).hexdigest(),
        )
        self.assertIn("apple_archive", verification.candidate_set)
        self.assertEqual(
            set(verification.candidate_set["apple_dsyms"]),
            {"app", "widget", "watch"},
        )

    def test_candidate_preflight_rejects_already_promoted_manifest(self) -> None:
        manifest = self.manifest("android_phone")
        failures: list[str] = []

        verification = verify_signed_candidate_artifacts(
            self.root,
            manifest,
            failures,
            artifact_root=self.artifact_root,
            bundletool_jar=self.bundletool,
            runner=self.runner,
        )
        results = verification.artifacts

        self.assertTrue(
            any(
                "preflight requires the committed manifest to remain blocked"
                in failure
                for failure in failures
            )
        )
        self.assertTrue(all(not result.byte_verified for result in results.values()))

    def test_candidate_preflight_rejects_source_byte_mutation(self) -> None:
        manifest = self.manifest()
        for artifact_id in ("android_phone", "wear_os"):
            self.write_android_bundle(manifest["artifacts"][artifact_id]["filename"])
        self.write_android_mapping(manifest)
        self.write_apple_candidate()
        phone_path = self.artifact_root / manifest["artifacts"]["android_phone"][
            "filename"
        ]
        failures: list[str] = []
        mutated = False
        apple_certificate = b"fixture-apple-certificate"

        def mutating_runner(
            command: list[str], **kwargs: object
        ) -> subprocess.CompletedProcess:
            nonlocal mutated
            if not mutated:
                phone_path.write_bytes(phone_path.read_bytes() + b"mutated")
                mutated = True
            executable = Path(command[0]).name
            if executable in {"codesign", "security", "xcrun"} or (
                executable == "openssl" and "-fingerprint" in command
            ):
                return self.apple_runner(
                    command,
                    text=bool(kwargs.get("text", True)),
                    timeout=int(kwargs.get("timeout", 120)),
                    certificate_bytes=apple_certificate,
                )
            return self.runner(
                command,
                text=bool(kwargs.get("text", True)),
                timeout=int(kwargs.get("timeout", 120)),
            )

        with (
            mock.patch(
                "scripts.release_artifact_verifier.BUNDLETOOL_SHA256",
                self.bundletool_sha256,
            ),
            mock.patch(
                "scripts.release_artifact_verifier.ANDROID_UPLOAD_CERTIFICATE_SHA256",
                self.android_certificate_sha256,
            ),
            mock.patch(
                "scripts.release_artifact_verifier.APPLE_DISTRIBUTION_CERTIFICATE_SHA256",
                hashlib.sha256(apple_certificate).hexdigest(),
            ),
            mock.patch(
                "scripts.release_artifact_verifier._required_system_tool",
                side_effect=lambda path, owner, failures: str(path),
            ),
        ):
            verification = verify_signed_candidate_artifacts(
                self.root,
                manifest,
                failures,
                artifact_root=self.artifact_root,
                bundletool_jar=self.bundletool,
                runner=mutating_runner,
            )
        results = verification.artifacts

        self.assertTrue(mutated)
        self.assertTrue(
            any(
                "source tree changed during verification" in failure
                for failure in failures
            )
        )
        self.assertFalse(verification.byte_verified)
        self.assertFalse(results["android_phone"].byte_verified)

    def test_candidate_rejects_stale_manifest_against_current_checkout(self) -> None:
        manifest = self.manifest()
        with tempfile.TemporaryDirectory() as worktree_directory:
            old_source = Path(worktree_directory) / "source"
            subprocess.run(
                [
                    "git",
                    "worktree",
                    "add",
                    "--detach",
                    str(old_source),
                    self.source_revision,
                ],
                cwd=self.root,
                check=True,
                capture_output=True,
                text=True,
            )
            try:
                (self.root / "app/build.gradle.kts").write_text(
                    'versionName = "1.1.0"\nversionCode = 8\n// current-source drift\n',
                    encoding="utf-8",
                )
                subprocess.run(
                    ["git", "add", "app/build.gradle.kts"],
                    cwd=self.root,
                    check=True,
                )
                subprocess.run(
                    ["git", "commit", "-q", "-m", "fixture product drift"],
                    cwd=self.root,
                    check=True,
                )
                failures: list[str] = []

                verification = verify_signed_candidate_artifacts(
                    self.root,
                    manifest,
                    failures,
                    artifact_root=self.artifact_root,
                    bundletool_jar=self.bundletool,
                    source_repository_root=old_source,
                    runner=self.runner,
                )
            finally:
                subprocess.run(
                    ["git", "worktree", "remove", "--force", str(old_source)],
                    cwd=self.root,
                    check=True,
                    capture_output=True,
                    text=True,
                )

        self.assertFalse(verification.byte_verified)
        self.assertTrue(
            any("is stale for release source" in failure for failure in failures),
            failures,
        )

    def test_candidate_preflight_rejects_stale_valid_r8_mapping(self) -> None:
        manifest = self.manifest()
        for artifact_id in ("android_phone", "wear_os"):
            self.write_android_bundle(manifest["artifacts"][artifact_id]["filename"])
        mapping_path = self.write_android_mapping(manifest)
        mapping_path.write_text(
            self.android_mapping_text().replace(
                "fixture-map-hash",
                "different-but-well-formed-map-hash",
            ),
            encoding="utf-8",
        )
        self.write_apple_candidate()
        failures: list[str] = []
        apple_certificate = b"fixture-apple-certificate"

        def candidate_runner(
            command: list[str], **kwargs: object
        ) -> subprocess.CompletedProcess:
            executable = Path(command[0]).name
            if executable in {"codesign", "security", "xcrun"} or (
                executable == "openssl" and "-fingerprint" in command
            ):
                return self.apple_runner(
                    command,
                    text=bool(kwargs.get("text", True)),
                    timeout=int(kwargs.get("timeout", 120)),
                    certificate_bytes=apple_certificate,
                )
            return self.runner(
                command,
                text=bool(kwargs.get("text", True)),
                timeout=int(kwargs.get("timeout", 120)),
            )

        with (
            mock.patch(
                "scripts.release_artifact_verifier.BUNDLETOOL_SHA256",
                self.bundletool_sha256,
            ),
            mock.patch(
                "scripts.release_artifact_verifier.ANDROID_UPLOAD_CERTIFICATE_SHA256",
                self.android_certificate_sha256,
            ),
            mock.patch(
                "scripts.release_artifact_verifier.APPLE_DISTRIBUTION_CERTIFICATE_SHA256",
                hashlib.sha256(apple_certificate).hexdigest(),
            ),
            mock.patch(
                "scripts.release_artifact_verifier._required_system_tool",
                side_effect=lambda path, owner, failures: str(path),
            ),
        ):
            verification = verify_signed_candidate_artifacts(
                self.root,
                manifest,
                failures,
                artifact_root=self.artifact_root,
                bundletool_jar=self.bundletool,
                runner=candidate_runner,
            )

        self.assertFalse(verification.byte_verified)
        self.assertTrue(
            any(
                "external mapping differs from phone AAB mapping" in failure
                for failure in failures
            )
        )

    def test_candidate_preflight_rejects_unexpected_root_entry(self) -> None:
        manifest = self.manifest()
        for artifact_id in ("android_phone", "wear_os"):
            self.write_android_bundle(manifest["artifacts"][artifact_id]["filename"])
        self.write_android_mapping(manifest)
        self.write_apple_candidate()
        (self.artifact_root / "unexpected-secret.bin").write_bytes(b"must not upload")
        failures: list[str] = []

        verification = verify_signed_candidate_artifacts(
            self.root,
            manifest,
            failures,
            artifact_root=self.artifact_root,
            bundletool_jar=self.bundletool,
            runner=self.runner,
        )

        self.assertFalse(verification.byte_verified)
        self.assertTrue(
            any(
                "candidate root inventory mismatch" in failure
                and "unexpected-secret.bin" in failure
                for failure in failures
            )
        )

    def test_incomplete_blocked_contract_is_rejected(self) -> None:
        manifest = self.manifest()
        manifest["artifacts"] = {
            artifact_id: {"source_sync": "blocked"}
            for artifact_id in ("android_phone", "wear_os", "apple")
        }
        failures: list[str] = []

        results = verify_manifest_artifacts(self.root, manifest, failures)

        self.assertTrue(failures)
        self.assertTrue(
            all(not result.byte_verified for result in results.values())
        )
        self.assertEqual(
            sum("expected exactly" in failure for failure in failures),
            3,
        )

    def test_stale_manifest_revision_cannot_verify_current_bytes(self) -> None:
        manifest = self.manifest("android_phone")
        path = self.write_android_bundle(
            manifest["artifacts"]["android_phone"]["filename"]
        )
        manifest["artifacts"]["android_phone"]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        (self.root / "app/build.gradle.kts").write_text(
            'versionName = "1.1.0"\nversionCode = 9\n',
            encoding="utf-8",
        )

        results, failures = self.verify_android(manifest)

        self.assertFalse(results["android_phone"].byte_verified)
        self.assertTrue(
            any("is stale for release source" in failure for failure in failures)
        )
        self.assertTrue(
            any("differs from source 9" in failure for failure in failures)
        )

    def test_assume_unchanged_cannot_hide_dirty_release_source(self) -> None:
        subprocess.run(
            ["git", "update-index", "--assume-unchanged", "app/build.gradle.kts"],
            cwd=self.root,
            check=True,
        )
        (self.root / "app/build.gradle.kts").write_text(
            'versionName = "1.1.0"\nversionCode = 9\n',
            encoding="utf-8",
        )
        failures: list[str] = []

        verify_manifest_artifacts(self.root, self.manifest(), failures)

        self.assertTrue(
            any(
                "unsafe release-source index flags" in failure
                and "h:app/build.gradle.kts" in failure
                for failure in failures
            )
        )

    def test_git_stat_cache_cannot_hide_changed_release_bytes(self) -> None:
        path = self.root / "app/build.gradle.kts"
        original_status = path.stat()
        subprocess.run(
            ["git", "config", "core.trustctime", "false"],
            cwd=self.root,
            check=True,
        )
        subprocess.run(
            ["git", "config", "core.checkStat", "minimal"],
            cwd=self.root,
            check=True,
        )
        path.write_text(
            'versionName = "1.1.0"\nversionCode = 9\n',
            encoding="utf-8",
        )
        os.utime(
            path,
            ns=(original_status.st_atime_ns, original_status.st_mtime_ns),
        )
        failures: list[str] = []

        verify_manifest_artifacts(self.root, self.manifest(), failures)

        self.assertTrue(
            any(
                "actual working-tree bytes differ from source_revision" in failure
                and "app/build.gradle.kts" in failure
                for failure in failures
            )
        )

    def test_manifest_release_must_match_current_build_sources(self) -> None:
        manifest = self.manifest()
        manifest["release"] = "1.0.0"
        failures: list[str] = []

        verify_manifest_artifacts(self.root, manifest, failures)

        self.assertEqual(
            sum("source release '1.1.0' differs" in failure for failure in failures),
            3,
        )
        self.assertEqual(
            sum("filename does not match" in failure for failure in failures),
            2,
        )

    def test_fake_digest_without_artifact_bytes_fails_closed(self) -> None:
        manifest = self.manifest()
        self.promote_all(manifest, "a" * 64)
        failures: list[str] = []

        results = verify_manifest_artifacts(self.root, manifest, failures)

        self.assertTrue(all(not result.byte_verified for result in results.values()))
        for artifact_id in ("android_phone", "wear_os", "apple"):
            self.assertIn(
                f"upload manifest artifact {artifact_id}: verified-current requires "
                "real artifact bytes through NIMBO_RELEASE_ARTIFACT_ROOT",
                failures,
            )

    def test_verified_current_cannot_self_certify_all_evidence_with_manifest(
        self,
    ) -> None:
        manifest = self.manifest("android_phone")
        artifact = manifest["artifacts"]["android_phone"]
        artifact["sha256"] = "d" * 64
        manifest_evidence = "store/upload-manifest-1.1.0.json"
        artifact["source_sync_evidence"] = manifest_evidence
        artifact["signing_evidence"] = manifest_evidence
        artifact["physical_qa_evidence"] = manifest_evidence
        manifest_path = self.root / manifest_evidence
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )
        subprocess.run(
            ["git", "add", "--", manifest_evidence],
            cwd=self.root,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-q", "-m", "fixture self-certifying manifest"],
            cwd=self.root,
            check=True,
        )
        failures: list[str] = []

        results = verify_manifest_artifacts(self.root, manifest, failures)

        self.assertFalse(results["android_phone"].byte_verified)
        self.assertIn(
            "upload manifest artifact android_phone: source, signing, and "
            "physical evidence must be separate committed records",
            failures,
        )
        for field in (
            "source_sync_evidence",
            "signing_evidence",
            "physical_qa_evidence",
        ):
            self.assertIn(
                f"upload manifest artifact android_phone.{field} must be a "
                "Markdown record under growth/quality",
                failures,
            )

    def test_verified_current_evidence_aliases_cannot_reuse_one_record(
        self,
    ) -> None:
        manifest = self.manifest("android_phone")
        artifact = manifest["artifacts"]["android_phone"]
        path = self.write_android_bundle(artifact["filename"])
        artifact["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        artifact["source_sync_evidence"] = "growth/quality/alias.md"
        artifact["signing_evidence"] = "growth//quality/alias.md"
        artifact["physical_qa_evidence"] = "growth/quality/./alias.md"
        alias = self.root / "growth/quality/alias.md"
        alias.write_text(
            f"source revision: {self.source_revision}\n"
            f"artifact SHA-256: {artifact['sha256']}\n",
            encoding="utf-8",
        )
        subprocess.run(
            ["git", "add", "--", "growth/quality/alias.md"],
            cwd=self.root,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-q", "-m", "fixture aliased evidence"],
            cwd=self.root,
            check=True,
        )

        with mock.patch.object(self, "write_current_evidence", return_value=None):
            results, failures = self.verify_android(manifest)

        self.assertFalse(results["android_phone"].byte_verified)
        self.assertIn(
            "upload manifest artifact android_phone: source, signing, and "
            "physical evidence must be separate committed records",
            failures,
        )

    def test_artifact_sha_is_recomputed_from_bytes(self) -> None:
        manifest = self.manifest("android_phone")
        path = self.write_android_bundle(manifest["artifacts"]["android_phone"]["filename"])
        manifest["artifacts"]["android_phone"]["sha256"] = "a" * 64

        results, failures = self.verify_android(manifest)

        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertFalse(results["android_phone"].byte_verified)
        self.assertIn(
            f"upload manifest artifact android_phone: artifact SHA-256 {actual} "
            f"differs from manifest {'a' * 64}",
            failures,
        )

    def test_android_phone_happy_path_is_byte_verified(self) -> None:
        manifest = self.manifest("android_phone")
        path = self.write_android_bundle(manifest["artifacts"]["android_phone"]["filename"])
        manifest["artifacts"]["android_phone"]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

        results, failures = self.verify_android(manifest)

        self.assertEqual(failures, [])
        self.assertTrue(results["android_phone"].byte_verified)
        self.assertEqual(
            results["android_phone"].sha256,
            manifest["artifacts"]["android_phone"]["sha256"],
        )

    def test_wear_happy_path_is_byte_verified(self) -> None:
        manifest = self.manifest("wear_os")
        path = self.write_android_bundle(manifest["artifacts"]["wear_os"]["filename"])
        manifest["artifacts"]["wear_os"]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

        results, failures = self.verify_android(manifest)

        self.assertEqual(failures, [])
        self.assertTrue(results["wear_os"].byte_verified)

    def test_wear_watch_feature_must_be_required(self) -> None:
        manifest = self.manifest("wear_os")
        path = self.write_android_bundle(manifest["artifacts"]["wear_os"]["filename"])
        manifest["artifacts"]["wear_os"]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

        results, failures = self.verify_android(manifest, wear_required=False)

        self.assertFalse(results["wear_os"].byte_verified)
        self.assertTrue(
            any("must require android.hardware.type.watch" in item for item in failures)
        )

    def test_apple_happy_path_is_byte_verified(self) -> None:
        manifest = self.manifest("apple")
        path = self.write_apple_candidate()
        manifest["artifacts"]["apple"]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

        results, failures = self.verify_apple(manifest)

        self.assertEqual(failures, [])
        self.assertTrue(results["apple"].byte_verified)
        self.assertEqual(len(results["apple"].details["products"]), 3)
        self.assertEqual(len(results["apple"].details["archive_products"]), 3)
        self.assertEqual(
            {
                product["signer_sha256"]
                for product in results["apple"].details["archive_products"]
            },
            {
                hashlib.sha256(
                    b"fixture-apple-development-certificate"
                ).hexdigest()
            },
        )

    def test_apple_export_options_require_xcode_managed_signing(self) -> None:
        manifest = self.manifest("apple")
        path = self.write_apple_candidate()
        manifest["artifacts"]["apple"]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        export_options_path = self.artifact_root / "ExportOptions.plist"
        export_options = plistlib.loads(export_options_path.read_bytes())
        export_options["signingStyle"] = "manual"
        export_options_path.write_bytes(plistlib.dumps(export_options))

        results, failures = self.verify_apple(manifest)

        self.assertFalse(results["apple"].byte_verified)
        self.assertTrue(
            any(
                "ExportOptions.plist differs from the exact expected contract"
                in failure
                and "differing=['signingStyle']" in failure
                for failure in failures
            )
        )

    def test_apple_export_options_reject_unexpected_key(self) -> None:
        manifest = self.manifest("apple")
        path = self.write_apple_candidate()
        manifest["artifacts"]["apple"]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        export_options_path = self.artifact_root / "ExportOptions.plist"
        export_options = plistlib.loads(export_options_path.read_bytes())
        export_options["thinning"] = "<thin-for-all-variants>"
        export_options_path.write_bytes(plistlib.dumps(export_options))

        results, failures = self.verify_apple(manifest)

        self.assertFalse(results["apple"].byte_verified)
        self.assertTrue(
            any(
                "ExportOptions.plist differs from the exact expected contract"
                in failure
                and "unexpected=['thinning']" in failure
                for failure in failures
            ),
            failures,
        )

    def test_apple_archive_requires_exact_nimbo_app_product(self) -> None:
        manifest = self.manifest("apple")
        path = self.write_apple_candidate(include_archive_app=False)
        manifest["artifacts"]["apple"]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

        results, failures = self.verify_apple(manifest)

        self.assertFalse(results["apple"].byte_verified)
        self.assertTrue(
            any(
                "xcarchive must contain exactly Products/Applications/Nimbo.app"
                in failure
                for failure in failures
            )
        )

    def test_apple_archive_executable_uuid_must_match_exported_ipa(self) -> None:
        manifest = self.manifest("apple")
        path = self.write_apple_candidate()
        manifest["artifacts"]["apple"]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

        results, failures = self.verify_apple(
            manifest,
            archive_uuid_mismatch=True,
        )

        self.assertFalse(results["apple"].byte_verified)
        self.assertTrue(
            any(
                "xcarchive app: executable UUIDs" in failure
                and "differ from exported IPA" in failure
                for failure in failures
            )
        )

    def test_apple_archive_rejects_external_symlink_hops(self) -> None:
        targets = (
            "Products/Applications/Nimbo.app",
            "Products/Applications/Nimbo.app/PlugIns/NimboWidget.appex",
            "Products/Applications/Nimbo.app/Watch/NimboWatch.app",
            "Products/Applications/Nimbo.app/Nimbo",
            "Products/Applications/Nimbo.app/embedded.mobileprovision",
            "dSYMs/Nimbo.app.dSYM",
            "dSYMs/Nimbo.app.dSYM/Contents/Resources/DWARF/Nimbo",
        )
        for index, relative in enumerate(targets):
            with self.subTest(relative=relative):
                if index:
                    shutil.rmtree(self.artifact_root)
                    shutil.rmtree(self.root / "apple-payload")
                    self.artifact_root.mkdir()
                manifest = self.manifest("apple")
                path = self.write_apple_candidate()
                target = self.artifact_root / "Nimbo.xcarchive" / relative
                outside = self.root / f"outside-archive-entry-{index}"
                is_directory = target.is_dir()
                if is_directory:
                    shutil.copytree(target, outside)
                    shutil.rmtree(target)
                else:
                    shutil.copy2(target, outside)
                    target.unlink()
                target.symlink_to(outside, target_is_directory=is_directory)
                manifest["artifacts"]["apple"]["sha256"] = hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()

                results, failures = self.verify_apple(manifest)

                self.assertFalse(results["apple"].byte_verified)
                self.assertTrue(
                    any(
                        "must not traverse a symlink" in failure
                        for failure in failures
                    ),
                    failures,
                )

    def test_apple_missing_signed_source_revision_is_rejected(self) -> None:
        manifest = self.manifest("apple")
        path = self.write_apple_candidate(include_revision=False)
        manifest["artifacts"]["apple"]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

        results, failures = self.verify_apple(manifest)

        self.assertFalse(results["apple"].byte_verified)
        self.assertEqual(
            sum("NimboSourceRevision" in failure for failure in failures),
            6,
        )

    def test_apple_expired_profiles_are_rejected(self) -> None:
        manifest = self.manifest("apple")
        path = self.write_apple_candidate()
        manifest["artifacts"]["apple"]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

        results, failures = self.verify_apple(
            manifest,
            expiration=datetime(2020, 1, 1),
        )

        self.assertFalse(results["apple"].byte_verified)
        self.assertEqual(
            sum("provisioning profile is expired" in failure for failure in failures),
            6,
        )

    def test_embedded_android_revision_must_match_manifest(self) -> None:
        manifest = self.manifest("android_phone")
        path = self.write_android_bundle(
            manifest["artifacts"]["android_phone"]["filename"],
            revision="2" * 40,
        )
        manifest["artifacts"]["android_phone"]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

        results, failures = self.verify_android(manifest)

        self.assertFalse(results["android_phone"].byte_verified)
        self.assertTrue(
            any("embedded VCS revisions" in failure for failure in failures)
        )

    def test_jarsigner_exit_zero_with_unsigned_text_is_rejected(self) -> None:
        manifest = self.manifest("android_phone")
        path = self.write_android_bundle(manifest["artifacts"]["android_phone"]["filename"])
        manifest["artifacts"]["android_phone"]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

        results, failures = self.verify_android(
            manifest,
            jarsigner_output="jar is unsigned.",
        )

        self.assertFalse(results["android_phone"].byte_verified)
        self.assertTrue(
            any("jarsigner did not prove a signed AAB" in failure for failure in failures)
        )

    def test_partially_signed_aab_warning_is_rejected(self) -> None:
        manifest = self.manifest("android_phone")
        path = self.write_android_bundle(manifest["artifacts"]["android_phone"]["filename"])
        manifest["artifacts"]["android_phone"]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

        results, failures = self.verify_android(
            manifest,
            jarsigner_output=(
                "jar verified.\nWarning: This jar contains unsigned entries "
                "which have not been integrity-checked."
            ),
        )

        self.assertFalse(results["android_phone"].byte_verified)
        self.assertTrue(
            any("jarsigner did not prove a signed AAB" in failure for failure in failures)
        )

    def test_android_signer_fingerprint_mismatch_is_rejected(self) -> None:
        manifest = self.manifest("android_phone")
        path = self.write_android_bundle(manifest["artifacts"]["android_phone"]["filename"])
        manifest["artifacts"]["android_phone"]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

        results, failures = self.verify_android(manifest, certificate="f" * 64)

        self.assertFalse(results["android_phone"].byte_verified)
        self.assertTrue(
            any("differs from the pinned Google Play upload certificate" in failure for failure in failures)
        )

    def test_extracted_android_certificate_must_match_pinned_fingerprint(self) -> None:
        manifest = self.manifest("android_phone")
        path = self.write_android_bundle(
            manifest["artifacts"]["android_phone"]["filename"]
        )
        manifest["artifacts"]["android_phone"]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

        results, failures = self.verify_android(
            manifest,
            certificate_der=b"different-extracted-certificate",
        )

        self.assertFalse(results["android_phone"].byte_verified)
        self.assertTrue(
            any(
                "extracted signer certificate SHA-256" in failure
                for failure in failures
            )
        )

    def test_manifest_cannot_repin_verification_identity(self) -> None:
        manifest = self.manifest()
        manifest["verification_policy"]["android_upload_certificate_sha256"] = "f" * 64
        failures: list[str] = []

        verify_manifest_artifacts(self.root, manifest, failures)

        self.assertIn(
            "upload manifest: verification_policy differs from the pinned "
            "release-artifact contract",
            failures,
        )

    def test_wrong_manifest_schema_cannot_return_byte_verified(self) -> None:
        manifest = self.manifest("android_phone")
        path = self.write_android_bundle(manifest["artifacts"]["android_phone"]["filename"])
        manifest["artifacts"]["android_phone"]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        manifest["schema_version"] = 1

        results, failures = self.verify_android(manifest)

        self.assertFalse(results["android_phone"].byte_verified)
        self.assertIn("upload manifest: schema_version must be 2", failures)

    def test_unexpected_android_feature_module_is_rejected(self) -> None:
        manifest = self.manifest("android_phone")
        path = self.write_android_bundle(manifest["artifacts"]["android_phone"]["filename"])
        with zipfile.ZipFile(path, "a") as archive:
            archive.writestr("unexpected_feature/manifest/AndroidManifest.xml", b"module")
        manifest["artifacts"]["android_phone"]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()

        results, failures = self.verify_android(manifest)

        self.assertFalse(results["android_phone"].byte_verified)
        self.assertTrue(
            any("unexpected feature/module roots" in failure for failure in failures)
        )


if __name__ == "__main__":
    unittest.main()
