#!/usr/bin/env python3
"""Build the portfolio from Arian's canonical GitHub profile data."""

from __future__ import annotations

import argparse
import html
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = "https://raw.githubusercontent.com/arian-gogani/arian-gogani/main/data/profile.json"


def load(source: str) -> dict:
    path = Path(source)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    request = urllib.request.Request(source, headers={"User-Agent": "arian-gogani-portfolio-builder"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)
    except urllib.error.URLError as exc:
        snapshot = ROOT / "data" / "profile.json"
        if not snapshot.exists():
            raise
        print(
            f"canonical profile unavailable ({exc}); using checked-in verified snapshot",
            file=sys.stderr,
        )
        return json.loads(snapshot.read_text(encoding="utf-8"))


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def build(profile: dict) -> str:
    ident = profile["identity"]
    links = profile["links"]
    metrics = profile["metrics"]

    project_cards = "\n".join(
        f'''<article class="project-card reveal">
          <p class="eyebrow">{esc(p['eyebrow'])}</p>
          <h3>{esc(p['name'])}</h3>
          <p>{esc(p['description'])}</p>
          <p class="proof">{esc(p['proof'])}</p>
          <a href="{esc(p['url'])}" rel="me">Inspect the work <span aria-hidden="true">↗</span></a>
        </article>'''
        for p in profile["projects"]
    )
    architecture = "\n".join(
        f'''<li class="architecture-step reveal">
          <span>{esc(a['step'])}</span>
          <div><h3>{esc(a['name'])}</h3><p>{esc(a['description'])}</p></div>
        </li>'''
        for a in profile["architecture"]
    )
    results = "\n".join(
        f'''<li class="result-row reveal">
          <a href="{esc(r['url'])}">{esc(r['label'])} <span aria-hidden="true">↗</span></a>
          <p>{esc(r['detail'])}</p>
        </li>'''
        for r in profile["external_results"]
    )
    search_title = f"{ident['name']} | {ident['school']} student and Nobulex creator"

    json_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": ident["name"],
            "url": links["portfolio"],
            "description": ident["short_bio"],
            "homeLocation": {"@type": "Place", "name": ident["location"]},
            "affiliation": {"@type": "EducationalOrganization", "name": ident["school"]},
            "sameAs": [links["github"], links["linkedin"], links["x"], links["nobulex"]],
            "knowsAbout": [
                "AI decision integrity",
                "software verification",
                "agent security",
                "reproducible research",
            ],
        },
        separators=(",", ":"),
    ).replace("</", "<\\/")

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(search_title)}</title>
  <meta name="description" content="{esc(ident['short_bio'])}">
  <link rel="canonical" href="{esc(links['portfolio'])}/">
  <meta property="og:type" content="profile">
  <meta property="og:title" content="{esc(search_title)}">
  <meta property="og:description" content="{esc(ident['short_bio'])}">
  <meta property="og:url" content="{esc(links['portfolio'])}/">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{esc(search_title)}">
  <meta name="twitter:description" content="{esc(ident['short_bio'])}">
  <meta name="theme-color" content="#07110f">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script>document.documentElement.classList.add("js")</script>
  <link rel="stylesheet" href="styles.css?v=3">
  <script type="application/ld+json">{json_ld}</script>
  <script src="app.js" defer></script>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <div class="ambient" aria-hidden="true"></div>
  <header class="site-header">
    <a class="wordmark" href="#top" aria-label="Arian Gogani, home">AG<span>.</span></a>
    <nav aria-label="Main navigation">
      <a href="#work">Work</a>
      <a href="#architecture">Architecture</a>
      <a href="#evidence">Evidence</a>
      <a href="evidence.html">Full ledger</a>
      <a href="press.html">Press kit</a>
      <a class="nav-cta" href="{esc(links['github'])}">GitHub ↗</a>
    </nav>
  </header>

  <main id="main">
    <section class="hero" id="top">
      <div class="hero-copy reveal">
        <p class="kicker"><span class="status-dot"></span> {esc(ident['school'])} · {esc(ident['location'])}</p>
        <h1>I test what<br><em>“verified”</em><br>actually means.</h1>
        <p class="hero-intro">{esc(ident['bio'])}</p>
        <div class="hero-actions">
          <a class="button primary" href="#work">See the work</a>
          <a class="button secondary" href="{esc(links['linkedin'])}" rel="me">Official LinkedIn ↗</a>
        </div>
      </div>
      <aside class="decision-console reveal" aria-label="Nobulex decision model">
        <div class="console-top"><span></span><span></span><span></span><code>decision.boundary</code></div>
        <div class="console-body">
          <p><span class="muted">action</span> <strong>broker.order.create</strong></p>
          <p><span class="muted">evidence</span> <strong class="warn">INDETERMINATE</strong></p>
          <p><span class="muted">policy</span> <strong>equity-order-v1</strong></p>
          <div class="console-rule"></div>
          <p class="console-result"><span>decision</span><strong>ESCALATE</strong></p>
          <p class="console-note">Missing evidence is not approval.</p>
        </div>
      </aside>
    </section>

    <section class="metrics" aria-label="Measured project metrics">
      <div><strong data-metric="nobulex_stars">{metrics['nobulex_stars']}</strong><span>Nobulex stars</span></div>
      <div><strong data-metric="nobulex_forks">{metrics['nobulex_forks']}</strong><span>Nobulex forks</span></div>
      <div><strong>{metrics['verification_fixtures']}</strong><span>executable fixtures</span></div>
      <div><strong>{metrics['merged_conformance_prs']}</strong><span>merged conformance PRs</span></div>
      <p>GitHub counts measured <time data-measured-at datetime="{metrics['measured_at']}">{metrics['measured_at']}</time>. Every other number links to inspectable work.</p>
    </section>

    <section class="section" id="work">
      <div class="section-heading reveal">
        <p class="eyebrow">Selected work</p>
        <h2>Claims that ship with a way to check them.</h2>
      </div>
      <div class="project-grid">{project_cards}</div>
    </section>

    <section class="section architecture" id="architecture">
      <div class="section-heading reveal">
        <p class="eyebrow">Nobulex architecture</p>
        <h2>Make the decision boundary deterministic.</h2>
        <p>The world can be ambiguous. The system’s response to that ambiguity does not have to be.</p>
      </div>
      <ol>{architecture}</ol>
      <div class="state-pair reveal">
        <div><small>Evidence status</small><strong>PASS · FAIL · INDETERMINATE</strong></div>
        <span aria-hidden="true">→</span>
        <div><small>Execution decision</small><strong>PERMIT · BLOCK · ESCALATE</strong></div>
      </div>
    </section>

    <section class="section evidence" id="evidence">
      <div class="section-heading reveal">
        <p class="eyebrow">External evidence</p>
        <h2>The useful result is what changed outside my repository.</h2>
      </div>
      <ul>{results}</ul>
      <a class="button secondary ledger-button" href="evidence.html">Open all {len(profile['achievements'])} linked records →</a>
    </section>

    <section class="principle reveal">
      <p class="eyebrow">Working standard</p>
      <blockquote>“If I cannot establish it, I should not return a clean result.”</blockquote>
      <p>I publish the command, expected result, and limitation beside each claim. Corrections stay visible.</p>
    </section>
  </main>

  <footer>
    <div>
      <strong>{esc(ident['name'])}</strong>
      <p>{esc(ident['role'])} at {esc(ident['school'])}.</p>
    </div>
    <nav aria-label="Profile links">
      <a href="{esc(links['github'])}" rel="me">GitHub</a>
      <a href="{esc(links['linkedin'])}" rel="me">Official LinkedIn</a>
      <a href="{esc(links['x'])}" rel="me">X</a>
      <a href="{esc(links['nobulex'])}">Nobulex</a>
    </nav>
    <p class="identity-note">Official personal website of Arian Gogani. Canonical public data comes from the GitHub profile repository.</p>
  </footer>
