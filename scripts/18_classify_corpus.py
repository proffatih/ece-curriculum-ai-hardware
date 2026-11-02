#!/usr/bin/env python3
"""
EDU01 R1 — Step 18: exact-phrase wave classification of the harvested corpus
============================================================================
Input : $EDU01_RUN_OUT/corpus/*.jsonl (step 17), data/wave_definitions_v2.json
Output: data/pool_yearly.csv          articles per journal-year (denominator)
        data/wave_matches.csv         every matched article (DOI, year, journal, title, waves)
        data/wave_yearly.csv          wave x year counts, pool share, growth
        data/validation_precision.csv random matched sample per wave (for manual coding)
        data/validation_nearmiss.csv  random unmatched titles containing a seed token
"""
import csv, glob, html, json, os, random, re, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = Path(os.environ.get("EDU01_RUN_OUT", Path.home() / "run_out" / "EDU01")) / "corpus"
OUT = ROOT / "data"
OUT.mkdir(parents=True, exist_ok=True)
DEFS = json.loads((ROOT / "data" / "wave_definitions_v2.json").read_text())
DEF = DEFS["waves"]
NONRES = re.compile(DEFS["_meta"]["non_research_filter"], re.I)
PAT = {w: ([re.compile(p, re.I) for p in d["include"]], [re.compile(p, re.I) for p in d["exclude"]])
       for w, d in DEF.items()}
SEEDS = {"ai_hardware": r"accelerat|memristor|in-memory|crossbar",
         "neuromorphic": r"spik|synap|brain|neuro",
         "iot_security": r"secur|attack|trojan|trust",
         "quantum_hw": r"quantum"}
N_PREC, N_MISS, SEED = 50, 30, 20261104  # rounds 1-2 (rule tuning) used 20261102, 20261103


def clean(t):
    t = html.unescape(t)
    t = re.sub(r"<[^>]+>", " ", t)              # MathML / JATS tags
    t = re.sub(r"\$[^$]*\$", " ", t)            # inline LaTeX
    t = t.replace("‐", "-").replace("‑", "-").replace("–", "-")
    return re.sub(r"\s+", " ", t).strip()


def classify(title):
    title = title.lower().replace("-", " ")
    hits = []
    for w, (inc, exc) in PAT.items():
        if any(p.search(title) for p in inc) and not any(p.search(title) for p in exc):
            hits.append(w)
    return hits


def main():
    seen, rows, n_nonres = set(), [], [0]
    for f in sorted(glob.glob(str(RUN / "*.jsonl"))):
        journal, year = Path(f).stem.rsplit("_", 1)
        for line in open(f):
            d = json.loads(line)
            doi = d["DOI"].lower()
            if doi in seen or not d.get("title"):
                continue
            seen.add(doi)
            t = clean(d["title"][0])
            if NONRES.match(t):
                n_nonres[0] += 1
                continue
            rows.append((doi, int(year), journal, t))

    pool = Counter((y, j) for _, y, j, _ in rows)
    with open(OUT / "pool_yearly.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["year", "journal", "n_articles"])
        for (y, j), n in sorted(pool.items()):
            w.writerow([y, j, n])

    matched, by_wave = [], defaultdict(list)
    for doi, y, j, t in rows:
        h = classify(t)
        if h:
            matched.append((doi, y, j, t, ";".join(h)))
            for w in h:
                by_wave[w].append((doi, y, j, t))
    with open(OUT / "wave_matches.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["doi", "year", "journal", "title", "waves"]); w.writerows(matched)

    tot_year = Counter(y for _, y, _, _ in rows)
    with open(OUT / "wave_yearly.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["wave", "year", "n", "pool_total", "share_pct"])
        for wave in DEF:
            c = Counter(y for _, y, _, _ in by_wave[wave])
            for y in sorted(tot_year):
                w.writerow([wave, y, c[y], tot_year[y], round(100 * c[y] / tot_year[y], 3)])

    matched_dois = {m[0] for m in matched}
    nm_pool = {wave: [r for r in rows if r[0] not in matched_dois and re.search(s, r[3], re.I)]
               for wave, s in SEEDS.items()}
    (OUT / "nearmiss_pool_sizes.json").write_text(json.dumps({w: len(c) for w, c in nm_pool.items()}))
    if "--sample" not in sys.argv:  # coded validation files must not be regenerated
        print(f"corpus {len(rows)} research articles ({n_nonres[0]} non-research items removed), {len(matched)} matched")
        return
    rng = random.Random(SEED)
    with open(OUT / "validation_precision.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["wave", "doi", "year", "journal", "title", "relevant(1/0)", "note"])
        for wave in DEF:
            for r in rng.sample(by_wave[wave], min(N_PREC, len(by_wave[wave]))):
                w.writerow([wave, *r, "", ""])
    matched_dois = {m[0] for m in matched}
    with open(OUT / "validation_nearmiss.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["wave", "doi", "year", "journal", "title", "should_match(1/0)", "note"])
        for wave, s in SEEDS.items():
            cand = [r for r in rows if r[0] not in matched_dois and re.search(s, r[3], re.I)]
            for r in rng.sample(cand, min(N_MISS, len(cand))):
                w.writerow([wave, *r, "", ""])
            print(f"{wave}: matched {len(by_wave[wave])}, near-miss pool {len(cand)}")
    print(f"corpus {len(rows)} research articles ({n_nonres[0]} non-research items removed), {len(matched)} matched")


if __name__ == "__main__":
    main()
