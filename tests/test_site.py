#!/usr/bin/env python3

from __future__ import annotations

import json
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
    source = ROOT.parent / "arian-gogani" / "data" / "profile.json"
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build.py"), "--source", str(source)], check=True)
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    profile = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))
    parser = Inspector()
    parser.feed(page)

    check("Granite Bay High School" in page, "school missing from portfolio")
    check("arian-gogani-nobulex" in page, "official LinkedIn missing")
    check("4017b0369" not in page, "old duplicate profile leaked into portfolio")
    check({"main", "top", "work", "architecture", "evidence"} <= parser.ids, "required landmarks missing")
    check(parser.json_ld == 1, "Person JSON-LD missing or duplicated")
    check(profile["metrics"]["nobulex_stars"] == 40, "snapshot does not match measured star count")
    check(profile["metrics"]["nobulex_forks"] == 11, "snapshot does not match measured fork count")
    check("Missing evidence is not approval." in page, "core principle missing")
    check((ROOT / "styles.css").stat().st_size > 5000, "site styling is unexpectedly incomplete")
    check((ROOT / "app.js").stat().st_size > 500, "data-loop client is unexpectedly incomplete")

    spec = importlib.util.spec_from_file_location("portfolio_build", ROOT / "scripts" / "build.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    fallback = module.load("https://127.0.0.1:1/profile.json")
    check(fallback["identity"]["name"] == "Arian Gogani", "remote failure did not use verified snapshot")
    print("portfolio checks: 11/11 passed")


if __name__ == "__main__":
    main()
