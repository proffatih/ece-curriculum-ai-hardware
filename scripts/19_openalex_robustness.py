#!/usr/bin/env python3
"""
EDU01 R1 — Step 19: title+abstract robustness check via OpenAlex
================================================================
Crossref carries no IEEE abstracts, so the primary classification (step 18)
is title-based. This step repeats the count on titles AND abstracts using
OpenAlex quoted-phrase Boolean search over the same 13 journals, grouped by
publication year (one request per wave plus one for the pool total).
Output: data/openalex_title_abstract_yearly.csv
"""
import csv, json, time
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
POOL = json.loads((ROOT / "data" / "ieee_xplore_keywords.json").read_text())["_meta"]["ieee_journals_issn_pool"]
OUT = ROOT / "data" / "openalex_title_abstract_yearly.csv"
API = "https://api.openalex.org/works"

PHRASES = {
    "ai_hardware": ["in-memory computing", "compute-in-memory", "computing-in-memory", "processing-in-memory",
                    "neural network accelerator", "deep learning accelerator", "DNN accelerator",
                    "CNN accelerator", "AI accelerator", "neural processing unit", "memristor crossbar",
                    "RRAM crossbar"],
    "neuromorphic": ["neuromorphic", "spiking neural network", "artificial synapse", "synaptic device",
                     "synaptic transistor", "brain-inspired computing"],
    "iot_security": ["physical unclonable function", "physically unclonable function", "hardware Trojan",
                     "side-channel attack", "hardware security", "root of trust",
                     "trusted execution environment", "logic locking"],
    "quantum_hw": ["qubit", "quantum processor", "quantum computer", "superconducting quantum",
                   "quantum error correction", "NISQ", "cryo-CMOS"],
}


def by_year(extra):
    flt = "primary_location.source.issn:" + "|".join(POOL.values()) + ",publication_year:2015-2025,type:article"
    if extra:
        flt += "," + extra
    r = requests.get(API, params={"filter": flt, "group_by": "publication_year", "per_page": 200}, timeout=60)
    r.raise_for_status()
    return {int(g["key"]): g["count"] for g in r.json()["group_by"]}


def main():
    total = by_year("")
    rows = []
    for wave, ph in PHRASES.items():
        q = " OR ".join(f'"{p}"' for p in ph)
        c = by_year("title_and_abstract.search:" + q)
        for y in range(2015, 2026):
            rows.append([wave, y, c.get(y, 0), total.get(y, 0), round(100 * c.get(y, 0) / total[y], 3)])
        time.sleep(1)
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["wave", "year", "n", "pool_total", "share_pct"]); w.writerows(rows)
    for r in rows:
        if r[1] in (2015, 2025):
            print(r)


if __name__ == "__main__":
    main()