</body>
</html>
'''


def build_evidence(profile: dict) -> str:
    ident = profile["identity"]
    links = profile["links"]
    achievements = sorted(profile["achievements"], key=lambda item: item["rank"])

    cards = []
    for item in achievements:
        category = (
            "external"
            if item["classification"].startswith(("Normative", "Merged", "Closed", "Open reviewed"))
            or "upstream" in item["classification"].lower()
            else "research"
        )
        links_html = "".join(
            f'<a href="{esc(link["url"])}">{esc(link["label"])} ↗</a>' for link in item["links"]
        )
        cards.append(
            f'''<article class="ledger-record reveal" data-category="{category}" data-search="{esc((item['title'] + ' ' + item['classification'] + ' ' + item['summary']).lower())}">
          <div class="ledger-rank">{int(item['rank']):02d}</div>
          <div class="ledger-copy">
            <div class="ledger-meta"><span>{esc(item['classification'])}</span><strong>{esc(item['status'])}</strong></div>
            <h2>{esc(item['title'])}</h2>
            <p>{esc(item['summary'])}</p>
            <div class="ledger-links">{links_html}</div>
            <p class="ledger-caveat"><b>Boundary:</b> {esc(item['caveat'])}</p>
          </div>
        </article>'''
        )

    json_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "Arian Gogani Evidence Ledger",
            "url": f"{links['portfolio']}/evidence.html",
            "description": "Linked public record of Arian Gogani's merged contributions, research, listings, and closed work.",
            "author": {"@type": "Person", "name": ident["name"], "url": links["portfolio"]},
            "mainEntity": [
                {"@type": "CreativeWork", "position": a["rank"], "name": a["title"], "url": a["links"][0]["url"]}
                for a in achievements
            ],
        },
        separators=(",", ":"),
    ).replace("</", "<\\/")

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Evidence Ledger · {esc(ident['name'])}</title>
  <meta name="description" content="Every linked, verified public contribution and research record for {esc(ident['name'])}, with status and limitations.">
  <link rel="canonical" href="{esc(links['portfolio'])}/evidence.html">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Evidence Ledger · {esc(ident['name'])}">
  <meta property="og:description" content="Merged work, public research, listings, and closed contributions. Every record links to its evidence and names its boundary.">
  <meta property="og:url" content="{esc(links['portfolio'])}/evidence.html">
  <meta name="theme-color" content="#07110f">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script>document.documentElement.classList.add("js")</script>
  <link rel="stylesheet" href="styles.css?v=3">
  <script type="application/ld+json">{json_ld}</script>
  <script src="app.js" defer></script>
  <script src="evidence.js" defer></script>
</head>
<body>
  <a class="skip-link" href="#ledger">Skip to ledger</a>
  <div class="ambient" aria-hidden="true"></div>
  <header class="site-header">
    <a class="wordmark" href="index.html" aria-label="Arian Gogani, home">AG<span>.</span></a>
    <nav aria-label="Main navigation">
      <a href="index.html#work">Work</a>
      <a href="index.html#architecture">Architecture</a>
      <a href="press.html">Press kit</a>
      <a class="nav-cta" href="{esc(links['github'])}">GitHub ↗</a>
    </nav>
  </header>

  <main id="ledger">
    <section class="ledger-hero reveal">
      <p class="kicker"><span class="status-dot"></span> Public record · {len(achievements)} linked entries</p>
      <h1>Evidence,<br><em>classified.</em></h1>
      <p class="hero-intro">Every public achievement I can currently substantiate with a link. Normative changes, merged code, references, listings, self-published research, and closed work are labeled differently because they mean different things.</p>
    </section>

    <section class="ledger-controls" aria-label="Filter evidence ledger">
      <label for="ledger-search">Search the ledger</label>
      <input id="ledger-search" type="search" placeholder="Try OWASP, Microsoft, validator…" autocomplete="off">
      <div class="filter-row" role="group" aria-label="Record type">
        <button class="active" type="button" data-filter="all">All <span>{len(achievements)}</span></button>
        <button type="button" data-filter="external">External movement</button>
        <button type="button" data-filter="research">Public research</button>
      </div>
    </section>

    <section class="ledger-list" aria-live="polite">
      {''.join(cards)}
      <p class="ledger-empty" hidden>No linked records match that filter.</p>
    </section>

    <section class="ledger-method reveal">
      <p class="eyebrow">Ranking rule</p>
      <h2>Movement outside my repository ranks first.</h2>
      <p>A change to someone else’s normative text or code outranks a reference. A reference outranks a list. A list outranks a page I wrote about myself. Statuses are rechecked against the linked artifact, so old “open” labels become “merged” or “closed” when reality changes.</p>
      <p>Excluded from this page: private drafts, work with no surviving public artifact, and claims that cannot be linked.</p>
    </section>
  </main>

  <footer>
    <div><strong>{esc(ident['name'])}</strong><p>{esc(ident['role'])} at {esc(ident['school'])}.</p></div>
    <nav aria-label="Profile links"><a href="index.html">Portfolio</a><a href="{esc(links['github'])}">GitHub</a><a href="{esc(links['linkedin'])}" rel="me">Official LinkedIn</a></nav>
    <p class="identity-note">Generated from the same canonical public profile data as the GitHub profile.</p>
  </footer>
</body>
</html>
'''


