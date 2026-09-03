#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

usage() {
  cat <<'EOF'
Usage: scripts/local-ci.sh [core|android-ui|apple|full]

  core        Python/repository checks plus Android/shared tests, lint, and bundles
  android-ui  API 24/36 phone and API 36 tablet emulator matrix
  apple       iOS shared/surface tests plus unsigned iOS/watchOS builds
  full        All locally reproducible CI gates (default)
EOF
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Required command is missing: $1" >&2
    exit 69
  fi
}

require_toolchain() {
  require_command java
  require_command python3

  local java_version
  java_version="$(
    java -XshowSettings:properties -version 2>&1 \
      | sed -n 's/^[[:space:]]*java\.specification\.version = //p' \
      | head -1
  )"
  if [[ "$java_version" != "17" ]]; then
    echo "JDK 17 is required for local CI; found ${java_version:-unknown}." >&2
    exit 69
  fi

  python3 - <<'PY'
import sys

if sys.version_info[:2] != (3, 11):
    found = ".".join(str(part) for part in sys.version_info[:3])
    raise SystemExit(f"Python 3.11 is required for local CI; found {found}.")
PY
}

run_core() {
  require_toolchain
  require_command ffmpeg
  require_command ffprobe
  python3 - <<'PY'
import PIL

if PIL.__version__ != "12.2.0":
    raise SystemExit(
        f"Pillow 12.2.0 is required for local CI; found {PIL.__version__}"
    )
PY

  python3 -m compileall -q scripts
  python3 scripts/release_materialization_workflow_security.py
  python3 scripts/trusted_release_workflow_security.py
  python3 -m unittest discover -s scripts/growth/tests -p 'test_*.py'

  python3 scripts/check_repository.py
  python3 scripts/verify_release_artifacts.py --contract-only
  python3 scripts/check_release_qa_matrix.py --contract-only
  python3 scripts/check_localizations.py
  python3 scripts/check_store_metadata.py
  python3 scripts/check_store_assets.py
  python3 scripts/check_store_previews.py
  python3 scripts/check_dashboard_report.py
  python3 scripts/build_site.py --output build/pages-local-ci
  python3 scripts/build_site.py --output build/pages-drafts-local-ci --include-drafts
  git diff --check

  ./gradlew \
    ktlintCheck \
    :shared:allTests \
    :shared:testAndroidHostTest \
    :app:testDebugUnitTest \
    :wearApp:testDebugUnitTest \
    :shared:verifySqlDelightMigration \
    :app:lintRelease \
    :wearApp:lintRelease \
    :app:bundleRelease \
    :wearApp:bundleRelease
}

run_android_ui() {
  require_toolchain
  bash scripts/run_local_android_ui_matrix.sh
}

run_apple() {
  require_toolchain
  require_command xcodebuild
  local source_revision
  source_revision="$(python3 scripts/verify_release_artifacts.py --print-source-revision)"

  ./gradlew :shared:iosSimulatorArm64Test
  bash scripts/test_ios_surfaces.sh
  xcodebuild \
    -project iosApp/Nimbo.xcodeproj \
    -scheme NimboSimulator \
    -configuration Release \
    -sdk iphonesimulator \
    -destination 'generic/platform=iOS Simulator' \
    -derivedDataPath build/xcode-local-ci/ios \
    CODE_SIGNING_ALLOWED=NO \
    ARCHS=arm64 \
    ONLY_ACTIVE_ARCH=YES \
    NIMBO_SOURCE_REVISION="$source_revision" \
    build
  xcodebuild \
    -project iosApp/Nimbo.xcodeproj \
    -scheme NimboWatch \
    -configuration Release \
    -sdk watchsimulator \
    -destination 'generic/platform=watchOS Simulator' \
    -derivedDataPath build/xcode-local-ci/watch \
    CODE_SIGNING_ALLOWED=NO \
    ARCHS=arm64 \
    ONLY_ACTIVE_ARCH=YES \
    NIMBO_SOURCE_REVISION="$source_revision" \
    build
}

mode="${1:-full}"
case "$mode" in
  core)
    run_core
    ;;
  android-ui)
    run_android_ui
    ;;
  apple)
    run_apple
    ;;
  full)
    run_core
    run_android_ui
    run_apple
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    usage >&2
    exit 64
    ;;
esac
