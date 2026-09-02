#!/usr/bin/env python3
"""Capture fixed public App Store and Google Play UZ discovery surfaces."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.growth.common import (  # noqa: E402
    GROWTH_ROOT,
    config_fingerprint,
    load_json,
    now_in,
    parse_date,
    write_json,
)


class MonitorError(RuntimeError):
    """Expected source or parser failure."""


class _GooglePlayHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.items: list[dict[str, Any]] = []
        self._index_by_identifier: dict[str, int] = {}
        self._active_identifier: str | None = None
        self._active_anchor_depth = 0

    @staticmethod
    def _package_from_href(href: str) -> str | None:
        parsed = urlparse(href)
        if not parsed.path.endswith("/store/apps/details"):
            return None
        values = parse_qs(parsed.query).get("id", [])
        if not values:
            return None
        package = values[0].strip()
        if not package or "." not in package:
            return None
        return package

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = {key: value for key, value in attrs}
        if tag == "a":
            package = self._package_from_href(attributes.get("href") or "")
            if package is not None:
                self._active_identifier = package
                self._active_anchor_depth = 1
                if package not in self._index_by_identifier:
                    self._index_by_identifier[package] = len(self.items)
                    self.items.append(
                        {"identifier": package, "name": None, "developer": None}
                    )
                return
        if self._active_identifier is not None:
            self._active_anchor_depth += 1
            title = (attributes.get("title") or "").strip()
            if title:
                self._set_name(title)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if self._active_identifier is None:
            return
        attributes = {key: value for key, value in attrs}
        title = (attributes.get("title") or "").strip()
        if title:
            self._set_name(title)

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if self._active_identifier is not None and text:
            self._set_name(text)

    def handle_endtag(self, tag: str) -> None:
        if self._active_identifier is None:
            return
        self._active_anchor_depth -= 1
        if self._active_anchor_depth <= 0 or tag == "a":
            self._active_identifier = None
            self._active_anchor_depth = 0

    def _set_name(self, value: str) -> None:
        if self._active_identifier is None:
            return
        item = self.items[self._index_by_identifier[self._active_identifier]]
        if item["name"] is None:
            item["name"] = value


def _load_json_payload(payload: bytes | str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8")
    loaded = json.loads(payload)
    if not isinstance(loaded, dict):
        raise MonitorError("expected a JSON object")
    return loaded


def parse_apple_chart(payload: bytes | str | dict[str, Any]) -> list[dict[str, Any]]:
    """Parse Apple's legacy public RSS JSON category feed."""

    root = _load_json_payload(payload)
    entries = root.get("feed", {}).get("entry", [])
    if isinstance(entries, dict):
        entries = [entries]
    if not isinstance(entries, list):
        raise MonitorError("Apple chart feed.entry is not a list")

    items: list[dict[str, Any]] = []
    for entry in entries:
        try:
            identifier = str(entry["id"]["attributes"]["im:id"])
            name = str(entry["im:name"]["label"])
        except (KeyError, TypeError) as exc:
            raise MonitorError("Apple chart entry is missing id or name") from exc
        developer = entry.get("im:artist", {}).get("label")
        items.append(
            {
                "identifier": identifier,
                "name": name,
                "developer": str(developer) if developer is not None else None,
            }
        )
    if not items:
        raise MonitorError("Apple chart returned no apps")
    return items


def parse_apple_search(payload: bytes | str | dict[str, Any]) -> list[dict[str, Any]]:
    """Parse Apple's public Search API software results in response order."""

    root = _load_json_payload(payload)
    results = root.get("results", [])
    if not isinstance(results, list):
        raise MonitorError("Apple search results is not a list")
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for result in results:
        if "trackId" not in result:
            continue
        identifier = str(result["trackId"])
        if identifier in seen:
            continue
        seen.add(identifier)
        items.append(
            {
                "identifier": identifier,
                "name": result.get("trackName"),
                "developer": result.get("sellerName") or result.get("artistName"),
            }
        )
    return items