def build_press(profile: dict) -> str:
    ident = profile["identity"]
    links = profile["links"]
    metrics = profile["metrics"]
    achievements = {item["rank"]: item for item in profile["achievements"]}
    selected = [achievements[rank] for rank in (1, 2, 3, 5, 6, 7)]

    records = []
    for item in selected:
        item_links = "".join(
            f'<a href="{esc(link["url"])}">{esc(link["label"])} ↗</a>'
            for link in item["links"]
        )
        records.append(
            f'''<article class="press-record">
          <div class="ledger-meta"><span>{esc(item['classification'])}</span><strong>{esc(item['status'])}</strong></div>
          <h3>{esc(item['title'])}</h3>
          <p>{esc(item['summary'])}</p>
          <div class="ledger-links">{item_links}</div>
          <p class="ledger-caveat"><b>Boundary:</b> {esc(item['caveat'])}</p>
        </article>'''
        )

    json_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "ProfilePage",
            "name": f"{ident['name']} press and school fact sheet",
            "url": f"{links['portfolio']}/press.html",
            "dateModified": metrics["measured_at"],
            "mainEntity": {
                "@type": "Person",
                "name": ident["name"],
                "description": ident["short_bio"],
                "affiliation": {
                    "@type": "EducationalOrganization",
                    "name": ident["school"],
                },
                "homeLocation": {"@type": "Place", "name": ident["location"]},
                "sameAs": [links["github"], links["linkedin"], links["x"], links["nobulex"]],
            },
        },
        separators=(",", ":"),
    ).replace("</", "<\\/")

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(ident['name'])} Press Kit | {esc(ident['school'])} student</title>
  <meta name="description" content="Verified press and school fact sheet for {esc(ident['name'])}, a {esc(ident['school'])} student and creator of Nobulex.">
  <link rel="canonical" href="{esc(links['portfolio'])}/press.html">
  <meta property="og:type" content="profile">
  <meta property="og:title" content="{esc(ident['name'])} | Press and school fact sheet">
  <meta property="og:description" content="Linked evidence for merged open-source contributions, current project status, and reporting boundaries.">
  <meta property="og:url" content="{esc(links['portfolio'])}/press.html">
  <meta name="theme-color" content="#07110f">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script>document.documentElement.classList.add("js")</script>
  <link rel="stylesheet" href="styles.css?v=3">
  <script type="application/ld+json">{json_ld}</script>
  <script src="app.js" defer></script>
