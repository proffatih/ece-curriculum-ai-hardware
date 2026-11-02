#!/usr/bin/env python3
"""EDU01 R1 — Fig. 1: research output per wave (a) article counts, (b) share of core-pool output."""
import csv, sys
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pro_style
pro_style.apply()

V2 = ROOT / "data"
OUT = ROOT / "figures"
OUT.mkdir(parents=True, exist_ok=True)
WAVES = [("ai_hardware", "AI hardware", "o"), ("neuromorphic", "Neuromorphic computing", "s"),
         ("iot_security", "IoT/hardware security", "^"), ("quantum_hw", "Quantum computing eng.", "D")]
CORE_EXCLUDE = {"ACCESS", "IoT-J"}
YEARS = list(range(2015, 2026))

n_all = defaultdict(lambda: defaultdict(int))
n_core = defaultdict(lambda: defaultdict(int))
tot_core = defaultdict(int)
for r in csv.DictReader(open(V2 / "pool_yearly.csv")):
    if r["journal"] not in CORE_EXCLUDE:
        tot_core[int(r["year"])] += int(r["n_articles"])
for r in csv.DictReader(open(V2 / "wave_matches.csv")):
    y = int(r["year"])
    for w in r["waves"].split(";"):
        n_all[w][y] += 1
        if r["journal"] not in CORE_EXCLUDE:
            n_core[w][y] += 1

fig, (a, b) = plt.subplots(1, 2, figsize=(7.16, 2.7))
for (w, lab, m), c in zip(WAVES, pro_style.PALETTE):
    a.plot(YEARS, [n_all[w][y] for y in YEARS], marker=m, color=c, label=lab)
    b.plot(YEARS, [100 * n_core[w][y] / tot_core[y] for y in YEARS], marker=m, color=c, label=lab)
a.set_ylabel("Articles per year (13 journals)")
b.set_ylabel("Share of core-pool articles (%)")
for ax, t in ((a, "(a)"), (b, "(b)")):
    ax.set_xticks(YEARS[::2])
    ax.set_xlabel("Publication year")
    ax.set_title(t, loc="left", fontsize=10, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.9))
h, l = a.get_legend_handles_labels()
fig.legend(h, l, loc="upper center", ncol=4, bbox_to_anchor=(0.5, 1.0), handlelength=1.6, columnspacing=1.0)
for ext in ("pdf", "png"):
    fig.savefig(OUT / f"fig1_research_trends.{ext}")
print("ok")
