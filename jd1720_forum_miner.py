#!/usr/bin/env python3
"""
JD 1720 Forum Miner
- Fetch forum threads
- Extract text + detect issue keywords and part mentions
- Output per-thread CSV + aggregated frequency CSV

NOTE:
- Respect robots.txt and each site's Terms. Keep requests low-rate.
- Some forums require login; those pages will return little/blocked content.
"""

import argparse
import os
import re
import time
import csv
import json
import math
from dataclasses import dataclass
from collections import Counter, defaultdict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


# -------------------------
# Config
# -------------------------

USER_AGENT = "Mozilla/5.0 (compatible; JD1720ForumMiner/1.0; +https://example.invalid)"
REQUEST_TIMEOUT_S = 20
SLEEP_BETWEEN_REQ_S = 2.0

# Issue keywords: tweak for your wording / local slang
ISSUE_PATTERNS = [
    r"\b(start(s|ed)? and stop(s|ped)?)\b",
    r"\b(intermittent|sporadic|cuts? out|drop(s|ped)? out)\b",
    r"\b(plug(s|ged)?|block(s|ed)?|bridg(e|ing))\b",
    r"\b(skips?|missing|mis[- ]?singulation|double(s|d)?)\b",
    r"\b(low vacuum|vacuum leak|air leak|loss of vacuum)\b",
    r"\b(hydraulic drive|drive motor|hyd motor)\b",
    r"\b(voltage|low voltage|no power|short|open circuit|bad ground)\b",
    r"\b(sensor(s)?|seed sensor|ground speed|radar)\b",
    r"\b(bearing(s)?|worn|wear)\b",
    r"\b(chain(s)?|sprocket(s)?|idler)\b",
    r"\b(depth|too deep|too shallow|depth control)\b",
    r"\b(clutch(es)?|electric clutch)\b",
    r"\b(rate control|population|planting rate|seed rate)\b",
]

# Parts dictionary: add your own JD part names as you build the guide
PART_TERMS = {
    # Metering / seed delivery
    "seed sensor": [r"\bseed sensor(s)?\b", r"\bsensor(s)?\b"],
    "ground speed / radar": [r"\bground speed\b", r"\bradar\b", r"\bspeed signal\b"],
    "wiring / harness / voltage": [r"\bwiring\b", r"\bharness\b", r"\bvoltage\b", r"\bbad ground\b"],
    "hydraulic drive motor": [r"\bhydraulic drive\b", r"\bdrive motor\b", r"\bhyd motor\b"],
    "vacuum system / hoses / seals": [r"\bvacuum\b", r"\bair leak\b", r"\bhose(s)?\b", r"\bseal(s)?\b", r"\bendcap(s)?\b"],
    # Row unit wear
    "bearings": [r"\bbearing(s)?\b"],
    "chains / sprockets": [r"\bchain(s)?\b", r"\bsprocket(s)?\b", r"\bidler\b"],
    "gauge wheels": [r"\bgauge wheel(s)?\b"],
    "openers / discs": [r"\bopener(s)?\b", r"\bdisc(s)?\b", r"\bdouble disc\b"],
    "closing wheels": [r"\bclosing wheel(s)?\b", r"\bpress wheel(s)?\b"],
    "downforce": [r"\bdown[- ]?force\b"],
}

DATE_REGEXES = [
    # Very loose: forums show dates in many formats; we grab "best effort"
    re.compile(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4}\b", re.I),
    re.compile(r"\b\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b", re.I),
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
]


@dataclass
class ThreadResult:
    url: str
    domain: str
    title: str
    approx_date: str
    text: str
    issues: Counter
    parts: Counter


def fetch_html(url: str) -> str:
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_S)
    r.raise_for_status()
    return r.text