</head>
<body>
  <a class="skip-link" href="#press">Skip to fact sheet</a>
  <div class="ambient" aria-hidden="true"></div>
  <header class="site-header">
    <a class="wordmark" href="index.html" aria-label="{esc(ident['name'])}, home">AG<span>.</span></a>
    <nav aria-label="Main navigation">
      <a href="index.html">Portfolio</a>
      <a href="evidence.html">Evidence ledger</a>
      <a class="nav-cta" href="{esc(links['github'])}">GitHub ↗</a>
    </nav>
  </header>

  <main id="press">
    <section class="press-hero reveal">
      <p class="kicker"><span class="status-dot"></span> Press and school fact sheet · verified {esc(metrics['measured_at'])}</p>
      <h1>A story with<br><em>receipts.</em></h1>
      <p class="hero-intro">{esc(ident['name'])} is a {esc(ident['school'])} student in {esc(ident['location'])} who builds reproducible systems for AI decision integrity and contributes fixes, tests, and technical guidance to open-source projects.</p>
      <div class="hero-actions">
        <a class="button primary" href="#verified">Check the record</a>
        <a class="button secondary" href="{esc(links['linkedin'])}" rel="me">Official LinkedIn ↗</a>
      </div>
    </section>

    <section class="press-summary reveal" aria-label="Short biography">
      <p class="eyebrow">Short biography</p>
      <p>{esc(ident['bio'])}</p>
      <p>His current project, Nobulex, is an open-source prototype. It is implemented and tested locally, but it is not deployed in a customer production path.</p>
    </section>

    <section class="section" id="verified">
      <div class="section-heading reveal">
        <p class="eyebrow">Verified external results</p>
        <h2>Work accepted outside his own repositories.</h2>
        <p>Each item links to the external pull request and preserves the limitation that comes with it.</p>
      </div>
      <div class="press-records">{''.join(records)}</div>
      <a class="button secondary ledger-button" href="evidence.html">Open all {len(profile['achievements'])} classified records →</a>
    </section>

    <section class="section press-facts">
      <div class="section-heading reveal">
        <p class="eyebrow">Measured project facts</p>
        <h2>Numbers with a date and a source.</h2>
      </div>
      <div class="metrics">
        <div><strong>{metrics['nobulex_stars']}</strong><span>Nobulex stars</span></div>
        <div><strong>{metrics['nobulex_forks']}</strong><span>Nobulex forks</span></div>
        <div><strong>{metrics['verification_fixtures']}</strong><span>executable fixtures</span></div>
        <div><strong>5</strong><span>merged shared-test-vector contributions</span></div>
        <p>Repository counts measured {esc(metrics['measured_at'])}. Merge links are listed above and in the evidence ledger.</p>
      </div>
    </section>

    <section class="press-grid">
      <article class="press-note reveal">
        <p class="eyebrow">Accurate framing</p>
        <h2>What the record supports</h2>
        <ul>
          <li>A Granite Bay High School student contributed code, tests, and technical guidance that external maintainers merged.</li>
          <li>The work examines where verification can appear successful while checking less than a reader assumes.</li>
          <li>The public artifacts can be inspected independently.</li>
        </ul>
      </article>
      <article class="press-note caution reveal">
        <p class="eyebrow">Reporting boundary</p>
        <h2>What the record does not support</h2>
        <ul>
          <li>No OWASP, Microsoft, IETF, or maintainer endorsement of Nobulex is claimed.</li>
          <li>No paid customer, production deployment, prevented financial loss, or finished commercial product is claimed.</li>
          <li>Merged documentation and listings are identified separately from merged code.</li>
        </ul>
      </article>
    </section>

    <section class="principle reveal">
      <p class="eyebrow">Authorship disclosure</p>
      <blockquote>AI-assisted work should still be independently checkable.</blockquote>
      <p>The work and this fact sheet were AI-assisted. Public contribution records identify the human author, external reviewer, status, and exact diff. Interview Arian about the experiments, decisions, corrections, and limitations he can personally explain.</p>
    </section>
  </main>

  <footer>
    <div><strong>{esc(ident['name'])}</strong><p>{esc(ident['role'])} at {esc(ident['school'])}.</p></div>
    <nav aria-label="Official links"><a href="index.html">Portfolio</a><a href="{esc(links['github'])}" rel="me">GitHub</a><a href="{esc(links['linkedin'])}" rel="me">Official LinkedIn</a></nav>
    <p class="identity-note">Official fact sheet generated from the same canonical public profile data as the portfolio and GitHub profile.</p>
  </footer>
</body>
</html>
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=DEFAULT_SOURCE)
    args = parser.parse_args()
    profile = load(args.source)
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "profile.json").write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    (ROOT / "index.html").write_text(build(profile), encoding="utf-8")
    (ROOT / "evidence.html").write_text(build_evidence(profile), encoding="utf-8")
    (ROOT / "press.html").write_text(build_press(profile), encoding="utf-8")


if __name__ == "__main__":
    main()
