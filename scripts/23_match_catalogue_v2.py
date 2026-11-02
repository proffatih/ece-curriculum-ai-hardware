#!/usr/bin/env python3
"""
EDU01 R1 — Step 23: course candidates per wave from the rebuilt catalogues
==========================================================================
Input : data/catalog_v2/<slug>.csv (code,title,description,level,...),
        data/catalog_v2/coverage_audit.csv
Output: data/course_candidates.csv — every course whose title or
        description matches a wave pattern; columns `coding` (dedicated /
        partial / false) and `coding_note` are filled by manual inspection.
Existing manual codes are preserved when the script is re-run.
"""
import csv, glob, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data" / "catalog_v2"
OUT = ROOT / "data" / "course_candidates.csv"
PAT = {
    "ai_hardware": [r"hardware (for|of) (machine learning|deep learning|ai|artificial intelligence|neural)",
                    r"(machine learning|deep learning|neural network|ai|dnn) (hardware|accelerat|processors?|chips?|systems? design)",
                    r"accelerat\w* (for|of) (machine learning|deep learning|neural|ai)",
                    r"in memory comput", r"compute in memory", r"processing in memory", r"memristor", r"memristive",
                    r"\brram\b", r"\breram\b", r"neural processing unit", r"\btinyml\b", r"\bsystolic",
                    r"(circuits?|chips?|hardware|vlsi|socs?|processors?|architectures?|systems?) for (ai|artificial intelligence|machine learning|deep learning|neural)",
                    r"\b(ai|ml) (circuits?|chips?|vlsi|socs?|hardware|accelerators?|processors?)",
                    r"efficient (deep learning|machine learning|ml|ai|neural)",
                    r"neural networks? (implementation|hardware|chips?|circuits?|accelerat)"],
    "neuromorphic": [r"neuromorphic", r"spiking", r"brain inspired", r"synaptic (device|transistor)s?",
                     r"silicon neuron"],
    "iot_security": [r"hardware security", r"secure hardware", r"side channel", r"physical(ly)? unclonable",
                     r"\bpufs?\b", r"hardware trojan", r"trusted execution", r"root of trust",
                     r"fault (injection|attack)", r"trusted hardware", r"hardware (attack|trust)",
                     r"embedded (system )?security", r"security of (embedded|iot|cyber physical)",
                     r"tamper", r"cryptographic (hardware|engineering)", r"trusted computing"],
    "quantum_hw": [r"\bqubits?\b", r"quantum comput", r"quantum information", r"quantum engineering",
                   r"quantum technolog", r"quantum hardware", r"quantum (circuit|algorithm|software|processor)s?",
                   r"\bnisq\b"],
}
EXCL = {"quantum_hw": [r"post quantum"]}
COMP = {w: [re.compile(p) for p in ps] for w, ps in PAT.items()}
EXC = {w: [re.compile(p) for p in ps] for w, ps in EXCL.items()}


def norm(s):
    return re.sub(r"\s+", " ", (s or "").lower().replace("-", " "))


def main():
    old = {}
    if OUT.exists():
        for r in csv.DictReader(open(OUT)):
            old[(r["slug"], r["code"], r["wave"])] = (r["coding"], r["coding_note"])
    rows = []
    for f in sorted(glob.glob(str(CAT / "*.csv"))):
        slug = Path(f).stem
        if slug == "coverage_audit":
            continue
        for c in csv.DictReader(open(f)):
            t, d = norm(c["title"]), norm(c["description"])
            for w in PAT:
                th = any(p.search(t) for p in COMP[w])
                dh = any(p.search(d) for p in COMP[w])
                if (th or dh) and not any(p.search(t + " " + d) for p in EXC.get(w, [])):
                    code, note = old.get((slug, c["code"], w), ("", ""))
                    rows.append({"slug": slug, "university": c["university"], "code": c["code"],
                                 "title": c["title"], "level": c["level"], "wave": w,
                                 "hit": "title" if th else "description",
                                 "description": (c["description"] or "")[:600],
                                 "coding": code, "coding_note": note})
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"{len(rows)} candidates; uncoded {sum(1 for r in rows if not r['coding'])}")


if __name__ == "__main__":
    main()
