#!/usr/bin/env python3
"""Build Nimbo's dependency-free, localized GitHub Pages site."""

from __future__ import annotations

import argparse
import html
import json
import os
import shutil
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

try:
    from scripts.check_dashboard_report import verify_dashboard_report
except ModuleNotFoundError:
    from check_dashboard_report import verify_dashboard_report


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "site"
DEFAULT_OUTPUT = REPO_ROOT / "build" / "pages"
LOCALE_ORDER = ("uz", "ru", "en")
PAGE_ORDER = ("landing", "press", "support", "privacy")
PAGE_SLUGS = {"landing": "", "press": "press", "support": "support", "privacy": "privacy"}
CANONICAL_BASE_URL = "https://nimbo.uz"
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
          <div class="device device-ios"><img src="{assets}/screenshots/{locale}-ios.png" alt="Nimbo Weather on iPhone"></div>
          <div class="device device-android"><img src="{assets}/screenshots/{locale}-android.png" alt="Nimbo Weather on Android"></div>
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
              <a class="asset-card" href="{assets}/nimbo-icon.png" download><span class="asset-preview"><img src="{assets}/nimbo-icon.png" alt="Nimbo app icon"></span><span class="asset-label">{escaped(page['download_icon'])} ↓</span></a>
              <a class="asset-card" href="{assets}/screenshots/{locale}-ios.png" download><span class="asset-preview"><img src="{assets}/screenshots/{locale}-ios.png" alt="Nimbo iPhone screenshot"></span><span class="asset-label">{escaped(page['download_ios'])} ↓</span></a>
              <a class="asset-card" href="{assets}/screenshots/{locale}-android.png" download><span class="asset-preview"><img src="{assets}/screenshots/{locale}-android.png" alt="Nimbo Android screenshot"></span><span class="asset-label">{escaped(page['download_android'])} ↓</span></a>
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


def render_body(page_name: str, locale: str, data: dict[str, object], site: dict[str, str], assets: str) -> str:
    if page_name == "landing":
        return landing_body(locale, data, site, assets)
    if page_name == "press":
        return press_body(locale, data, site, assets)
    if page_name == "support":
        return support_body(data, site)
    if page_name == "privacy":
        return privacy_body(data, site)
    raise ValueError(f"Unknown page: {page_name}")


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
    for locale in LOCALE_ORDER:
        locale_data = content["locales"][locale]
        missing_pages = set(PAGE_ORDER) - locale_data.keys()
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
    shutil.copy2(REPO_ROOT / "branding/store/nimbo-app-icon-1024.png", assets / "nimbo-icon.png")
    shutil.copy2(REPO_ROOT / "store/assets/google-play/feature-graphic-1024x500.jpg", assets / "nimbo-feature.jpg")
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
    shutil.copy2(source, target)
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


def build(output: Path, base_url_override: str | None) -> int:
    content = json.loads((SOURCE_ROOT / "content.json").read_text(encoding="utf-8"))
    template = (SOURCE_ROOT / "templates/page.html").read_text(encoding="utf-8")
    validate_content(content)
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
        for page_name in PAGE_ORDER:
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
                for target_page in PAGE_ORDER
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
                for target_page in PAGE_ORDER
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
                "{{CANONICAL_URL}}": escaped(current_url),
                "{{OG_IMAGE_URL}}": escaped(urljoin(f"{base_url}/", "assets/nimbo-feature.jpg")),
                "{{ALTERNATES}}": alternates,
                "{{ASSET_PREFIX}}": assets,
                "{{SKIP_LABEL}}": {"uz": "Asosiy mazmunga o‘tish", "ru": "Перейти к содержанию", "en": "Skip to content"}[locale],
                "{{HOME_URL}}": relative_directory_link(current, destination(output, locale, "landing")),
                "{{NAV_LINKS}}": nav_links,
                "{{LANGUAGE_LABEL}}": escaped(locale_data["common"]["language"]),
                "{{LANGUAGE_LINKS}}": language_links,
                "{{BODY}}": render_body(page_name, locale, locale_data, content["site"], assets),
                "{{WEATHER_DATA}}": escaped(locale_data["common"]["weather_data"]),
                "{{FOOTER_LINKS}}": footer_links,
                "{{NO_TRACKING}}": escaped(locale_data["common"]["no_tracking"]),
            }
            rendered = template
            for placeholder, value in replacements.items():
                rendered = rendered.replace(placeholder, value)
            if "{{" in rendered or "}}" in rendered:
                raise ValueError(f"Unresolved template placeholder in {current.relative_to(output)}")
            current.write_text(rendered.strip() + "\n", encoding="utf-8")

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "".join(f"  <url><loc>{escaped(url)}</loc></url>\n" for url in generated_urls)
    sitemap += "</urlset>\n"
    (output / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (output / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n", encoding="utf-8")
    (output / ".nojekyll").write_text("", encoding="utf-8")

    if has_growth_dashboard:
        generated_urls.append(f"{base_url}/growth/")
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        sitemap += "".join(f"  <url><loc>{escaped(url)}</loc></url>\n" for url in generated_urls)
        sitemap += "</urlset>\n"
        (output / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    expected = len(LOCALE_ORDER) * len(PAGE_ORDER) + int(has_growth_dashboard)
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
    return parser.parse_args()


if __name__ == "__main__":
    try:
        arguments = parse_args()
        sys.exit(build(arguments.output, arguments.base_url))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"site build failed: {error}", file=sys.stderr)
        sys.exit(1)
