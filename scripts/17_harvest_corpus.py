#!/usr/bin/env python3
"""
EDU01 R1 — Step 17: full-corpus harvest of the 13-journal IEEE pool
===================================================================
Replaces the relevance-count approach of step 01. Crossref
`query.bibliographic` is a relevance (OR-token) search, so its
`total-results` counts every article sharing any query token. Here every
journal-article of every pool journal is downloaded (DOI, title, abstract,
issue date) and classified locally by exact-phrase matching (step 18).

Output (outside git, large): $EDU01_RUN_OUT/corpus/<journal>_<year>.jsonl
Usage: EDU01_RUN_OUT=~/run_out/EDU01 python3 scripts/17_harvest_corpus.py
Resumable: finished (journal, year) files are skipped.
"""
import json, os, sys, time
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
KW = json.loads((ROOT / "data" / "ieee_xplore_keywords.json").read_text())
POOL = KW["_meta"]["ieee_journals_issn_pool"]
OUT = Path(os.environ.get("EDU01_RUN_OUT", Path.home() / "run_out" / "EDU01")) / "corpus"
OUT.mkdir(parents=True, exist_ok=True)

API = "https://api.crossref.org/works"
HEADERS = {"User-Agent": "EDU01-bibliometrics/2.0 (mailto:fatih.gul@erdogan.edu.tr)"}
SELECT = "DOI,title,abstract,issued,published-print,published-online,container-title,ISSN,type"


def get(params):
    for attempt in range(8):
        try:
            r = requests.get(API, params=params, headers=HEADERS, timeout=120)
            if r.status_code == 200:
                return r.json()["message"]
            time.sleep(min(60, 2 ** attempt))
        except requests.RequestException:
            time.sleep(min(60, 2 ** attempt))
    raise RuntimeError(f"failed: {params}")


def harvest(abbr, issn, year):
    done = OUT / f"{abbr}_{year}.jsonl"
    if done.exists():
        return
    tmp = done.with_suffix(".part")
    params = {
        "filter": f"issn:{issn},from-pub-date:{year}-01-01,until-pub-date:{year}-12-31,type:journal-article",
        "select": SELECT, "rows": 1000, "cursor": "*",
    }
    n, total = 0, None
    with tmp.open("w") as f:
        while True:
            msg = get(params)
            total = msg["total-results"]
            items = msg["items"]
            for it in items:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
            n += len(items)
            if not items or n >= total:
                break
            params["cursor"] = msg["next-cursor"]
    tmp.rename(done)
    print(f"{abbr} {year}: {n}/{total}", flush=True)


def main():
    for abbr, issn in POOL.items():
        for year in range(2015, 2026):
            harvest(abbr, issn, year)
    print("HARVEST DONE", flush=True)


if __name__ == "__main__":
    sys.exit(main())
