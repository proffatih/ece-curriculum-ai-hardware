#!/usr/bin/env python3
"""
EDU01 R1 — Step 24: undergraduate coverage, representation ratio, Figs. 2-3
==========================================================================
Input : data/catalog_v2/*.csv, coverage_audit.csv, course_candidates.csv (coded),
        data/bib_windows.csv
Output: data/coverage_by_programme.csv, data/coverage_summary.csv,
        manuscript/numbers_cat.tex, figures/fig2_coverage.{pdf,png},
        figures/fig3_alignment.{pdf,png}
Rules: analysis sample = catalogues classed 'complete'; undergraduate-accessible
= level UG or UG/G; programme status per wave = UG-dedicated > UG-partial >
graduate-only (dedicated G course) > none.
"""
import csv, math, re, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CAT = DATA / "catalog_v2"
TEX = ROOT / "manuscript" / "numbers_cat.tex"
FIG = ROOT / "figures"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pro_style
pro_style.apply()

WAVES = [("ai_hardware", "AI", "AI hardware"), ("neuromorphic", "NE", "Neuromorphic"),
         ("iot_security", "SE", "IoT/HW security"), ("quantum_hw", "QU", "Quantum comp. eng.")]
UGL = {"UG", "UG/G"}
SLUG2AUDIT = {"mit": "MIT", "gatech": "Georgia Tech", "uiuc": "UIUC", "umd": "UMD College Park", "ucsd": "UCSD",
              "purdue": "Purdue", "utaustin": "UT Austin", "stanford": "Stanford", "cornell": "Cornell",
              "tamu": "Texas A&M", "cmu": "CMU", "cambridge": "Cambridge", "imperial": "Imperial College",
              "oxford": "Oxford", "tudelft": "TU Delft", "kth": "KTH", "eth": "ETH Zürich", "epfl": "EPFL",
              "nus": "NUS", "ntu": "NTU Singapore", "kaist": "KAIST", "hkust": "HKUST", "tsinghua": "Tsinghua",
              "metu": "ODTÜ (METU)", "bogazici": "Boğaziçi", "bilkent": "Bilkent"}
RNG = np.random.default_rng(20261102)
NBOOT = 5000


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, 100 * (c - h)), min(100.0, 100 * (c + h))


def fr(x):
    if x is None:
        return "undefined"
    return "unbounded" if not np.isfinite(x) else f"{x:.1f}"


def base(slug, code):
    return re.sub(r"\.\d+$", "", code) if slug == "utaustin" else code


def load(oxford_partc_ug=False):
    audit = {}
    for r in csv.DictReader(open(CAT / "coverage_audit.csv")):
        audit[r["university"]] = r
    progs = {}
    for f in sorted(CAT.glob("*.csv")):
        if f.stem == "coverage_audit":
            continue
        rows = list(csv.DictReader(open(f)))
        uni = SLUG2AUDIT[f.stem]
        ug = set()
        for c in rows:
            lev = c["level"]
            if oxford_partc_ug and f.stem == "oxford" and lev == "G":
                lev = "UG"
            if lev in UGL:
                ug.add(base(f.stem, c["code"]))
        progs[f.stem] = {"uni": uni, "status": audit[uni]["status"], "region": audit[uni]["region"],
                         "n_ug": len(ug), "ded_ug": defaultdict(set), "par_ug": defaultdict(set),
                         "ded_g": defaultdict(set)}
    for r in csv.DictReader(open(DATA / "course_candidates.csv")):
        p = progs[r["slug"]]
        lev = r["level"]
        if oxford_partc_ug and r["slug"] == "oxford" and lev == "G":
            lev = "UG"
        code = base(r["slug"], r["code"])
        if r["coding"] == "dedicated" and lev in UGL:
            p["ded_ug"][r["wave"]].add(code)
        elif r["coding"] == "partial" and lev in UGL:
            p["par_ug"][r["wave"]].add(code)
        elif r["coding"] == "dedicated":
            p["ded_g"][r["wave"]].add(code)
    return progs


def status(p, w):
    if p["ded_ug"][w]:
        return 3
    if p["par_ug"][w]:
        return 2
    if p["ded_g"][w]:
        return 1
    return 0


def research_share():
    r = {}
    for row in csv.DictReader(open(DATA / "bib_windows.csv")):
        if row["pool"] == "core":
            r[row["wave"]] = float(row["share_2023_25_pct"])
    return r


def coverage(progs, keys):
    out = {}
    n = len(keys)
    for w, t, _ in WAVES:
        st = [status(progs[k], w) for k in keys]
        k3 = sum(s == 3 for s in st)
        k23 = sum(s >= 2 for s in st)
        kg = sum(s == 1 for s in st)
        out[w] = dict(n=n, k=k3, kp=k23, kg=kg, k0=sum(s == 0 for s in st), ci=wilson(k3, n), cip=wilson(k23, n))
    return out


