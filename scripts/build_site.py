#!/usr/bin/env python3
"""Build Nimbo's dependency-free, localized GitHub Pages site."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import json
import os
import re
import shutil
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlencode, urljoin, urlparse, urlunparse

try:
    from scripts.check_dashboard_report import verify_dashboard_report
except ModuleNotFoundError:
    from check_dashboard_report import verify_dashboard_report


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "site"
DEFAULT_OUTPUT = REPO_ROOT / "build" / "pages"
LOCALE_ORDER = ("uz", "ru", "en")
BASE_PAGE_ORDER = ("landing", "press", "support", "privacy")
GUIDE_PAGE_ORDER = ("landing", "guides", "press", "support", "privacy")
PAGE_SLUGS = {
    "landing": "",
    "guides": "guides",
    "press": "press",
    "support": "support",
    "privacy": "privacy",
}
CANONICAL_BASE_URL = "https://nimbo.uz"
ARTICLES_SOURCE = REPO_ROOT / "growth/content/articles.json"
CONTENT_CALENDAR_SOURCE = REPO_ROOT / "growth/content/calendar.csv"
QUALITY_GATES_SOURCE = REPO_ROOT / "growth/quality/gates.json"
SITE_ICON_SOURCE = SOURCE_ROOT / "assets/nimbo-icon-site.png"
UNRESOLVED_PLACEHOLDER = re.compile(r"\{\{[A-Z0-9_]+\}\}")
SCREENSHOT_SOURCES = {
    "uz": {
        "ios": REPO_ROOT / "store/screenshots/app-store/iphone-6.9-uz-UZ/01-current.png",
        "android": REPO_ROOT / "store/screenshots/google-play/phone-uz-UZ/01-current.png",
    },
    "ru": {
        "ios": REPO_ROOT / "store/screenshots/app-store/iphone-6.9-ru-RU/01-current.png",
        "android": REPO_ROOT / "store/screenshots/google-play/phone-ru-RU/01-current.png",
    },
    "en": {
        "ios": REPO_ROOT / "store/screenshots/app-store/iphone-6.9-en/01-current.png",
        "android": REPO_ROOT / "store/screenshots/google-play/phone-en/01-current.png",
    },
}
FEATURE_GRAPHIC_SOURCES = {
    "uz": REPO_ROOT / "store/assets/google-play/feature-graphic-uz-UZ-1024x500.jpg",
    "ru": REPO_ROOT / "store/assets/google-play/feature-graphic-ru-RU-1024x500.jpg",
    "en": REPO_ROOT / "store/assets/google-play/feature-graphic-en-US-1024x500.jpg",
}
WATCH_ASSET_SOURCES = {
    "uz": {
        "apple": (
            REPO_ROOT / "store/screenshots/app-store/apple-watch-uz-UZ/01-current.png",
            "nimbo-apple-watch-uz.png",
        ),
        "wear": (
            REPO_ROOT / "store/screenshots/google-play/wear-os-uz-UZ/01-current.png",
            "nimbo-wear-os-uz.png",
        ),
    },
    "ru": {
        "apple": (
            REPO_ROOT / "store/screenshots/app-store/apple-watch-ru-RU/01-current.png",
            "nimbo-apple-watch-ru.png",
        ),
        "wear": (
            REPO_ROOT / "store/screenshots/google-play/wear-os-ru-RU/01-current.png",
            "nimbo-wear-os-ru.png",
        ),
    },
    "en": {
        "apple": (
            REPO_ROOT / "store/screenshots/app-store/apple-watch-en/01-current.jpg",
            "nimbo-apple-watch-en.jpg",
        ),
        "wear": (
            REPO_ROOT / "store/screenshots/google-play/wear-os-en/01-current.jpg",
            "nimbo-wear-os-en.jpg",
        ),
    },
}


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        for key in ("href", "src"):
            value = attributes.get(key)
            if value:
                self.references.append(value)


def escaped(value: object) -> str:
    return html.escape(str(value), quote=True)


def route_parts(locale: str, page: str) -> tuple[str, ...]:
    parts: list[str] = []
    if locale != "uz":
        parts.append(locale)
    slug = PAGE_SLUGS[page]
    if slug:
        parts.append(slug)
    return tuple(parts)


def destination(output: Path, locale: str, page: str) -> Path:
    return output.joinpath(*route_parts(locale, page), "index.html")


def relative_directory_link(current: Path, target: Path) -> str:
    relative = Path(os.path.relpath(target.parent, start=current.parent)).as_posix()
    return "./" if relative == "." else f"{relative}/"


def canonical_url(base_url: str, locale: str, page: str) -> str:
    path = "/".join(route_parts(locale, page))
    return f"{base_url.rstrip('/')}/{path + '/' if path else ''}"


def localized_site(site: dict[str, str], locale: str) -> dict[str, str]:
    """Return locale-correct public destinations without analytics parameters."""
    parsed = urlparse(site["play_store_url"])
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query["hl"] = {"uz": "uz", "ru": "ru", "en": "en"}[locale]
    query["gl"] = "UZ"
    localized = dict(site)
    localized["play_store_url"] = urlunparse(
        parsed._replace(query=urlencode(query))
    )
    return localized


def article_route_parts(locale: str, slug: str) -> tuple[str, ...]:
    parts: list[str] = []
    if locale != "uz":
        parts.append(locale)
    parts.extend(("guides", slug))
    return tuple(parts)


def article_destination(output: Path, locale: str, slug: str) -> Path:
    return output.joinpath(*article_route_parts(locale, slug), "index.html")


def article_canonical_url(base_url: str, locale: str, slug: str) -> str:
    path = "/".join(article_route_parts(locale, slug))
    return f"{base_url.rstrip('/')}/{path}/"


def article_structured_data(
    *,
    base_url: str,
    locale: str,
    article: dict[str, object],
) -> str:
    page = article["locales"][locale]
    url = article_canonical_url(base_url, locale, article["slug"])
    payload: dict[str, object] = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": page["title"],
        "description": page["description"],
        "inLanguage": locale,
        "mainEntityOfPage": url,
        "url": url,
        "image": urljoin(f"{base_url.rstrip('/')}/", f"assets/nimbo-feature-{locale}.jpg"),
        "author": {"@type": "Organization", "name": "Nimbo"},
        "publisher": {
            "@type": "Organization",
            "name": "Nimbo",
            "logo": {
                "@type": "ImageObject",
                "url": urljoin(
                    f"{base_url.rstrip('/')}/", "assets/nimbo-icon-site.png"
                ),
            },
        },
        "citation": article["source_urls"],
    }
    published_on = article.get("published_on")
    if article.get("status") == "published" and isinstance(published_on, str):
        payload["datePublished"] = published_on
        payload["dateModified"] = published_on
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    safe_serialized = serialized.replace("</", "<\\/")
    return f'<script type="application/ld+json">{safe_serialized}</script>'


def landing_structured_data(
    *,
    base_url: str,
    locale: str,
    page: dict[str, object],
    site: dict[str, str],
) -> str:
    """Describe only visible, verified landing-page and application facts."""
    site = localized_site(site, locale)
    current_url = canonical_url(base_url, locale, "landing")
    organization_id = f"{base_url.rstrip('/')}/#organization"
    application: dict[str, object] = {
        "@type": "SoftwareApplication",
        "@id": f"{current_url}#software-application",
        "name": site["name"],
        "alternateName": "Nimbo",
        "url": current_url,
        "description": page["description"],
        "inLanguage": locale,
        "applicationCategory": "UtilitiesApplication",
        "operatingSystem": "Android, iOS, iPadOS, Wear OS, watchOS",
        "image": urljoin(
            f"{base_url.rstrip('/')}/", f"assets/nimbo-feature-{locale}.jpg"
        ),
        "isAccessibleForFree": True,
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD",
        },
        "downloadUrl": [site["app_store_url"], site["play_store_url"]],
        "publisher": {"@id": organization_id},
    }
    organization: dict[str, object] = {
        "@type": "Organization",
        "@id": organization_id,
        "name": site["name"],
        "url": f"{base_url.rstrip('/')}/",
        "logo": urljoin(
            f"{base_url.rstrip('/')}/", "assets/nimbo-icon-site.png"
        ),
        "sameAs": [site["github_url"]],
    }
    graph: list[dict[str, object]] = [organization, application]
    if locale == "uz":
        graph.insert(
            1,
            {
                "@type": "WebSite",
                "@id": f"{base_url.rstrip('/')}/#website",
                "url": f"{base_url.rstrip('/')}/",
                "name": site["name"],
                "alternateName": "Nimbo",
                "inLanguage": list(LOCALE_ORDER),
            },
        )
    payload = {"@context": "https://schema.org", "@graph": graph}
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    safe_serialized = serialized.replace("</", "<\\/")
    return f'<script type="application/ld+json">{safe_serialized}</script>'


def load_quality_gates() -> dict[str, dict[str, object]]:
    try:
        payload = json.loads(QUALITY_GATES_SOURCE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read publication gates: {error}") from error
    gates = payload.get("gates")
    if payload.get("schema_version") != 1 or not isinstance(gates, dict):
        raise ValueError("growth/quality/gates.json must use schema version 1")
    for gate_id, gate in gates.items():
        if (
            not isinstance(gate_id, str)
            or not isinstance(gate, dict)
            or gate.get("status") not in {"pass", "pending", "partial", "blocked"}
            or not isinstance(gate.get("blocks_publication"), bool)
            or not isinstance(gate.get("reason"), str)
            or not gate["reason"].strip()
        ):
            raise ValueError(f"publication gate {gate_id!r} has invalid state")
    return gates


def publication_gate_ids(gates: dict[str, dict[str, object]]) -> set[str]:
    return {
        gate_id
        for gate_id, gate in gates.items()
        if gate["blocks_publication"] is True
    }


def validate_content_calendar(
    articles: list[dict[str, object]],
    gates: dict[str, dict[str, object]],
) -> None:
    with CONTENT_CALENDAR_SOURCE.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    expected_pairs = {
        (article["id"], locale)
        for article in articles
        for locale in LOCALE_ORDER
    }
    actual_pairs = {(row.get("content_id"), row.get("locale")) for row in rows}
    if actual_pairs != expected_pairs or len(rows) != len(expected_pairs):
        raise ValueError("growth/content/calendar.csv must map every article locale once")

    article_by_id = {article["id"]: article for article in articles}
    required_publication_gates = publication_gate_ids(gates)
    if not required_publication_gates:
        raise ValueError("publication gate registry cannot be empty")
    blockers_by_article: dict[str, tuple[str, ...]] = {}
    planned_dates_by_article: dict[str, dt.date] = {}
    for row in rows:
        article = article_by_id[row["content_id"]]
        locale = row["locale"]
        expected_url = article_canonical_url(
            CANONICAL_BASE_URL,
            locale,
            article["slug"],
        )
        if row.get("canonical_url") != expected_url:
            raise ValueError(
                f"calendar {article['id']}.{locale}: canonical URL differs from route"
            )
        if row.get("slug") != article["slug"]:
            raise ValueError(f"calendar {article['id']}.{locale}: slug differs")
        if row.get("title") != article["locales"][locale]["title"]:
            raise ValueError(f"calendar {article['id']}.{locale}: title differs")
        if row.get("status") != article["status"]:
            raise ValueError(f"calendar {article['id']}.{locale}: status differs")
        if row.get("channel") != "site" or row.get("content_type") != "article":
            raise ValueError(f"calendar {article['id']}.{locale}: invalid surface")
        if row.get("source_path") != "growth/content/articles.json":
            raise ValueError(f"calendar {article['id']}.{locale}: invalid source path")
        blockers = tuple(
            blocker.strip()
            for blocker in row.get("blocked_by", "").split("|")
            if blocker.strip()
        )
        if not blockers or len(blockers) != len(set(blockers)):
            raise ValueError(
                f"calendar {article['id']}.{locale}: blocking gates must be unique"
            )
        blocker_set = set(blockers)
        unknown = blocker_set - gates.keys()
        missing = required_publication_gates - blocker_set
        non_publication = blocker_set - required_publication_gates
        if unknown:
            raise ValueError(
                f"calendar {article['id']}.{locale}: unknown blocking gates "
                f"{sorted(unknown)}"
            )
        if missing or non_publication:
            raise ValueError(
                f"calendar {article['id']}.{locale}: publication gate set differs "
                f"(missing={sorted(missing)}, extra={sorted(non_publication)})"
            )
        previous_blockers = blockers_by_article.setdefault(article["id"], blockers)
        if previous_blockers != blockers:
            raise ValueError(
                f"calendar {article['id']}: localized blocking gates differ"
            )
        if article["status"] == "published":
            failing = [
                blocker for blocker in blockers if gates[blocker]["status"] != "pass"
            ]
            if failing:
                raise ValueError(
                    f"article {article['id']}: publication blocked by {failing}"
                )
        try:
            planned_date = dt.date.fromisoformat(row.get("planned_date", ""))
        except (TypeError, ValueError):
            raise ValueError(
                f"calendar {article['id']}.{locale}: planned_date must be ISO"
            ) from None
        if planned_date.strftime("%Y-%m") != article["target_month"]:
            raise ValueError(
                f"calendar {article['id']}.{locale}: planned_date differs from "
                "target_month"
            )
        previous_date = planned_dates_by_article.setdefault(
            article["id"],
            planned_date,
        )
        if previous_date != planned_date:
            raise ValueError(
                f"calendar {article['id']}: localized planned dates differ"
            )


def asset_prefix(output: Path, current: Path) -> str:
    relative = Path(os.path.relpath(output / "assets", start=current.parent)).as_posix()
    return relative.rstrip("/")


def buttons(site: dict[str, str], common: dict[str, str], *, dark: bool = False) -> str:
    secondary = "button-secondary" if not dark else "button-secondary"
    return (
        '<div class="store-actions">'
        f'<a class="button button-primary" href="{escaped(site["app_store_url"])}">'
        f'<span aria-hidden="true">●</span>{escaped(common["app_store"])}</a>'
        f'<a class="button {secondary}" href="{escaped(site["play_store_url"])}">'
        f'<span aria-hidden="true">▶</span>{escaped(common["play_store"])}</a>'
        "</div>"
    )


def landing_body(locale: str, data: dict[str, object], site: dict[str, str], assets: str) -> str:
    page = data["landing"]
    common = data["common"]
    features = "".join(
        '<article class="feature-card">'
        f'<span class="feature-number">{escaped(item["number"])}</span>'
        f'<h3>{escaped(item["title"])}</h3>'
        f'<p>{escaped(item["text"])}</p>'
        "</article>"
        for item in page["features"]
    )
    return f"""
    <section class="hero">
      <div class="shell hero-grid">
        <div class="hero-copy">
          <p class="eyebrow">{escaped(page['eyebrow'])}</p>
          <h1>{escaped(page['headline'])}</h1>
          <p>{escaped(page['lead'])}</p>
          {buttons(site, common)}
          <div class="trust-line">
            <span>{escaped(common['no_tracking'])}</span>
            <span>{escaped(common['available'])}</span>
          </div>
        </div>
        <div class="device-stage" aria-label="{escaped(page['proof'])}">
          <div class="device-halo" aria-hidden="true"></div>
          <div class="device device-ios"><img src="{assets}/screenshots/{locale}-ios.png" alt="{escaped(common['ios_alt'])}" width="1320" height="2868" decoding="async" fetchpriority="high"></div>
          <div class="device device-android"><img src="{assets}/screenshots/{locale}-android.png" alt="{escaped(common['android_alt'])}" width="1080" height="1920" decoding="async"></div>
          <div class="proof-chip">{escaped(page['proof'])}</div>
        </div>
      </div>
    </section>
    <section class="section section-white">
      <div class="shell">
        <div class="section-heading">
          <h2>{escaped(page['features_title'])}</h2>
          <p>{escaped(page['features_intro'])}</p>
        </div>
        <div class="feature-grid">{features}</div>
      </div>
    </section>
    <section class="section">
      <div class="shell split-grid">
        <article class="split-card">
          <span class="icon" aria-hidden="true">○</span>
          <h2>{escaped(page['privacy_title'])}</h2>
          <p>{escaped(page['privacy_text'])}</p>
        </article>
        <article class="split-card">
          <span class="icon" aria-hidden="true">⌘</span>
          <h2>{escaped(page['open_title'])}</h2>
          <p>{escaped(page['open_text'])}</p>
          <a class="button button-link" href="{escaped(site['github_url'])}">{escaped(common['source'])} →</a>
        </article>
      </div>
    </section>
    <section class="section-dark final-cta">
      <div class="shell">
        <h2>{escaped(page['cta_title'])}</h2>
        <p>{escaped(page['cta_text'])}</p>
        {buttons(site, common, dark=True)}
      </div>
    </section>
    """


def page_hero(page: dict[str, object]) -> str:
    return f"""
    <section class="page-hero">
      <div class="shell">
        <p class="eyebrow">{escaped(page['eyebrow'])}</p>
        <h1>{escaped(page['headline'])}</h1>
        <p class="lead">{escaped(page['lead'])}</p>
      </div>
    </section>
    """


def press_body(locale: str, data: dict[str, object], site: dict[str, str], assets: str) -> str:
    page = data["press"]
    apple_watch_asset = WATCH_ASSET_SOURCES[locale]["apple"][1]
    wear_asset = WATCH_ASSET_SOURCES[locale]["wear"][1]
    facts = "".join(f"<li>{escaped(item)}</li>" for item in page["facts"])
    discussions = escaped(site["discussions_url"])
    return page_hero(page) + f"""
    <section class="section section-white">
      <div class="shell content-grid">
        <div class="content-main">
          <section class="content-section"><h2>{escaped(page['facts_title'])}</h2><ul>{facts}</ul></section>
          <section class="content-section">
            <h2>{escaped(page['assets_title'])}</h2><p>{escaped(page['assets_text'])}</p>
            <div class="asset-grid">
              <a class="asset-card" href="{assets}/nimbo-icon.png" download><span class="asset-preview"><img src="{assets}/nimbo-icon.png" alt="{escaped(page['download_icon'])}" loading="lazy" decoding="async"></span><span class="asset-label">{escaped(page['download_icon'])} ↓</span></a>
              <a class="asset-card" href="{assets}/screenshots/{locale}-ios.png" download><span class="asset-preview"><img src="{assets}/screenshots/{locale}-ios.png" alt="{escaped(page['download_ios'])}" loading="lazy" decoding="async"></span><span class="asset-label">{escaped(page['download_ios'])} ↓</span></a>
              <a class="asset-card" href="{assets}/screenshots/{locale}-android.png" download><span class="asset-preview"><img src="{assets}/screenshots/{locale}-android.png" alt="{escaped(page['download_android'])}" loading="lazy" decoding="async"></span><span class="asset-label">{escaped(page['download_android'])} ↓</span></a>
              <a class="asset-card" href="{assets}/nimbo-feature-{locale}.jpg" download><span class="asset-preview"><img src="{assets}/nimbo-feature-{locale}.jpg" alt="{escaped(page['download_feature'])}" loading="lazy" decoding="async"></span><span class="asset-label">{escaped(page['download_feature'])} ↓</span></a>
              <a class="asset-card" href="{assets}/{apple_watch_asset}" download><span class="asset-preview"><img src="{assets}/{apple_watch_asset}" alt="{escaped(page['download_apple_watch'])}" loading="lazy" decoding="async"></span><span class="asset-label">{escaped(page['download_apple_watch'])} ↓</span></a>
              <a class="asset-card" href="{assets}/{wear_asset}" download><span class="asset-preview"><img src="{assets}/{wear_asset}" alt="{escaped(page['download_wear'])}" loading="lazy" decoding="async"></span><span class="asset-label">{escaped(page['download_wear'])} ↓</span></a>
            </div>
            <div class="store-actions">
              <a class="button button-secondary" href="{assets}/nimbo-creative-manifest.json" download>{escaped(page['download_manifest'])}</a>
              <a class="button button-secondary" href="{assets}/nimbo-asset-usage.md" download>{escaped(page['download_usage'])}</a>
            </div>
          </section>
          <section class="content-section"><h2>{escaped(page['boilerplate_title'])}</h2><p class="quote">{escaped(page['boilerplate'])}</p></section>
          <section class="content-section"><h2>{escaped(page['contact_title'])}</h2><p>{escaped(page['contact_text'])}</p><a class="button button-primary" href="{discussions}">GitHub Discussions</a></section>
        </div>
        <aside class="aside-card">
          <h2>Nimbo Weather</h2><p>{escaped(data['common']['no_tracking'])}</p>
          <a class="button button-primary" href="{escaped(site['app_store_url'])}">{escaped(data['common']['app_store'])}</a>
          <a class="button button-secondary" href="{escaped(site['play_store_url'])}">{escaped(data['common']['play_store'])}</a>
        </aside>
      </div>
    </section>
    """


def guides_body(data: dict[str, object], articles: list[dict[str, object]]) -> str:
    page = data["guides"]
    cards = "".join(
        '<article class="guide-card">'
        f'<p class="guide-kicker">{escaped(article["target_month"])}</p>'
        f'<h2>{escaped(article["locales"][data["html_lang"]]["title"])}</h2>'
        f'<p>{escaped(article["locales"][data["html_lang"]]["description"])}</p>'
        + (
            f'<p class="guide-status">{escaped(page["draft_notice"])}</p>'
            if article["status"] != "published"
            else ""
        )
        + f'<a class="button button-link" href="{escaped(article["slug"])}/">'
        f'{escaped(page["read_more"])} →</a>'
        "</article>"
        for article in articles
    )
    return page_hero(page) + f"""
    <section class="section section-white">
      <div class="shell guide-grid">{cards}</div>
    </section>
    """


def article_body(
    locale: str,
    data: dict[str, object],
    article: dict[str, object],
    site: dict[str, str],
) -> str:
    site = localized_site(site, locale)
    page = article["locales"][locale]
    guides = data["guides"]
    sections = "".join(
        f'<section class="content-section"><h2>{escaped(section["title"])}</h2>'
        f'<p>{escaped(section["text"])}</p></section>'
        for section in page["sections"]
    )
    sources = "".join(
        f'<li><a href="{escaped(url)}">{escaped(urlparse(url).netloc)}</a></li>'
        for url in article["source_urls"]
    )
    draft = (
        f'<p class="guide-status">{escaped(guides["draft_notice"])}</p>'
        if article["status"] != "published"
        else ""
    )
    return page_hero(page) + f"""
    <section class="section section-white">
      <div class="shell content-grid">
        <div class="content-main">
          {sections}
          <section class="content-section">
            <h2>{escaped(guides['sources'])}</h2>
            <ul>{sources}</ul>
          </section>
          <section class="content-section">
            <h2>{escaped(page['cta_title'])}</h2>
            <p>{escaped(page['cta_text'])}</p>
            {buttons(site, data['common'])}
          </section>
        </div>
        <aside class="aside-card">
          <a class="button button-link" href="../">← {escaped(guides['back'])}</a>
          <p>{escaped(page['disclaimer'])}</p>
          {draft}
        </aside>
      </div>
    </section>
    """


def support_body(data: dict[str, object], site: dict[str, str]) -> str:
    page = data["support"]
    steps = "".join(f"<li>{escaped(item)}</li>" for item in page["steps"])
    return page_hero(page) + f"""
    <section class="section section-white">
      <div class="shell content-grid">
        <div class="content-main">
          <section class="content-section"><h2>{escaped(page['steps_title'])}</h2><ol>{steps}</ol></section>
          <section class="content-section"><h2>{escaped(page['report_title'])}</h2><p>{escaped(page['report_text'])}</p>
            <div class="store-actions">
              <a class="button button-primary" href="{escaped(site['issues_url'])}">{escaped(page['report_button'])}</a>
              <a class="button button-secondary" href="{escaped(site['discussions_url'])}">{escaped(page['discussion_button'])}</a>
            </div>
          </section>
        </div>
        <aside class="aside-card"><h2>Nimbo Weather</h2><p>{escaped(data['common']['available'])}</p>{buttons(site, data['common'])}</aside>
      </div>
    </section>
    """


def privacy_body(data: dict[str, object], site: dict[str, str]) -> str:
    page = data["privacy"]
    sections = "".join(
        f'<section class="content-section"><h2>{escaped(item["title"])}</h2><p>{escaped(item["text"])}</p></section>'
        for item in page["sections"]
    )
    source_url = f"{site['github_url']}/blob/master/docs/PRIVACY.md"
    security_url = escaped(site["security_url"])
    return page_hero(page) + f"""
    <section class="section section-white">
      <div class="shell content-grid">
        <div class="content-main">{sections}</div>
        <aside class="aside-card">
          <h2>{escaped(page['source_button'])}</h2><p>{escaped(page['source_text'])}</p>
          <a class="button button-primary" href="{escaped(source_url)}">{escaped(page['source_button'])}</a>
          <a class="button button-secondary" href="{security_url}">{escaped(page['private_contact_button'])}</a>
        </aside>
      </div>
    </section>
    """


def render_body(
    page_name: str,
    locale: str,
    data: dict[str, object],
    site: dict[str, str],
    assets: str,
    articles: list[dict[str, object]],
) -> str:
    site = localized_site(site, locale)
    if page_name == "landing":
        return landing_body(locale, data, site, assets)
    if page_name == "press":
        return press_body(locale, data, site, assets)
    if page_name == "guides":
        return guides_body(data, articles)
    if page_name == "support":
        return support_body(data, site)
    if page_name == "privacy":
        return privacy_body(data, site)
    raise ValueError(f"Unknown page: {page_name}")


def load_articles(*, include_drafts: bool) -> list[dict[str, object]]:
    payload = json.loads(ARTICLES_SOURCE.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1 or not isinstance(payload.get("items"), list):
        raise ValueError("growth/content/articles.json must use schema version 1")
    articles = payload["items"]
    ids: set[str] = set()
    slugs: set[str] = set()
    required_localized = {
        "title",
        "description",
        "eyebrow",
        "headline",
        "lead",
        "sections",
        "disclaimer",
        "cta_title",
        "cta_text",
    }
    for article in articles:
        if not isinstance(article, dict):
            raise ValueError("article entries must be objects")
        article_id = article.get("id")
        slug = article.get("slug")
        if not isinstance(article_id, str) or not article_id:
            raise ValueError("article id must be a non-empty string")
        if article_id in ids:
            raise ValueError(f"duplicate article id {article_id!r}")
        ids.add(article_id)
        if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise ValueError(f"article {article_id}: invalid slug")
        if slug in slugs:
            raise ValueError(f"duplicate article slug {slug!r}")
        slugs.add(slug)
        status = article.get("status")
        if status not in {"draft-blocked", "published"}:
            raise ValueError(f"article {article_id}: invalid status")
        published_on = article.get("published_on")
        if status == "published":
            try:
                dt.date.fromisoformat(published_on)
            except (TypeError, ValueError):
                raise ValueError(
                    f"article {article_id}: published article needs an ISO date"
                ) from None
        elif published_on is not None:
            raise ValueError(f"article {article_id}: blocked draft cannot be dated")
        target_month = article.get("target_month")
        if not isinstance(target_month, str) or not re.fullmatch(
            r"\d{4}-(?:0[1-9]|1[0-2])",
            target_month,
        ):
            raise ValueError(f"article {article_id}: target_month must be YYYY-MM")
        sources = article.get("source_urls")
        if not isinstance(sources, list) or not sources:
            raise ValueError(f"article {article_id}: source URLs are required")
        for source in sources:
            parsed = urlparse(source) if isinstance(source, str) else None
            if parsed is None or parsed.scheme != "https" or not parsed.netloc:
                raise ValueError(f"article {article_id}: source must be absolute HTTPS")
        locales = article.get("locales")
        if not isinstance(locales, dict) or set(locales) != set(LOCALE_ORDER):
            raise ValueError(f"article {article_id}: UZ/RU/EN copy is required")
        for locale, localized in locales.items():
            if not isinstance(localized, dict) or set(localized) != required_localized:
                raise ValueError(f"article {article_id}.{locale}: localized schema differs")
            for key in required_localized - {"sections"}:
                if not isinstance(localized[key], str) or not localized[key].strip():
                    raise ValueError(f"article {article_id}.{locale}.{key}: blank value")
            sections = localized["sections"]
            if not isinstance(sections, list) or len(sections) != 4:
                raise ValueError(f"article {article_id}.{locale}: four sections required")
            for section in sections:
                if (
                    not isinstance(section, dict)
                    or set(section) != {"title", "text"}
                    or not all(
                        isinstance(value, str) and value.strip()
                        for value in section.values()
                    )
                ):
                    raise ValueError(f"article {article_id}.{locale}: invalid section")
    validate_content_calendar(articles, load_quality_gates())
    return [
        article
        for article in articles
        if include_drafts or article["status"] == "published"
    ]


def validate_content(content: dict[str, object]) -> None:
    if tuple(content.get("locales", {}).keys()) != LOCALE_ORDER:
        raise ValueError(f"Locales must be ordered exactly as {LOCALE_ORDER}")
    required_site = {"name", "base_url", "app_store_url", "play_store_url", "github_url", "issues_url", "discussions_url", "security_url"}
    missing_site = required_site - content.get("site", {}).keys()
    if missing_site:
        raise ValueError(f"Missing site keys: {sorted(missing_site)}")
    site = content["site"]
    if site["base_url"] != CANONICAL_BASE_URL:
        raise ValueError(
            f"site.base_url must use canonical {CANONICAL_BASE_URL!r}"
        )
    for key in ("base_url", "app_store_url", "play_store_url", "github_url", "issues_url", "discussions_url", "security_url"):
        parsed = urlparse(site[key])
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError(f"site.{key} must be an absolute HTTPS URL")
        lowered = site[key].lower()
        if "utm_" in lowered or "referrer=" in lowered:
            raise ValueError(f"site.{key} must not contain tracking parameters")
    if urlparse(site["app_store_url"]).netloc != "apps.apple.com":
        raise ValueError("site.app_store_url must point to apps.apple.com")
    if urlparse(site["play_store_url"]).netloc != "play.google.com":
        raise ValueError("site.play_store_url must point to play.google.com")
    if not SITE_ICON_SOURCE.is_file() or SITE_ICON_SOURCE.stat().st_size > 64 * 1024:
        raise ValueError("site chrome icon must exist and remain at most 64 KiB")
    for locale in LOCALE_ORDER:
        locale_data = content["locales"][locale]
        missing_pages = set(GUIDE_PAGE_ORDER) - locale_data.keys()
        if missing_pages:
            raise ValueError(f"{locale}: missing pages {sorted(missing_pages)}")
        if len(locale_data["landing"]["features"]) != 6:
            raise ValueError(f"{locale}: landing must contain exactly six benefit stories")
        if len(locale_data["privacy"]["sections"]) != 6:
            raise ValueError(
                f"{locale}: public privacy policy must contain six complete sections"
            )
        for platform, source in SCREENSHOT_SOURCES[locale].items():
            if not source.is_file():
                raise ValueError(f"Missing real {platform} screenshot for {locale}: {source.relative_to(REPO_ROOT)}")
        if not FEATURE_GRAPHIC_SOURCES[locale].is_file():
            raise ValueError(f"Missing localized feature graphic for {locale}")
        for platform, (source, _) in WATCH_ASSET_SOURCES[locale].items():
            if not source.is_file():
                raise ValueError(f"Missing real {platform} watch screenshot for {locale}")


def safe_output(path: Path) -> Path:
    resolved = path.resolve()
    build_root = (REPO_ROOT / "build").resolve()
    if resolved == build_root or build_root not in resolved.parents:
        raise ValueError(f"Output must be a child of {build_root}")
    return resolved


def copy_assets(output: Path) -> None:
    assets = output / "assets"
    screenshots = assets / "screenshots"
    screenshots.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE_ROOT / "assets/site.css", assets / "site.css")
    shutil.copy2(SOURCE_ROOT / "assets/site.js", assets / "site.js")
    shutil.copy2(SITE_ICON_SOURCE, assets / "nimbo-icon-site.png")
    shutil.copy2(REPO_ROOT / "branding/store/nimbo-app-icon-1024.png", assets / "nimbo-icon.png")
    for locale, source in FEATURE_GRAPHIC_SOURCES.items():
        shutil.copy2(source, assets / f"nimbo-feature-{locale}.jpg")
    for platform_sources in WATCH_ASSET_SOURCES.values():
        for source, filename in platform_sources.values():
            shutil.copy2(source, assets / filename)
    shutil.copy2(
        REPO_ROOT / "store/creative-sets/growth-2026-08.json",
        assets / "nimbo-creative-manifest.json",
    )
    shutil.copy2(
        SOURCE_ROOT / "assets/press-asset-usage.md",
        assets / "nimbo-asset-usage.md",
    )
    for locale, sources in SCREENSHOT_SOURCES.items():
        for platform, source in sources.items():
            shutil.copy2(source, screenshots / f"{locale}-{platform}.png")

    schemas = output / "schemas"
    schemas.mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        REPO_ROOT / "store/metadata.schema.json",
        schemas / "store-metadata-v2.json",
    )


def copy_growth_dashboard(output: Path) -> bool:
    source = REPO_ROOT / "growth/dashboard/report.html"
    artifact = REPO_ROOT / "growth/dashboard/artifact.json"
    if not source.exists() and not artifact.exists():
        return False
    if not source.is_file() or not artifact.is_file():
        raise ValueError(
            "growth dashboard requires both artifact.json and report.html"
        )
    verify_dashboard_report(artifact, source)
    target = output / "growth/index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    rendered = source.read_text(encoding="utf-8")
    if "<head>" not in rendered:
        raise ValueError("growth dashboard lacks a head element")
    rendered = rendered.replace(
        "<head>",
        '<head>\n  <meta name="robots" content="noindex,follow">',
        1,
    )
    target.write_text(rendered, encoding="utf-8")
    return True


def validate_generated_site(output: Path) -> None:
    failures: list[str] = []
    output_root = output.resolve()
    for page in sorted(output.glob("**/*.html")):
        collector = LinkCollector()
        collector.feed(page.read_text(encoding="utf-8"))
        for reference in collector.references:
            parsed = urlparse(reference)
            if parsed.scheme or parsed.netloc or reference.startswith("#"):
                continue
            relative_path = unquote(parsed.path)
            if not relative_path:
                continue
            target = (
                output / relative_path.lstrip("/")
                if relative_path.startswith("/")
                else page.parent / relative_path
            ).resolve()
            if target != output_root and output_root not in target.parents:
                failures.append(f"{page.relative_to(output)}: link escapes output: {reference}")
                continue
            if relative_path.endswith("/") or target.is_dir():
                target = target / "index.html"
            if not target.is_file():
                failures.append(
                    f"{page.relative_to(output)}: missing local target {reference}"
                )
    if failures:
        raise ValueError("Generated-site validation failed:\n" + "\n".join(failures))


def build(
    output: Path,
    base_url_override: str | None,
    *,
    include_drafts: bool = False,
) -> int:
    content = json.loads((SOURCE_ROOT / "content.json").read_text(encoding="utf-8"))
    template = (SOURCE_ROOT / "templates/page.html").read_text(encoding="utf-8")
    validate_content(content)
    articles = load_articles(include_drafts=include_drafts)
    page_order = GUIDE_PAGE_ORDER if articles else BASE_PAGE_ORDER
    output = safe_output(output)
    base_url = (base_url_override or content["site"]["base_url"]).rstrip("/")

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    copy_assets(output)
    has_growth_dashboard = copy_growth_dashboard(output)

    generated_urls: list[str] = []
    for locale in LOCALE_ORDER:
        locale_data = content["locales"][locale]
        for page_name in page_order:
            current = destination(output, locale, page_name)
            current.parent.mkdir(parents=True, exist_ok=True)
            assets = asset_prefix(output, current)
            page = locale_data[page_name]
            current_url = canonical_url(base_url, locale, page_name)
            generated_urls.append(current_url)

            nav_links = "".join(
                '<a href="'
                + relative_directory_link(current, destination(output, locale, target_page))
                + '"'
                + (' aria-current="page"' if target_page == page_name else "")
                + ">"
                + escaped(locale_data["nav"]["home" if target_page == "landing" else target_page])
                + "</a>"
                for target_page in page_order
            )
            language_links = "".join(
                '<a href="'
                + relative_directory_link(current, destination(output, target_locale, page_name))
                + '"'
                + (' aria-current="true"' if target_locale == locale else "")
                + ">"
                + escaped(content["locales"][target_locale]["label"])
                + "</a>"
                for target_locale in LOCALE_ORDER
            )
            alternates = "\n  ".join(
                f'<link rel="alternate" hreflang="{target_locale}" href="{escaped(canonical_url(base_url, target_locale, page_name))}">'
                for target_locale in LOCALE_ORDER
            )
            alternates += (
                "\n  "
                f'<link rel="alternate" hreflang="x-default" href="{escaped(canonical_url(base_url, "uz", page_name))}">'
            )
            footer_links = "".join(
                f'<a href="{relative_directory_link(current, destination(output, locale, target_page))}">'
                f'{escaped(locale_data["nav"]["home" if target_page == "landing" else target_page])}</a>'
                for target_page in page_order
            )
            if has_growth_dashboard:
                footer_links += (
                    f'<a href="{relative_directory_link(current, output / "growth/index.html")}">'
                    f'{escaped(locale_data["common"]["growth_dashboard"])}</a>'
                )
            replacements = {
                "{{HTML_LANG}}": escaped(locale_data["html_lang"]),
                "{{TITLE}}": escaped(page["title"]),
                "{{DESCRIPTION}}": escaped(page["description"]),
                "{{OG_TYPE}}": "website",
                "{{ARTICLE_META}}": "",
                "{{CANONICAL_URL}}": escaped(current_url),
                "{{OG_IMAGE_URL}}": escaped(
                    urljoin(f"{base_url}/", f"assets/nimbo-feature-{locale}.jpg")
                ),
                "{{ALTERNATES}}": alternates,
                "{{STRUCTURED_DATA}}": (
                    landing_structured_data(
                        base_url=base_url,
                        locale=locale,
                        page=page,
                        site=content["site"],
                    )
                    if page_name == "landing"
                    else ""
                ),
                "{{ASSET_PREFIX}}": assets,
                "{{SKIP_LABEL}}": {"uz": "Asosiy mazmunga o‘tish", "ru": "Перейти к содержанию", "en": "Skip to content"}[locale],
                "{{HOME_URL}}": relative_directory_link(current, destination(output, locale, "landing")),
                "{{NAV_LINKS}}": nav_links,
                "{{LANGUAGE_LABEL}}": escaped(locale_data["common"]["language"]),
                "{{MENU_LABEL}}": escaped(locale_data["common"]["menu"]),
                "{{PRIMARY_NAV_LABEL}}": escaped(locale_data["common"]["primary_nav"]),
                "{{FOOTER_NAV_LABEL}}": escaped(locale_data["common"]["footer_nav"]),
                "{{LANGUAGE_LINKS}}": language_links,
                "{{BODY}}": render_body(
                    page_name,
                    locale,
                    locale_data,
                    content["site"],
                    assets,
                    articles,
                ),
                "{{WEATHER_DATA}}": escaped(locale_data["common"]["weather_data"]),
                "{{FOOTER_LINKS}}": footer_links,
                "{{NO_TRACKING}}": escaped(locale_data["common"]["no_tracking"]),
            }
            rendered = template
            for placeholder, value in replacements.items():
                rendered = rendered.replace(placeholder, value)
            if UNRESOLVED_PLACEHOLDER.search(rendered):
                raise ValueError(f"Unresolved template placeholder in {current.relative_to(output)}")
            current.write_text(rendered.strip() + "\n", encoding="utf-8")

    for article in articles:
        slug = article["slug"]
        for locale in LOCALE_ORDER:
            locale_data = content["locales"][locale]
            page = article["locales"][locale]
            current = article_destination(output, locale, slug)
            current.parent.mkdir(parents=True, exist_ok=True)
            assets = asset_prefix(output, current)
            current_url = article_canonical_url(base_url, locale, slug)
            generated_urls.append(current_url)
            nav_links = "".join(
                '<a href="'
                + relative_directory_link(
                    current, destination(output, locale, target_page)
                )
                + '"'
                + (' aria-current="page"' if target_page == "guides" else "")
                + ">"
                + escaped(
                    locale_data["nav"][
                        "home" if target_page == "landing" else target_page
                    ]
                )
                + "</a>"
                for target_page in page_order
            )
            language_links = "".join(
                '<a href="'
                + relative_directory_link(
                    current, article_destination(output, target_locale, slug)
                )
                + '"'
                + (' aria-current="true"' if target_locale == locale else "")
                + ">"
                + escaped(content["locales"][target_locale]["label"])
                + "</a>"
                for target_locale in LOCALE_ORDER
            )
            alternates = "\n  ".join(
                f'<link rel="alternate" hreflang="{target_locale}" '
                f'href="{escaped(article_canonical_url(base_url, target_locale, slug))}">'
                for target_locale in LOCALE_ORDER
            )
            alternates += (
                "\n  "
                f'<link rel="alternate" hreflang="x-default" '
                f'href="{escaped(article_canonical_url(base_url, "uz", slug))}">'
            )
            footer_links = "".join(
                f'<a href="{relative_directory_link(current, destination(output, locale, target_page))}">'
                f'{escaped(locale_data["nav"]["home" if target_page == "landing" else target_page])}</a>'
                for target_page in page_order
            )
            if has_growth_dashboard:
                footer_links += (
                    f'<a href="{relative_directory_link(current, output / "growth/index.html")}">'
                    f'{escaped(locale_data["common"]["growth_dashboard"])}</a>'
                )
            replacements = {
                "{{HTML_LANG}}": escaped(locale_data["html_lang"]),
                "{{TITLE}}": escaped(page["title"]),
                "{{DESCRIPTION}}": escaped(page["description"]),
                "{{OG_TYPE}}": "article",
                "{{ARTICLE_META}}": (
                    f'<meta property="article:published_time" content="{escaped(article["published_on"])}">'
                    if article.get("status") == "published"
                    else ""
                ),
                "{{CANONICAL_URL}}": escaped(current_url),
                "{{OG_IMAGE_URL}}": escaped(
                    urljoin(f"{base_url}/", f"assets/nimbo-feature-{locale}.jpg")
                ),
                "{{ALTERNATES}}": alternates,
                "{{STRUCTURED_DATA}}": article_structured_data(
                    base_url=base_url,
                    locale=locale,
                    article=article,
                ),
                "{{ASSET_PREFIX}}": assets,
                "{{SKIP_LABEL}}": {
                    "uz": "Asosiy mazmunga o‘tish",
                    "ru": "Перейти к содержанию",
                    "en": "Skip to content",
                }[locale],
                "{{HOME_URL}}": relative_directory_link(
                    current, destination(output, locale, "landing")
                ),
                "{{NAV_LINKS}}": nav_links,
                "{{LANGUAGE_LABEL}}": escaped(locale_data["common"]["language"]),
                "{{MENU_LABEL}}": escaped(locale_data["common"]["menu"]),
                "{{PRIMARY_NAV_LABEL}}": escaped(
                    locale_data["common"]["primary_nav"]
                ),
                "{{FOOTER_NAV_LABEL}}": escaped(
                    locale_data["common"]["footer_nav"]
                ),
                "{{LANGUAGE_LINKS}}": language_links,
                "{{BODY}}": article_body(
                    locale, locale_data, article, content["site"]
                ),
                "{{WEATHER_DATA}}": escaped(
                    locale_data["common"]["weather_data"]
                ),
                "{{FOOTER_LINKS}}": footer_links,
                "{{NO_TRACKING}}": escaped(locale_data["common"]["no_tracking"]),
            }
            rendered = template
            for placeholder, value in replacements.items():
                rendered = rendered.replace(placeholder, value)
            if UNRESOLVED_PLACEHOLDER.search(rendered):
                raise ValueError(
                    f"Unresolved template placeholder in {current.relative_to(output)}"
                )
            current.write_text(rendered.strip() + "\n", encoding="utf-8")

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "".join(f"  <url><loc>{escaped(url)}</loc></url>\n" for url in generated_urls)
    sitemap += "</urlset>\n"
    (output / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (output / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n", encoding="utf-8")
    (output / ".nojekyll").write_text("", encoding="utf-8")

    expected = (
        len(LOCALE_ORDER) * (len(page_order) + len(articles))
        + int(has_growth_dashboard)
    )
    actual = len(list(output.glob("**/index.html")))
    if actual != expected:
        raise ValueError(f"Expected {expected} HTML pages, generated {actual}")
    validate_generated_site(output)
    print(f"Built {actual} localized pages in {output.relative_to(REPO_ROOT)}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--base-url", help="Canonical base URL (defaults to site/content.json)")
    parser.add_argument(
        "--include-drafts",
        action="store_true",
        help="Render draft-blocked seasonal guides for local QA only",
    )
    return parser.parse_args()


if __name__ == "__main__":
    try:
        arguments = parse_args()
        sys.exit(
            build(
                arguments.output,
                arguments.base_url,
                include_drafts=arguments.include_drafts,
            )
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"site build failed: {error}", file=sys.stderr)
        sys.exit(1)
