#!/usr/bin/env python3
"""Bundle notices from an actual Gradle dependency report, never a guessed inventory.

Generate the report using dependencies for app/wear releaseRuntimeClasspath and
shared iosArm64CompileKlibraries, then pass its path as the sole argument.
Network reads retrieve license documents identified by published metadata.
"""
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path.home() / ".gradle/caches/modules-2/files-2.1"
DEST = ROOT / "shared/src/commonMain/composeResources/files/licenses/notices.txt"
NS = {"m": "http://maven.apache.org/POM/4.0.0"}


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Nimbo license bundler"})
    return urllib.request.urlopen(request, timeout=20).read().decode("utf-8")


class DocumentText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag in ("p", "div", "li", "h1", "h2", "h3", "br"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def main():
    report = Path(sys.argv[1]).read_text()
    if "BUILD SUCCESSFUL" not in report:
        raise SystemExit("Refusing an incomplete or failed dependency report")
    coordinates = set()
    for line in report.splitlines():
        if "(c)" in line:
            continue
        match = re.search(r"(?:\\---|\+---) ([\w.-]+):([\w.-]+):(\{[^}]+\}|[^\s]+)(?: -> ([^\s]+))?", line)
        if not match:
            continue
        group, name, version, selected = match.groups()
        if selected:
            if ":" in selected:
                group, name, version = selected.split(":")
            else:
                version = selected
        coordinates.add((group, name, version))
    if not coordinates:
        raise SystemExit("No resolved coordinates in report")
    catalog = (ROOT / "gradle/libs.versions.toml").read_text()
    desugar_version = re.search(r'desugarJdkLibs = "([^"]+)"', catalog).group(1)
    coordinates.add(("com.android.tools", "desugar_jdk_libs", desugar_version))
    if ("org.jetbrains.skiko", "skiko", "0.144.6") not in coordinates:
        raise SystemExit("Refresh the pinned Skiko/Skia upstream notices for the resolved version")
    sections = ["Runtime library licenses\n\nThis bundled inventory covers the resolved Android phone, Wear OS and iOS library graphs. Components listed for another platform may not be included in this installation. SDK terms are identified separately from open-source licenses. Original license documents and available distribution notices follow. Native system frameworks and additional third-party code embedded inside native binaries are not exhaustively described by Maven metadata."]
    license_urls = set()
    original_notices = set()
    for group, name, version in sorted(coordinates):
        directory = CACHE / group / name / version
        poms = list(directory.glob("*/*.pom"))
        if not poms:
            raise SystemExit(f"Missing cached POM: {group}:{name}:{version}")
        root = ET.parse(poms[0]).getroot()
        licenses = root.findall("m:licenses/m:license", NS)
        if not licenses:
            parent = root.find("m:parent", NS)
            if parent is not None:
                values = [parent.findtext("m:" + field, namespaces=NS) for field in ("groupId", "artifactId", "version")]
                parents = list(CACHE.joinpath(*values).glob("*/*.pom"))
                if parents:
                    licenses = ET.parse(parents[0]).getroot().findall("m:licenses/m:license", NS)
        details = []
        for license_node in licenses:
            label = license_node.findtext("m:name", namespaces=NS) or "License"
            url = license_node.findtext("m:url", namespaces=NS)
            details.append(label + ("\n" + url if url else ""))
            if url:
                license_urls.add(url)
        if group == "org.slf4j":
            details = ["MIT License (original notice included below)"]
        if not details:
            details = ["License metadata is not provided by this artifact; inspect original distribution notices below."]
        sections.append(f"{group}:{name}:{version}\n\n" + "\n\n".join(details))
        for archive in directory.glob("*/*"):
            if archive.suffix not in (".jar", ".aar", ".klib") or "sources" in archive.name or "metadata" in archive.name:
                continue
            with zipfile.ZipFile(archive) as content:
                for filename in content.namelist():
                    if re.search(r"(?:^|/)(?:LICENSE|NOTICE|COPYING|COPYRIGHT)(?:[._-].*)?$", filename, re.I):
                        notice = content.read(filename).decode("utf-8", errors="replace").strip()
                        if notice and notice not in original_notices:
                            original_notices.add(notice)
                            sections.append(f"Original notice: {group}:{name}:{version} / {filename}\n\n{notice}")
    documents = {}
    for url in sorted(license_urls):
        if "apache.org/licenses" in url:
            source = "https://www.apache.org/licenses/LICENSE-2.0.txt"
        elif "github.com" in url and "/blob/" in url:
            source = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        else:
            source = url
        if source not in documents:
            document = fetch(source).strip()
            if "<html" in document.lower() or "<!doctype" in document.lower():
                parsed = DocumentText()
                parsed.feed(document)
                document = re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", "".join(parsed.parts)).strip()
            documents[source] = document
    skia_source = "https://raw.githubusercontent.com/JetBrains/skia/m144-22f58c9fd4/LICENSE"
    documents[skia_source] = fetch(skia_source).strip()
    sections.append("Skia m144-22f58c9fd4 (embedded by Skiko 0.144.6 on iOS)\n\nBSD 3-Clause License\nUpstream version evidence: https://github.com/JetBrains/skiko/blob/v0.144.6/skiko/gradle.properties\nLicense source: " + skia_source)
    for name in ("LICENSE", "NOTICE"):
        source = "https://raw.githubusercontent.com/JetBrains/skiko/v0.144.6/" + name
        documents[source] = fetch(source).strip()
    for source, document in documents.items():
        sections.append(f"License document\nSource: {source}\n\n{document}")
    DEST.write_text(("\n\n\f\n\n".join(sections) + "\n").replace("\r\n", "\n"))
    print(f"Bundled {len(coordinates)} resolved components, {len(documents)} license documents, {len(original_notices)} original notices")


if __name__ == "__main__":
    main()