def parse_google_play_html(payload: bytes | str) -> list[dict[str, Any]]:
    """Extract unique Google Play package cards in first-seen HTML order."""

    if isinstance(payload, bytes):
        payload = payload.decode("utf-8", errors="replace")
    parser = _GooglePlayHTMLParser()
    parser.feed(payload)
    parser.close()
    if not parser.items:
        raise MonitorError("Google Play HTML contained no app detail links")
    return parser.items


def _rank_surface(
    *,
    surface_id: str,
    source_url: str,
    fetched_at: str,
    response_sha256: str,
    items: list[dict[str, Any]],
    target_identifier: str,
    capture_limit: int,
    top_slice_size: int,
    minimum_unique_apps: int,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if minimum_unique_apps < 1:
        raise ValueError("minimum_unique_apps must be positive")

    unique_items: list[dict[str, Any]] = []
    seen_identifiers: set[str] = set()
    for item in items:
        identifier = str(item.get("identifier", "")).strip()
        if not identifier or identifier in seen_identifiers:
            continue
        seen_identifiers.add(identifier)
        unique_items.append(item)

    target_rank = next(
        (
            index
            for index, item in enumerate(unique_items, start=1)
            if item["identifier"] == target_identifier
        ),
        None,
    )
    observed = unique_items[:capture_limit]
    target_item = (
        {"rank": target_rank, **unique_items[target_rank - 1]}
        if target_rank is not None
        else None
    )
    unique_observed_count = len(unique_items)
    complete = unique_observed_count >= minimum_unique_apps
    result: dict[str, Any] = {
        "surface_id": surface_id,
        "status": "ok" if complete else "incomplete",
        "source_url": source_url,
        "fetched_at": fetched_at,
        "response_sha256": response_sha256,
        "target_identifier": target_identifier,
        "target_rank": target_rank,
        "target_rank_bound": None
        if target_rank is not None
        else f">{len(unique_items)}",
        "target_item": target_item,
        "raw_observed_count": len(items),
        "observed_count": unique_observed_count,
        "unique_observed_count": unique_observed_count,
        "minimum_unique_apps": minimum_unique_apps,
        "top_items": [
            {"rank": rank, **item}
            for rank, item in enumerate(observed[:top_slice_size], start=1)
        ],
    }
    if not complete:
        result.update(
            {
                "error_type": "InsufficientUniqueApps",
                "error": (
                    f"observed {unique_observed_count} unique apps; "
                    f"at least {minimum_unique_apps} are required"
                ),
            }
        )
    if extra:
        result.update(extra)
    return result


def _error_surface(
    *, surface_id: str, source_url: str, error: Exception, extra: dict[str, Any] | None
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "surface_id": surface_id,
        "status": "error",
        "source_url": source_url,
        "error_type": type(error).__name__,
        "error": str(error)[:500],
    }
    if extra:
        result.update(extra)
    return result


def _fetch(
    url: str,
    *,
    headers: dict[str, str],
    timeout_seconds: int,
    retries: int,
) -> tuple[bytes, str]:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                payload = response.read()
            return payload, hashlib.sha256(payload).hexdigest()
        except (HTTPError, URLError, TimeoutError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(min(2**attempt, 4))
    assert last_error is not None
    raise MonitorError(str(last_error)) from last_error


def _unique_observed_count(surface: dict[str, Any]) -> int:
    explicit = surface.get("unique_observed_count")
    if isinstance(explicit, int) and not isinstance(explicit, bool) and explicit >= 0:
        return explicit
    identifiers = {
        str(item.get("identifier", "")).strip()
        for item in surface.get("top_items", [])
        if isinstance(item, dict) and str(item.get("identifier", "")).strip()
    }
    return len(identifiers)


def _surface_complete(surface: dict[str, Any], minimum_unique_apps: int) -> bool:
    return (
        surface.get("status") == "ok"
        and _unique_observed_count(surface) >= minimum_unique_apps
    )


def _all_surfaces_complete(
    surfaces: Iterable[dict[str, Any]], minimum_unique_apps: int
) -> bool:
    return all(_surface_complete(surface, minimum_unique_apps) for surface in surfaces)


def _minimum_unique_apps(framework: dict[str, Any]) -> int:
    raw = framework["primary_goal"]["daily_requirements"][
        "minimum_unique_observed_apps"
    ]
    if isinstance(raw, bool) or not isinstance(raw, int) or raw < 10:
        raise ValueError(
            "primary_goal.daily_requirements.minimum_unique_observed_apps "
            "must be an integer of at least 10"
        )
    return raw


def _rank_requirement_status(
    surface: dict[str, Any],
    *,
    maximum_rank: int,
    minimum_unique_apps: int,
) -> str:
    """Return pass/fail/unknown for one bounded rank requirement."""

    if not _surface_complete(surface, minimum_unique_apps):
        return "unknown"
    rank = surface.get("target_rank")
    if rank is None:
        return "fail"
    if isinstance(rank, bool) or not isinstance(rank, int) or rank < 1:
        return "unknown"
    return "pass" if rank <= maximum_rank else "fail"


def _conjunction_status(statuses: Iterable[str]) -> str:
    """Combine required conditions without letting unknown hide a proven failure."""

    values = list(statuses)
    if any(status == "fail" for status in values):
        return "fail"
    if values and all(status == "pass" for status in values):
        return "pass"
    return "unknown"


def _monitor_exit_code(snapshot: dict[str, Any]) -> int:
    """Fail observation only when the required daily goal cannot be decided."""

    evaluation = snapshot.get("evaluation")
    status = evaluation.get("status") if isinstance(evaluation, dict) else None
    return 0 if status in {"pass", "fail"} else 1


def _surface_rank(surface: dict[str, Any]) -> int | str:
    rank = surface.get("target_rank")
    if isinstance(rank, int) and not isinstance(rank, bool) and rank >= 1:
        return rank
    bound = surface.get("target_rank_bound")
    return bound if isinstance(bound, str) and bound else "unknown"


def _current_check_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Build a compact, explicitly non-canonical live-check result."""

    apple = snapshot["surfaces"]["apple"]
    google = snapshot["surfaces"]["google"]
    evaluation = snapshot["evaluation"]
    return {
        "schema_version": 1,
        "mode": "check-current",
        "persisted": False,
        "streak_eligible": False,
        "canonical_daily_snapshot_unchanged": True,
        "date": snapshot["date"],
        "captured_at": snapshot["captured_at"],
        "config_fingerprint": snapshot["config_fingerprint"],
        "diagnostic_capture_complete": snapshot["diagnostic_capture_complete"],
        "goal_evidence_complete": snapshot["goal_evidence_complete"],
        "evaluation": evaluation,
        "source_errors": snapshot["source_errors"],
        "ranks": {
            "apple_weather_category": _surface_rank(apple["category"]),
            "apple_search": {
                query_id: _surface_rank(surface)
                for query_id, surface in apple["search"].items()
            },
            "google_weather_category": {
                profile_id: _surface_rank(surface)
                for profile_id, surface in google["category"].items()
            },
            "google_generic_top10_queries": evaluation[
                "google_generic_top10_queries"
            ],
            "google_generic_top10_query_count": evaluation[
                "google_generic_top10_query_count"
            ],
        },
    }


def _intraday_observation_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    payload = dict(snapshot)
    payload["observation"] = {
        "kind": "intraday",
        "streak_eligible": False,
        "canonical_daily_snapshot_unchanged": True,
    }
    return payload


def _intraday_observation_path(root: Path, snapshot: dict[str, Any]) -> Path:
    captured_at = datetime.fromisoformat(str(snapshot["captured_at"]))
    if captured_at.tzinfo is None or captured_at.utcoffset() is None:
        raise ValueError("captured_at must include a UTC offset")
    captured_date = captured_at.date().isoformat()
    if captured_date != snapshot.get("date"):
        raise ValueError("captured_at date does not match snapshot date")
    filename = captured_at.strftime("%H%M%S%z.json")
    return root / captured_date / filename


def _write_json_exclusive(path: Path, payload: Any) -> None:
    """Write one observation without ever replacing an existing path."""

    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
        sort_keys=False,
    ) + "\n"
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def evaluate_day(
    snapshot: dict[str, Any],
    framework: dict[str, Any],
    *,
    expected_query_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    requirements = framework["primary_goal"]["daily_requirements"]
    diagnostics = framework["primary_goal"]["diagnostic_requirements"]
    max_rank = int(requirements["google_weather_category_rank_lte"])
    required_profiles = requirements["google_required_profiles"]
    query_max_rank = int(diagnostics["generic_query_rank_lte"])
    query_quorum = int(diagnostics["generic_query_profile_quorum"])
    query_required = int(diagnostics["generic_queries_required"])
    minimum_unique_apps = _minimum_unique_apps(framework)

    apple_category = snapshot["surfaces"]["apple"]["category"]
    google_categories = snapshot["surfaces"]["google"]["category"]
    google_searches = snapshot["surfaces"]["google"]["search"]

    apple_status = _rank_requirement_status(
        apple_category,
        maximum_rank=int(requirements["apple_weather_chart_rank_lte"]),
        minimum_unique_apps=minimum_unique_apps,
    )
    apple_top10 = apple_status == "pass"

    google_category_by_profile: dict[str, bool] = {}
    google_category_status_by_profile: dict[str, str] = {}
    for profile in required_profiles:
        surface = google_categories[profile]
        profile_status = _rank_requirement_status(
            surface,
            maximum_rank=max_rank,
            minimum_unique_apps=minimum_unique_apps,
        )
        google_category_status_by_profile[profile] = profile_status
        google_category_by_profile[profile] = profile_status == "pass"
    google_category_status = _conjunction_status(
        google_category_status_by_profile.values()
    )
    google_category_top10 = google_category_status == "pass"

    if expected_query_ids is None:
        methodology = snapshot.get("methodology")
        captured_query_ids = (
            methodology.get("fixed_query_ids")
            if isinstance(methodology, dict)
            else None
        )
        if isinstance(captured_query_ids, list):
            expected_query_ids = captured_query_ids
        else:
            # Schema-v1 snapshots predate fixed_query_ids but contain every query
            # under each profile. Keep those snapshots evaluable by inferring the
            # expected set from their captured surfaces.
            expected_query_ids = (
                query_id
                for profile in required_profiles
                for query_id in google_searches.get(profile, {})
            )
    query_ids = sorted(
        {
            query_id
            for query_id in expected_query_ids
            if isinstance(query_id, str) and query_id
        }
    )
    qualifying_queries: list[str] = []
    unresolved_queries: list[str] = []
    rejected_queries: list[str] = []
    query_profile_counts: dict[str, int] = {}
    query_unknown_profile_counts: dict[str, int] = {}
    query_statuses: dict[str, str] = {}
    for query_id in query_ids:
        confirmed_top10 = 0
        unknown_profiles = 0
        for profile in required_profiles:
            surface = google_searches.get(profile, {}).get(query_id, {})
            profile_status = _rank_requirement_status(
                surface,
                maximum_rank=query_max_rank,
                minimum_unique_apps=minimum_unique_apps,
            )
            if profile_status == "unknown":
                unknown_profiles += 1
            elif profile_status == "pass":
                confirmed_top10 += 1
        query_profile_counts[query_id] = confirmed_top10
        query_unknown_profile_counts[query_id] = unknown_profiles
        if confirmed_top10 >= query_quorum:
            query_statuses[query_id] = "pass"
            qualifying_queries.append(query_id)
        elif confirmed_top10 + unknown_profiles < query_quorum:
            query_statuses[query_id] = "fail"
            rejected_queries.append(query_id)
        else:
            query_statuses[query_id] = "unknown"
            unresolved_queries.append(query_id)

    if len(qualifying_queries) >= query_required:
        generic_query_status = "pass"
    elif len(qualifying_queries) + len(unresolved_queries) < query_required:
        generic_query_status = "fail"
    else:
        generic_query_status = "unknown"

    status = _conjunction_status((apple_status, google_category_status))
    complete = status != "unknown"
    requirements_pass = status == "pass"
    reasons: list[str] = []
    if apple_status == "unknown":
        reasons.append("Apple UZ Weather chart evidence is incomplete")
    elif apple_status == "fail":
        reasons.append("Apple UZ Weather chart is not verified in the top 10")
    if google_category_status == "unknown":
        reasons.append("Google UZ Weather category evidence is incomplete")
    elif google_category_status == "fail":
        reasons.append("Google UZ Weather category is not top 10 in all fixed profiles")
    return {
        "status": status,
        "complete": complete,
        "apple_weather_chart_top10": apple_top10,
        "apple_weather_chart_status": apple_status,
        "google_weather_category_top10_all_profiles": google_category_top10,
        "google_weather_category_status": google_category_status,
        "google_category_top10_by_profile": google_category_by_profile,
        "google_category_status_by_profile": google_category_status_by_profile,
        "google_generic_top10_queries": qualifying_queries,
        "google_generic_top10_query_count": len(qualifying_queries),
        "google_generic_query_status": generic_query_status,
        "google_generic_unresolved_queries": unresolved_queries,
        "google_generic_rejected_queries": rejected_queries,
        "google_query_statuses": query_statuses,
        "google_query_top10_profile_counts": query_profile_counts,
        "google_query_unknown_profile_counts": query_unknown_profile_counts,
        "requirements_pass": requirements_pass,
        "reasons": reasons,
    }


def capture(config: dict[str, Any], framework: dict[str, Any]) -> dict[str, Any]:
    timezone_name = config["market"]["timezone"]
    monitor = config["monitor"]
    target_apple = str(config["app"]["apple_id"])
    target_google = config["app"]["android_package"]
    country = config["market"]["country_code"]
    captured_at = now_in(timezone_name)
    capture_limit = int(monitor["google_capture_limit"])
    top_slice_size = int(monitor["top_slice_size"])
    delay = float(monitor["request_delay_seconds"])
    minimum_unique_apps = _minimum_unique_apps(framework)

    def request_surface(
        *,
        surface_id: str,
        url: str,
        parser: Any,
        target: str,
        headers: dict[str, str],
        extra: dict[str, Any] | None = None,
        item_limit: int = capture_limit,
    ) -> dict[str, Any]:
        try:
            payload, response_sha256 = _fetch(
                url,
                headers=headers,
                timeout_seconds=int(monitor["request_timeout_seconds"]),
                retries=int(monitor["request_retries"]),
            )
            items = parser(payload)
            fetched_at = now_in(timezone_name).isoformat(timespec="seconds")
            return _rank_surface(
                surface_id=surface_id,
                source_url=url,
                fetched_at=fetched_at,
                response_sha256=response_sha256,
                items=items,
                target_identifier=target,
                capture_limit=item_limit,
                top_slice_size=top_slice_size,
                minimum_unique_apps=minimum_unique_apps,
                extra=extra,
            )
        except (MonitorError, ValueError, json.JSONDecodeError) as exc:
            return _error_surface(
                surface_id=surface_id, source_url=url, error=exc, extra=extra
            )
        finally:
            if delay > 0:
                time.sleep(delay)

    apple_headers = {"User-Agent": monitor["user_agent"], "Accept": "application/json"}
    google_base_headers = {
        "User-Agent": monitor["google_user_agent"],
        "Accept": "text/html,application/xhtml+xml",
    }

    apple_category = request_surface(
        surface_id="apple.uz.top-free.weather",
        url=config["sources"]["apple_weather_chart"],
        parser=parse_apple_chart,
        target=target_apple,
        headers=apple_headers,
        item_limit=100,
        extra={"rank_kind": "official_apple_hosted_public_chart_order"},
    )

    apple_search: dict[str, Any] = {}
    for query in config["queries"]:
        params = urlencode(
            {
                "term": query["term"],
                "country": country.lower(),
                "media": "software",
                "entity": "software",
                "limit": int(monitor["apple_search_limit"]),
            }
        )
        url = f"{config['sources']['apple_search']}?{params}"
        apple_search[query["id"]] = request_surface(
            surface_id=f"apple.uz.search.{query['id']}",
            url=url,
            parser=parse_apple_search,
            target=target_apple,
            headers=apple_headers,
            item_limit=int(monitor["apple_search_limit"]),
            extra={
                "query_id": query["id"],
                "query": query["term"],
                "rank_kind": "public_search_api_response_order",
            },
        )

    google_category: dict[str, Any] = {}
    google_search: dict[str, dict[str, Any]] = {}
    for profile in config["google_profiles"]:
        profile_id = profile["id"]
        headers = {**google_base_headers, "Accept-Language": profile["accept_language"]}
        category_url = (
            f"{config['sources']['google_category']}?"
            + urlencode({"hl": profile["hl"], "gl": country})
        )
        google_category[profile_id] = request_surface(
            surface_id=f"google.uz.weather.{profile_id}",
            url=category_url,
            parser=parse_google_play_html,
            target=target_google,
            headers=headers,
            extra={
                "profile_id": profile_id,
                "hl": profile["hl"],
                "accept_language": profile["accept_language"],
                "rank_kind": "fixed_logged_out_public_html_first_seen_order",
            },
        )
        google_search[profile_id] = {}
        for query in config["queries"]:
            search_url = (
                f"{config['sources']['google_search']}?"
                + urlencode(
                    {
                        "q": query["term"],
                        "c": "apps",
                        "hl": profile["hl"],
                        "gl": country,
                    }
                )
            )
            google_search[profile_id][query["id"]] = request_surface(
                surface_id=f"google.uz.search.{profile_id}.{query['id']}",
                url=search_url,
                parser=parse_google_play_html,
                target=target_google,
                headers=headers,
                extra={
                    "profile_id": profile_id,
                    "hl": profile["hl"],
                    "accept_language": profile["accept_language"],
                    "query_id": query["id"],
                    "query": query["term"],
                    "rank_kind": "fixed_logged_out_public_html_first_seen_order",
                },
            )

    snapshot: dict[str, Any] = {
        "schema_version": 1,
        "date": captured_at.date().isoformat(),
        "captured_at": captured_at.isoformat(timespec="seconds"),
        "timezone": timezone_name,
        "config_fingerprint": config_fingerprint(config),
        "app": config["app"],
        "market": config["market"],
        "methodology": {
            "authenticated": False,
            "cookie_jar": False,
            "google_country_parameter": country,
            "fixed_google_profiles": [profile["id"] for profile in config["google_profiles"]],
            "fixed_query_ids": [query["id"] for query in config["queries"]],
            "position_semantics": "first unique app identifier in source response order",
            "absence_semantics": "greater than observed_count, not globally unranked",
            "caveats": [
                "Google Play results can still vary by IP, compatibility, experiments, and server-side personalization.",
                "Apple Search API order is a fixed public catalog surface and may differ from device UI.",
                "A source error is unknown and never counts as a passing day."
            ],
        },
        "surfaces": {
            "apple": {"category": apple_category, "search": apple_search},
            "google": {"category": google_category, "search": google_search},
        },
    }
    all_surfaces = [apple_category, *apple_search.values(), *google_category.values()]
    for searches in google_search.values():
        all_surfaces.extend(searches.values())
    snapshot["capture_complete"] = _all_surfaces_complete(
        all_surfaces, minimum_unique_apps
    )
    # Keep the original field as a compatibility alias for schema-v1 consumers.
    # It describes every configured diagnostic surface, not goal decisiveness.
    snapshot["diagnostic_capture_complete"] = snapshot["capture_complete"]
    snapshot["source_errors"] = []
    for surface in all_surfaces:
        if surface.get("status") != "ok":
            snapshot["source_errors"].append(
                {
                    "surface_id": surface["surface_id"],
                    "error_type": surface.get("error_type"),
                    "error": surface.get("error"),
                }
            )
    snapshot["evaluation"] = evaluate_day(
        snapshot,
        framework,
        expected_query_ids=(query["id"] for query in config["queries"]),
    )
    snapshot["goal_evidence_complete"] = snapshot["evaluation"]["complete"]
    return snapshot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", type=Path, default=GROWTH_ROOT / "config.json"
    )
    parser.add_argument(
        "--framework", type=Path, default=GROWTH_ROOT / "kpi-framework.json"
    )
    parser.add_argument("--date", help="Expected local capture date (YYYY-MM-DD)")
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--replace", action="store_true", help="Replace an existing daily snapshot"
    )
    live_mode = parser.add_mutually_exclusive_group()
    live_mode.add_argument(
        "--stdout",
        action="store_true",
        help="Print the full live capture without writing any file",
    )
    live_mode.add_argument(
        "--check-current",
        action="store_true",
        help="Print a compact live check without writing any file",
    )
    live_mode.add_argument(
        "--append-intraday",
        action="store_true",
        help="Append a non-streak intraday observation without changing the daily file",
    )
    parser.add_argument(
        "--intraday-dir",
        type=Path,
        help=(
            "Intraday observation root; defaults to "
            "growth/data/public-rank/intraday"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    live_mode = args.stdout or args.check_current or args.append_intraday
    if live_mode and args.output is not None:
        parser.error("--output cannot be combined with a live observation mode")
    if live_mode and args.replace:
        parser.error("--replace cannot be combined with a live observation mode")
    if args.intraday_dir is not None and not args.append_intraday:
        parser.error("--intraday-dir requires --append-intraday")

    config = load_json(args.config)
    framework = load_json(args.framework)
    local_date = now_in(config["market"]["timezone"]).date().isoformat()
    if args.date is not None:
        expected = parse_date(args.date).isoformat()
        if local_date != expected:
            print(
                f"local date is {local_date}, expected {expected}; refusing mislabeled output",
                file=sys.stderr,
            )
            return 2
    output: Path | None = None
    if not live_mode:
        output = (
            args.output
            or GROWTH_ROOT / "data/public-rank" / f"{local_date}.json"
        )
        if output.exists() and not args.replace:
            print(
                f"snapshot already exists: {output}; pass --replace to overwrite",
                file=sys.stderr,
            )
            return 2

    snapshot = capture(config, framework)
    if snapshot["date"] != local_date:
        print(
            f"capture crossed a local-date boundary ({local_date} -> {snapshot['date']}); "
            "refusing mislabeled output",
            file=sys.stderr,
        )
        return 2

    if args.stdout:
        print(json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=False))
        return _monitor_exit_code(snapshot)
    if args.check_current:
        print(
            json.dumps(
                _current_check_payload(snapshot),
                ensure_ascii=False,
                indent=2,
                sort_keys=False,
            )
        )
        return _monitor_exit_code(snapshot)
    if args.append_intraday:
        intraday_root = (
            args.intraday_dir
            or GROWTH_ROOT / "data/public-rank" / "intraday"
        )
        intraday_path = _intraday_observation_path(intraday_root, snapshot)
        try:
            _write_json_exclusive(
                intraday_path,
                _intraday_observation_payload(snapshot),
            )
        except FileExistsError:
            print(
                f"intraday observation already exists: {intraday_path}; "
                "refusing overwrite",
                file=sys.stderr,
            )
            return 2
        print(
            f"Appended {intraday_path} ({snapshot['evaluation']['status']}; "
            "streak_eligible=false; canonical_daily_snapshot_unchanged=true)."
        )
        return _monitor_exit_code(snapshot)

    assert output is not None
    try:
        if args.replace:
            write_json(output, snapshot)
        else:
            _write_json_exclusive(output, snapshot)
    except FileExistsError:
        print(
            f"snapshot already exists: {output}; pass --replace to overwrite",
            file=sys.stderr,
        )
        return 2
    print(
        f"Wrote {output} ({snapshot['evaluation']['status']}; "
        f"diagnostic_capture_complete={snapshot['diagnostic_capture_complete']}; "
        f"goal_evidence_complete={snapshot['goal_evidence_complete']})."
    )
    return _monitor_exit_code(snapshot)


if __name__ == "__main__":
    raise SystemExit(main())
