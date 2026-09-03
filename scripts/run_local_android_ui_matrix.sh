#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

sdk_root="${ANDROID_SDK_ROOT:-${ANDROID_HOME:-}}"
if [[ -z "$sdk_root" && -f local.properties ]]; then
  sdk_root="$(sed -n 's/^sdk\.dir=//p' local.properties | head -1)"
fi
if [[ -z "$sdk_root" ]]; then
  echo "Android SDK not found; set ANDROID_SDK_ROOT or sdk.dir in local.properties." >&2
  exit 69
fi

adb_bin="$sdk_root/platform-tools/adb"
emulator_bin="$sdk_root/emulator/emulator"
if [[ ! -x "$adb_bin" || ! -x "$emulator_bin" ]]; then
  echo "Android platform-tools and emulator are required under $sdk_root." >&2
  exit 69
fi
export PATH="$sdk_root/platform-tools:$sdk_root/emulator:$PATH"

avd_home="${ANDROID_AVD_HOME:-$HOME/.android/avd}"
active_serial=""
active_pid=""

cleanup_emulator() {
  if [[ -n "$active_serial" ]]; then
    "$adb_bin" -s "$active_serial" emu kill >/dev/null 2>&1 || true
  fi
  if [[ -n "$active_pid" ]]; then
    wait "$active_pid" 2>/dev/null || true
  fi
  active_serial=""
  active_pid=""
}
trap cleanup_emulator EXIT INT TERM

avd_config() {
  local avd_name="$1"
  local avd_ini="$avd_home/$avd_name.ini"
  local avd_path=""
  if [[ -f "$avd_ini" ]]; then
    avd_path="$(sed -n 's/^path=//p' "$avd_ini" | head -1)"
  fi
  if [[ -z "$avd_path" ]]; then
    avd_path="$avd_home/$avd_name.avd"
  fi
  printf '%s/config.ini\n' "$avd_path"
}

avd_matches() {
  local avd_name="$1"
  local expected_api="$2"
  local form_factor="$3"
  local config
  config="$(avd_config "$avd_name")"
  [[ -f "$config" ]] || return 1
  grep -Eq "^image\.sysdir\.1=.*system-images/android-${expected_api}/" "$config" || return 1

  local identity
  identity="$avd_name $(sed -n 's/^hw\.device\.name=//p' "$config" | head -1)"
  if [[ "$form_factor" == "tablet" ]]; then
    [[ "$identity" =~ [Tt]ablet|7in ]] || return 1
  else
    [[ ! "$identity" =~ [Tt]ablet|7in|[Ww]ear|[Tt][Vv]|[Aa]utomotive ]] || return 1
  fi
}

find_avd() {
  local expected_api="$1"
  local form_factor="$2"
  local avd_name
  while IFS= read -r avd_name; do
    if [[ -n "$avd_name" ]] && avd_matches "$avd_name" "$expected_api" "$form_factor"; then
      printf '%s\n' "$avd_name"
      return 0
    fi
  done < <("$emulator_bin" -list-avds)
  return 1
}

resolve_avd() {
  local configured="$1"
  local expected_api="$2"
  local form_factor="$3"
  local variable_name="$4"
  local result="$configured"
  if [[ -z "$result" ]]; then
    result="$(find_avd "$expected_api" "$form_factor" || true)"
  fi
  if [[ -z "$result" ]]; then
    echo "No local $form_factor API $expected_api AVD found; set $variable_name." >&2
    exit 69
  fi
  if ! avd_matches "$result" "$expected_api" "$form_factor"; then
    echo "$variable_name=$result is not a $form_factor API $expected_api AVD." >&2
    exit 69
  fi
  printf '%s\n' "$result"
}

run_matrix_entry() {
  local matrix_name="$1"
  local expected_api="$2"
  local avd_name="$3"
  local port="$4"
  local serial="emulator-$port"
  local emulator_log="build/android-ui-diagnostics/${matrix_name}-emulator.txt"

  if "$adb_bin" devices | awk 'NR > 1 {print $1}' | grep -qx "$serial"; then
    echo "$serial is already in use; stop it before running the local matrix." >&2
    exit 1
  fi

  mkdir -p build/android-ui-diagnostics
  echo "Starting $matrix_name with AVD $avd_name ($serial)"
  "$emulator_bin" -avd "$avd_name" -port "$port" \
    -no-window -noaudio -no-boot-anim -no-snapshot-load -no-snapshot-save \
    -gpu swiftshader_indirect >"$emulator_log" 2>&1 &
  active_pid="$!"
  active_serial="$serial"

  local deadline=$((SECONDS + 300))
  local boot_completed=""
  while (( SECONDS < deadline )); do
    if ! kill -0 "$active_pid" 2>/dev/null; then
      echo "Emulator $avd_name exited before boot; see $emulator_log." >&2
      exit 1
    fi
    boot_completed="$("$adb_bin" -s "$serial" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r' || true)"
    if [[ "$boot_completed" == "1" ]]; then
      break
    fi
    sleep 2
  done
  if [[ "$boot_completed" != "1" ]]; then
    echo "Emulator $avd_name did not boot within 300 seconds; see $emulator_log." >&2
    exit 1
  fi

  "$adb_bin" -s "$serial" shell settings put global window_animation_scale 0
  "$adb_bin" -s "$serial" shell settings put global transition_animation_scale 0
  "$adb_bin" -s "$serial" shell settings put global animator_duration_scale 0
  ANDROID_SERIAL="$serial" bash scripts/run_android_ui_ci.sh "$matrix_name" "$expected_api"
  cleanup_emulator
}

phone_api24_avd="$(resolve_avd "${NIMBO_AVD_PHONE_API24:-}" 24 phone NIMBO_AVD_PHONE_API24)"
phone_api36_avd="$(resolve_avd "${NIMBO_AVD_PHONE_API36:-}" 36 phone NIMBO_AVD_PHONE_API36)"
tablet_api36_avd="$(resolve_avd "${NIMBO_AVD_TABLET_API36:-}" 36 tablet NIMBO_AVD_TABLET_API36)"

run_matrix_entry phone-api24 24 "$phone_api24_avd" 5580
run_matrix_entry phone-api36 36 "$phone_api36_avd" 5582
run_matrix_entry tablet-api36 36 "$tablet_api36_avd" 5584
