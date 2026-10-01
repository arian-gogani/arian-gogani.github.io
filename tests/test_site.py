#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import importlib.util
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Inspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.json_ld = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"] or "")
        if tag == "a" and values.get("href"):
            self.links.append(values["href"] or "")
        if tag == "script" and values.get("type") == "application/ld+json":
            self.json_ld += 1


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    sibling_source = ROOT.parent / "arian-gogani" / "data" / "profile.json"
    source = sibling_source if sibling_source.exists() else ROOT / "data" / "profile.json"
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build.py"), "--source", str(source)], check=True)
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    evidence = (ROOT / "evidence.html").read_text(encoding="utf-8")
    press = (ROOT / "press.html").read_text(encoding="utf-8")
    profile = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))
    parser = Inspector()
    parser.feed(page)
    press_parser = Inspector()
    press_parser.feed(press)

    check("Granite Bay High School" in page, "school missing from portfolio")
    check("<title>Arian Gogani | Granite Bay High School student and Nobulex creator</title>" in page, "search title does not identify the school")
    check("arian-gogani-nobulex" in page, "official LinkedIn missing")
    check("4017b0369" not in page, "old duplicate profile leaked into portfolio")
    check({"main", "top", "work", "architecture", "evidence"} <= parser.ids, "required landmarks missing")
    check(parser.json_ld == 1, "Person JSON-LD missing or duplicated")
    check(profile["metrics"]["nobulex_stars"] == 40, "snapshot does not match measured star count")
    check(profile["metrics"]["nobulex_forks"] == 11, "snapshot does not match measured fork count")
    check("Missing evidence is not approval." in page, "core principle missing")
    check((ROOT / "styles.css").stat().st_size > 5000, "site styling is unexpectedly incomplete")
    check((ROOT / "app.js").stat().st_size > 500, "data-loop client is unexpectedly incomplete")
    check('href="favicon.svg"' in page and (ROOT / "favicon.svg").exists(), "site icon missing")

    spec = importlib.util.spec_from_file_location("portfolio_build", ROOT / "scripts" / "build.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    fallback = module.load("https://127.0.0.1:1/profile.json")
    check(fallback["identity"]["name"] == "Arian Gogani", "remote failure did not use verified snapshot")
    check(evidence.count('class="ledger-record reveal"') == 19, "evidence ledger does not contain 19 records")
    check(
        all('href="styles.css?v=3"' in item for item in (page, evidence, press)),
        "pages do not share the current stylesheet cache key",
    )
    check("Approved by one reviewer; open" in evidence and "/pull/2217" in evidence, "OWASP review win is missing or overstated")
    check(re.search(r'data-category="external" data-search="owasp receipt-guidance', evidence), "reviewer approval is hidden from the External movement filter")
    check("Closed without merge" in evidence, "closed yfinance status was lost")
    check("36 checks with zero failures" in evidence, "fresh Witness Independence result missing")
    check("62 passing tests" in evidence and "12-mutation" in evidence, "fresh DefaultDrift result missing")
    check("decompress_sync" not in evidence, "unpublished aiohttp draft entered public ledger")
    check((ROOT / "evidence.js").stat().st_size > 500, "ledger filtering script is incomplete")
    check("Granite Bay High School" in press, "press page omits the school")
    check("arian-gogani-nobulex" in press, "press page omits the official LinkedIn")
    check("prototype" in press.lower() and "not deployed" in press.lower(), "press page overstates deployment")
    check("Harvard" not in press, "press page contains the false Harvard affiliation")
    check("agentic-skills-top-10/pull/35" in press, "press page omits the OWASP normative change")
    check("agent-governance-vocabulary/pull/161" in press, "press page omits the merged validator fix")
    check("agent-governance-testvectors/pull/24" in press, "press page omits the accepted adversarial tests")
    check("AI-assisted" in press, "press page omits the assistance disclosure")
    check("press.html" in (ROOT / "sitemap.xml").read_text(encoding="utf-8"), "press page missing from sitemap")
    check(press_parser.json_ld == 1, "press ProfilePage JSON-LD missing or duplicated")
    check('href="press.html"' in page, "portfolio does not link to press page")
    check('href="press.html"' in evidence, "evidence ledger does not link to press page")
    check("What the record does not support" in press, "press page omits reporting boundaries")
    check(
        all('document.documentElement.classList.add("js")' in item for item in (page, evidence, press)),
        "pages do not enable reveal animations progressively",
    )
    check(".js .reveal" in (ROOT / "styles.css").read_text(encoding="utf-8"), "content can disappear when JavaScript is unavailable")
    check('"IntersectionObserver" in window' in (ROOT / "app.js").read_text(encoding="utf-8"), "older browsers can leave content hidden")
    print("portfolio checks: 38/38 passed")


if __name__ == "__main__":
    main()
