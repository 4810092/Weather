#!/usr/bin/env python3
"""Strict, self-contained read-only App Store Connect and Google Play probe.

Only these requests are permitted with --online:
* GET https://api.appstoreconnect.apple.com/v1/apps
* POST https://oauth2.googleapis.com/token (OAuth token exchange)
* GET https://androidpublisher.googleapis.com/.../reviews

The script refuses redirects and every other endpoint or HTTP method. It never
prints credentials, JWTs, OAuth tokens, or provider response bodies.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import stat
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PREFIX = "NIMBO"
APPLE_BUNDLE_ID = "uz.ganikhodjaev.weather"
CENTRAL_APPLE_BUNDLE_IDS = (
    "uz.ganikhodjaev.weather",
    "uz.cooksy.app",
    "uz.ganikhodjaev.steppeloom",
)
GOOGLE_PACKAGE = "uz.ganikhodjaev.weather"
APPLE_ROOT = "https://api.appstoreconnect.apple.com"
GOOGLE_ROOT = "https://androidpublisher.googleapis.com"
OAUTH_URL = "https://oauth2.googleapis.com/token"
GOOGLE_SCOPE = "https://www.googleapis.com/auth/androidpublisher"
MAX_RESPONSE_BYTES = 1024 * 1024
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class ProbeError(RuntimeError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def json_segment(value: dict) -> str:
    return b64url(json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8"))


def secret_bytes(path_name: str, b64_name: str) -> bytes:
    path_value = os.environ.get(path_name, "")
    b64_value = os.environ.get(b64_name, "")
    if bool(path_value) == bool(b64_value):
        raise ProbeError(f"set exactly one of {path_name} or {b64_name}")
    if b64_value:
        try:
            return base64.b64decode("".join(b64_value.split()), validate=True)
        except (ValueError, base64.binascii.Error) as exc:
            raise ProbeError(f"{b64_name} is not valid base64") from exc
    path = Path(path_value).expanduser().resolve()
    if path == REPOSITORY_ROOT or REPOSITORY_ROOT in path.parents:
        raise ProbeError(f"{path_name} must point outside the repository")
    if not path.is_file() or stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise ProbeError(f"{path_name} must be a mode-0600 readable file outside the repository")
    return path.read_bytes()


def command_signature(key: bytes, signing_input: bytes) -> bytes:
    with tempfile.NamedTemporaryFile(prefix="store-readonly-", delete=True) as key_file:
        key_file.write(key)
        key_file.flush()
        try:
            result = subprocess.run(
                ["openssl", "dgst", "-sha256", "-sign", key_file.name],
                input=signing_input,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ProbeError("openssl signing is unavailable") from exc
    if result.returncode != 0 or not result.stdout:
        raise ProbeError("credential private key cannot sign a JWT")
    return result.stdout


def der_es256_to_raw(signature: bytes) -> bytes:
    # ASN.1 DER: SEQUENCE(INTEGER r, INTEGER s); both must fit P-256.
    if len(signature) < 8 or signature[0] != 0x30:
        raise ProbeError("App Store Connect signing did not produce an ES256 signature")
    offset = 2
    if signature[1] & 0x80:
        width = signature[1] & 0x7F
        if width == 0 or width > 2 or len(signature) < 2 + width:
            raise ProbeError("invalid ES256 signature encoding")
        offset = 2 + width
    if signature[offset] != 0x02:
        raise ProbeError("invalid ES256 signature encoding")
    r_len = signature[offset + 1]
    r_start = offset + 2
    s_tag = r_start + r_len
    if s_tag + 2 > len(signature) or signature[s_tag] != 0x02:
        raise ProbeError("invalid ES256 signature encoding")
    s_len = signature[s_tag + 1]
    if s_tag + 2 + s_len != len(signature):
        raise ProbeError("invalid ES256 signature encoding")
    r = signature[r_start:s_tag].lstrip(b"\0")
    s = signature[s_tag + 2:].lstrip(b"\0")
    if not r or not s or len(r) > 32 or len(s) > 32:
        raise ProbeError("invalid ES256 signature length")
    return r.rjust(32, b"\0") + s.rjust(32, b"\0")


def jwt(header: dict, claims: dict, signature: bytes) -> str:
    signing_input = f"{json_segment(header)}.{json_segment(claims)}".encode("ascii")
    return f"{signing_input.decode('ascii')}.{b64url(signature(signing_input))}"


def request_json(method: str, url: str, *, headers: dict | None = None, data: bytes | None = None, apple_bundle_id: str = APPLE_BUNDLE_ID) -> tuple[int, object | None]:
    parsed = urllib.parse.urlparse(url)
    apple_query = urllib.parse.urlencode({"filter[bundleId]": apple_bundle_id})
    reviews_query = "maxResults=1"
    apple_get = method == "GET" and apple_bundle_id in CENTRAL_APPLE_BUNDLE_IDS and parsed.scheme == "https" and parsed.netloc == "api.appstoreconnect.apple.com" and parsed.path == "/v1/apps" and parsed.query == apple_query
    google_get = method == "GET" and parsed.scheme == "https" and parsed.netloc == "androidpublisher.googleapis.com" and parsed.path == f"/androidpublisher/v3/applications/{urllib.parse.quote(GOOGLE_PACKAGE, safe='')}/reviews" and parsed.query == reviews_query
    oauth_post = method == "POST" and url == OAUTH_URL
    if not (apple_get or google_get or oauth_post):
        raise ProbeError("refusing request outside the read-only allowlist")
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "store-readonly-probe", **(headers or {})}, data=data, method=method)
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=20) as response:
            payload = response.read(MAX_RESPONSE_BYTES + 1)
            if len(payload) > MAX_RESPONSE_BYTES:
                raise ProbeError("provider response exceeded the safe size limit")
            try:
                return response.status, json.loads(payload) if payload else None
            except json.JSONDecodeError:
                return response.status, None
    except urllib.error.HTTPError as exc:
        return exc.code, None
    except urllib.error.URLError as exc:
        raise ProbeError("provider endpoint is unavailable without interaction") from exc


def apple_probe(online: bool, apple_bundle_id: str = APPLE_BUNDLE_ID) -> tuple[str, str]:
    if apple_bundle_id not in CENTRAL_APPLE_BUNDLE_IDS:
        return "fail", "Apple bundle ID is outside the central read-only allowlist"
    key_id = os.environ.get(f"{PREFIX}_ASC_KEY_ID", "")
    issuer_id = os.environ.get(f"{PREFIX}_ASC_ISSUER_ID", "")
    if not key_id or not issuer_id:
        return "missing", "App Store Connect key ID or issuer ID is not configured"
    try:
        key = secret_bytes(f"{PREFIX}_ASC_PRIVATE_KEY_PATH", f"{PREFIX}_ASC_PRIVATE_KEY_B64")
        now = int(time.time())
        token = jwt({"alg": "ES256", "kid": key_id, "typ": "JWT"}, {"aud": "appstoreconnect-v1", "exp": now + 600, "iat": now, "iss": issuer_id, "scope": [f"GET /v1/apps?filter[bundleId]={apple_bundle_id}"]}, lambda data: der_es256_to_raw(command_signature(key, data)))
    except ProbeError as exc:
        return "missing", str(exc)
    if not online:
        return "ok", "credential can create a local JWT; network check not requested"
    query = urllib.parse.urlencode({"filter[bundleId]": apple_bundle_id})
    try:
        status, payload = request_json("GET", f"{APPLE_ROOT}/v1/apps?{query}", headers={"Authorization": f"Bearer {token}"}, apple_bundle_id=apple_bundle_id)
    except ProbeError as exc:
        return "fail", str(exc)
    records = payload.get("data") if isinstance(payload, dict) else None
    exact_matches = (
        [
            record
            for record in records
            if isinstance(record, dict)
            and isinstance(record.get("attributes"), dict)
            and record["attributes"].get("bundleId") == apple_bundle_id
        ]
        if isinstance(records, list)
        else []
    )
    if status == 200 and len(exact_matches) == 1:
        return "ok", "authenticated; configured bundle is visible"
    return "fail", "authenticated but exact app is not uniquely visible" if status == 200 else f"read-only app query failed with HTTP {status}"


def google_probe(online: bool) -> tuple[str, str]:
    token_name = f"{PREFIX}_GOOGLE_PLAY_ACCESS_TOKEN"
    direct_token = os.environ.get(token_name, "")
    service_account_names = (
        f"{PREFIX}_GOOGLE_PLAY_SERVICE_ACCOUNT_JSON",
        f"{PREFIX}_GOOGLE_PLAY_SERVICE_ACCOUNT_JSON_B64",
    )
    try:
        if direct_token:
            if any(os.environ.get(name, "") for name in service_account_names):
                raise ProbeError("set either an ephemeral access token or service-account JSON, not both")
            if len(direct_token) < 20:
                raise ProbeError(f"{token_name} is not a valid ephemeral access token")
            assertion = None
        else:
            credential = json.loads(secret_bytes(*service_account_names))
            if not isinstance(credential, dict) or credential.get("type") != "service_account" or credential.get("token_uri") != OAUTH_URL:
                raise ProbeError("credential is not an approved Google service-account JSON object")
            email, key = credential.get("client_email"), credential.get("private_key")
            if not isinstance(email, str) or not email or not isinstance(key, str) or not key:
                raise ProbeError("service-account credential is incomplete")
            now = int(time.time())
            assertion = jwt({"alg": "RS256", "typ": "JWT"}, {"aud": OAUTH_URL, "exp": now + 3600, "iat": now, "iss": email, "scope": GOOGLE_SCOPE}, lambda data: command_signature(key.encode("utf-8"), data))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return "missing", "Google service-account credential is not valid JSON"
    except ProbeError as exc:
        return "missing", str(exc)
    if not online:
        if direct_token:
            return "ok", "ephemeral access token is configured; network check not requested"
        return "ok", "credential can create a local JWT; network check not requested"
    try:
        if direct_token:
            token = direct_token
        else:
            form = urllib.parse.urlencode({"assertion": assertion, "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer"}).encode("ascii")
            status, payload = request_json("POST", OAUTH_URL, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=form)
            token = payload.get("access_token") if status == 200 and isinstance(payload, dict) else None
            if not isinstance(token, str) or not token:
                return "fail", f"Google OAuth token exchange failed with HTTP {status}"
        reviews = f"{GOOGLE_ROOT}/androidpublisher/v3/applications/{urllib.parse.quote(GOOGLE_PACKAGE, safe='')}/reviews?maxResults=1"
        status, _ = request_json("GET", reviews, headers={"Authorization": f"Bearer {token}"})
    except ProbeError as exc:
        return "fail", str(exc)
    return ("ok", "authenticated; configured Play app is visible") if status == 200 else ("fail", f"read-only reviews query failed with HTTP {status}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--online", action="store_true")
    parser.add_argument("--provider", choices=("apple", "google", "both"), default="both")
    parser.add_argument("--apple-bundle-id", choices=CENTRAL_APPLE_BUNDLE_IDS, default=APPLE_BUNDLE_ID)
    args = parser.parse_args()
    checks = []
    if args.provider in ("apple", "both"):
        apple = apple_probe(args.online, args.apple_bundle_id)
        print(f"apple={apple[0]}: {apple[1]}")
        checks.append(apple)
    if args.provider in ("google", "both"):
        google = google_probe(args.online)
        print(f"google={google[0]}: {google[1]}")
        checks.append(google)
    return 0 if all(status == "ok" for status, _ in checks) else 2 if any(status == "missing" for status, _ in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