def html_to_text(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")

    # remove scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    title = (soup.title.get_text(" ", strip=True) if soup.title else "").strip()

    text = soup.get_text(" ", strip=True)
    # normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return title, text


def guess_date(text: str) -> str:
    for rx in DATE_REGEXES:
        m = rx.search(text)
        if m:
            return m.group(0)
    return ""


def count_matches(patterns, text: str) -> Counter:
    c = Counter()
    for p in patterns:
        rx = re.compile(p, re.I)
        hits = rx.findall(text)
        if hits:
            c[p] += len(hits)
    return c


def count_parts(text: str) -> Counter:
    c = Counter()
    for part, pats in PART_TERMS.items():
        total = 0
        for p in pats:
            total += len(re.findall(p, text, flags=re.I))
        if total:
            c[part] = total
    return c


def mine_thread(url: str) -> ThreadResult:
    domain = urlparse(url).netloc
    html = fetch_html(url)
    title, text = html_to_text(html)
    approx_date = guess_date(text)

    issues = count_matches(ISSUE_PATTERNS, text)
    parts = count_parts(text)

    return ThreadResult(
        url=url,
        domain=domain,
        title=title,
        approx_date=approx_date,
        text=text,
        issues=issues,
        parts=parts
    )


def write_thread_csv(results: list[ThreadResult], out_csv: str):
    # Flatten into rows: one row per thread
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "url", "domain", "title", "approx_date",
            "top_issue_patterns", "top_parts"
        ])
        for r in results:
            top_issues = "; ".join([f"{k}:{v}" for k, v in r.issues.most_common(8)])
            top_parts = "; ".join([f"{k}:{v}" for k, v in r.parts.most_common(12)])
            w.writerow([r.url, r.domain, r.title, r.approx_date, top_issues, top_parts])


def write_aggregate_csv(results: list[ThreadResult], out_csv: str):
    issue_total = Counter()
    part_total = Counter()
    by_domain = defaultdict(Counter)

    for r in results:
        issue_total.update(r.issues)
        part_total.update(r.parts)
        by_domain[r.domain].update(r.parts)

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "name", "count"])
        for k, v in issue_total.most_common():
            w.writerow(["issue_pattern", k, v])
        for k, v in part_total.most_common():
            w.writerow(["part", k, v])

    # optional: per-domain part mentions
    with open(out_csv.replace(".csv", "_by_domain.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["domain", "part", "count"])
        for domain, ctr in by_domain.items():
            for part, cnt in ctr.most_common():
                w.writerow([domain, part, cnt])


DEFAULT_URLS = [
    # AgTalk examples around 1720 hydraulic drive / issues
    "https://talk.newagtalk.com/forums/thread-view.asp?DisplayType=flat&setCookie=1&tid=786926",  # hyd drive starts/stops
    "https://talk.newagtalk.com/forums/thread-view.asp?DisplayType=flat&setCookie=1&tid=786931",  # similar
    "https://talk.newagtalk.com/forums/thread-view.asp?DisplayType=nested&setCookie=1&tid=702350", # vacuum distribution / endcaps
    "https://talk.newagtalk.com/forums/thread-view.asp?DisplayType=flat&setCookie=1&tid=87695",   # planting rate problems / lag
    "https://talk.newagtalk.com/forums/thread-view.asp?DisplayType=nested&setCookie=1&tid=302591",# voltage / harness mention
    "https://talk.newagtalk.com/forums/thread-view.asp?mid=10745948&tid=1160484",                 # jerky drive motors (2024)
    # CombineForum stackfold owners (more general)
    "https://www.thecombineforum.com/threads/any-1720-stackfold-planter-owners-out-there.34161/",
]


def load_urls(path: str) -> list[str]:
    """Load URLs from a text file (one per line, # comments allowed)."""
    urls = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def main():
    parser = argparse.ArgumentParser(description="JD 1720 Forum Miner")
    parser.add_argument(
        "--output-dir", "-o", default=".",
        help="Directory to write CSV output files (default: current directory)",
    )
    parser.add_argument(
        "--urls-file", "-f", default=None,
        help="Text file with one URL per line (overrides built-in list)",
    )
    args = parser.parse_args()

    out_dir = args.output_dir
    os.makedirs(out_dir, exist_ok=True)

    if args.urls_file:
        urls = load_urls(args.urls_file)
        print(f"Loaded {len(urls)} URLs from {args.urls_file}")
    else:
        urls = DEFAULT_URLS

    results = []
    for i, url in enumerate(urls, 1):
        try:
            print(f"[{i}/{len(urls)}] Mining: {url}")
            res = mine_thread(url)
            results.append(res)
        except Exception as e:
            print(f"  !! Failed: {e}")
        time.sleep(SLEEP_BETWEEN_REQ_S)

    if not results:
        print("No results. (Possibly blocked / login required / network issue.)")
        return

    threads_csv = os.path.join(out_dir, "jd1720_threads.csv")
    aggregate_csv = os.path.join(out_dir, "jd1720_aggregate.csv")

    write_thread_csv(results, threads_csv)
    write_aggregate_csv(results, aggregate_csv)
    print(f"Done. Wrote {threads_csv} and {aggregate_csv}")


if __name__ == "__main__":
    main()