def main():
    progs = load()
    S = [k for k, p in progs.items() if p["status"] == "complete"]
    ALL = list(progs)
    cov, cov_all = coverage(progs, S), coverage(progs, ALL)
    cov_ox = coverage(load(oxford_partc_ug=True), S)
    rs = research_share()

    # teaching share: programme-averaged share of dedicated UG courses; RR with programme bootstrap
    ts, rr, rr_ci = {}, {}, {}
    for w, _, _ in WAVES:
        per = np.array([len(progs[k]["ded_ug"][w]) / progs[k]["n_ug"] for k in S])
        ts[w] = 100 * per.mean()
        if ts[w] == 0:  # no dedicated UG course anywhere: ratio undefined (unbounded)
            rr[w], rr_ci[w] = None, (None, None)
            continue
        rr[w] = rs[w] / ts[w]
        boots = []
        for _ in range(NBOOT):
            m = 100 * RNG.choice(per, size=len(per), replace=True).mean()
            boots.append(rs[w] / m if m else np.inf)
        b = np.array(boots)
        b = np.where(np.isfinite(b), b, np.inf)
        rr_ci[w] = (np.percentile(b, 2.5), np.percentile(b, 97.5))

    n_all4 = sum(all(status(progs[k], w) == 3 for w, _, _ in WAVES) for k in S)
    n_none = sum(all(status(progs[k], w) < 3 for w, _, _ in WAVES) for k in S)
    n_ug = sum(progs[k]["n_ug"] for k in S)
    n_ded_ug = {w: sum(len(progs[k]["ded_ug"][w]) for k in S) for w, _, _ in WAVES}
    n_ded_g = {w: sum(len(progs[k]["ded_g"][w]) for k in S) for w, _, _ in WAVES}
    cand = list(csv.DictReader(open(DATA / "course_candidates.csv")))
    n_cand = len(cand)
    pct = {c: 100 * sum(r["coding"] == c for r in cand) / n_cand for c in ("dedicated", "partial", "false")}
    max_partial_gain = max(cov[w]["kp"] - cov[w]["k"] for w, _, _ in WAVES)

    L = ["% generated by scripts/24_catalogue_indicators.py — do not edit",
         f"\\newcommand{{\\nProgAll}}{{{len(ALL)}}}", f"\\newcommand{{\\nProg}}{{{len(S)}}}",
         f"\\newcommand{{\\nProgPartial}}{{{len(ALL) - len(S)}}}",
         f"\\newcommand{{\\nCand}}{{{n_cand}}}", f"\\newcommand{{\\nUG}}{{{n_ug:,}}}".replace(",", "\\,"),
         f"\\newcommand{{\\nAllFour}}{{{n_all4}}}", f"\\newcommand{{\\nNoneFour}}{{{n_none}}}",
         f"\\newcommand{{\\pctDed}}{{{pct['dedicated']:.0f}}}", f"\\newcommand{{\\pctPar}}{{{pct['partial']:.0f}}}",
         f"\\newcommand{{\\pctFalse}}{{{pct['false']:.0f}}}", f"\\newcommand{{\\maxPartialGain}}{{{max_partial_gain}}}"]
    summ = []
    for w, t, lab in WAVES:
        c, ca, co = cov[w], cov_all[w], cov_ox[w]
        L += [f"\\newcommand{{\\cov{t}k}}{{{c['k']}}}",
              f"\\newcommand{{\\cov{t}}}{{{100 * c['k'] / c['n']:.0f}}}",
              f"\\newcommand{{\\cov{t}lo}}{{{c['ci'][0]:.0f}}}", f"\\newcommand{{\\cov{t}hi}}{{{c['ci'][1]:.0f}}}",
              f"\\newcommand{{\\covp{t}k}}{{{c['kp']}}}", f"\\newcommand{{\\covp{t}}}{{{100 * c['kp'] / c['n']:.0f}}}",
              f"\\newcommand{{\\covg{t}k}}{{{c['kg']}}}", f"\\newcommand{{\\covn{t}k}}{{{c['k0']}}}",
              f"\\newcommand{{\\nd{t}}}{{{n_ded_ug[w]}}}", f"\\newcommand{{\\ndg{t}}}{{{n_ded_g[w]}}}",
              f"\\newcommand{{\\ts{t}}}{{{ts[w]:.2f}}}", f"\\newcommand{{\\rs{t}}}{{{rs[w]:.2f}}}",
              f"\\newcommand{{\\rr{t}}}{{{fr(rr[w])}}}",
              f"\\newcommand{{\\rr{t}lo}}{{{fr(rr_ci[w][0])}}}", f"\\newcommand{{\\rr{t}hi}}{{{fr(rr_ci[w][1])}}}",
              f"\\newcommand{{\\covs{t}}}{{{100 * ca['k'] / ca['n']:.0f}}}",
              f"\\newcommand{{\\covo{t}}}{{{100 * co['k'] / co['n']:.0f}}}"]
        summ.append([w, c["n"], c["k"], round(100 * c["k"] / c["n"], 1), round(c["ci"][0], 1), round(c["ci"][1], 1),
                     c["kp"], c["kg"], c["k0"], n_ded_ug[w], n_ded_g[w], round(ts[w], 3), rs[w],
                     fr(rr[w]), fr(rr_ci[w][0]), fr(rr_ci[w][1]),
                     round(100 * ca["k"] / ca["n"], 1), round(100 * co["k"] / co["n"], 1)])
    TEX.write_text("\n".join(L) + "\n")
    with open(DATA / "coverage_summary.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["wave", "n_prog", "k_ug_dedicated", "coverage_pct", "ci_lo", "ci_hi", "k_ug_ded_or_partial",
                     "k_grad_only", "k_none", "n_ded_ug_courses", "n_ded_g_courses", "teaching_share_pct",
                     "research_share_core_2023_25_pct", "RR", "RR_lo", "RR_hi",
                     "coverage_pct_all26", "coverage_pct_oxford_partC_UG"])
        wr.writerows(summ)
    with open(DATA / "coverage_by_programme.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["slug", "university", "region", "catalogue_status", "n_ug_courses"] +
                    [f"{w}_status" for w, _, _ in WAVES] + [f"{w}_ug_dedicated_codes" for w, _, _ in WAVES])
        names = {3: "UG dedicated", 2: "UG partial", 1: "graduate only", 0: "none"}
        for k, p in progs.items():
            wr.writerow([k, p["uni"], p["region"], p["status"], p["n_ug"]] +
                        [names[status(p, w)] for w, _, _ in WAVES] +
                        [" ".join(sorted(p["ded_ug"][w])) for w, _, _ in WAVES])
    for s in summ:
        print(s)
    print("all four:", n_all4, " none of four:", n_none, " n_ug:", n_ug)

    # ---- Fig. 2: programme x wave status (complete catalogues), ordered by region
    order = {"USA": 0, "Europe": 1, "Asia": 2, "Türkiye": 3}
    K = sorted(S, key=lambda k: (order.get(progs[k]["region"], 9), progs[k]["uni"]))
    M = np.array([[status(progs[k], w) for w, _, _ in WAVES] for k in K])
    cmap = ListedColormap(["#F2F2F2", "#C9D6E8", "#7FA3CC", "#2E5A87"])
    fig, ax = plt.subplots(figsize=(3.5, 5.6))
    ax.imshow(M, cmap=cmap, vmin=0, vmax=3, aspect="auto")
    ax.set_xticks(range(4), ["AI\nhardware", "Neuro-\nmorphic", "IoT/HW\nsecurity", "Quantum\ncomputing"], fontsize=8)
    ax.xaxis.tick_top()
    short = {"UMD College Park": "UMD", "Imperial College": "Imperial", "ODTÜ (METU)": "METU",
             "Texas A&M": "Texas A&M", "Georgia Tech": "Georgia Tech"}
    ax.set_yticks(range(len(K)), [short.get(progs[k]["uni"], progs[k]["uni"]) for k in K], fontsize=7.5)
    ax.set_xticks(np.arange(-.5, 4, 1), minor=True); ax.set_yticks(np.arange(-.5, len(K), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2); ax.grid(which="major", visible=False)
    ax.tick_params(which="minor", length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    from matplotlib.patches import Patch
    leg = [Patch(color=cmap(i), label=l) for i, l in
           [(3, "UG dedicated"), (2, "UG partial only"), (1, "Graduate only"), (0, "None")]]
    ax.legend(handles=leg, loc="upper center", bbox_to_anchor=(0.4, -0.01), ncol=2, fontsize=7.5)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig2_coverage.{ext}")

    # ---- Fig. 3: research share vs coverage
    fig, ax = plt.subplots(figsize=(3.5, 2.6))
    marks = {"AI": "o", "NE": "s", "SE": "^", "QU": "D"}
    for (w, t, lab), c in zip(WAVES, pro_style.PALETTE):
        y = 100 * cov[w]["k"] / cov[w]["n"]
        lo, hi = cov[w]["ci"]
        ax.errorbar(rs[w], y, yerr=[[y - lo], [hi - y]], fmt=marks[t], color=c, capsize=3, ms=6, label=lab)
    ax.set_xlabel("Research share, 2023–25 (%)")
    ax.set_ylabel("Programmes with a dedicated\nUG course (%)")
    ax.set_ylim(-4, 100); ax.set_xlim(0, max(rs.values()) * 1.25)
    ax.legend(loc="upper right", fontsize=7.5)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig3_alignment.{ext}")


if __name__ == "__main__":
    main()
