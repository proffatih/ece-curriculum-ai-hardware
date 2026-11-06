#!/usr/bin/env python3
"""
EDU01 R1 — Step 26: Supplementary Material (Tables S1-S10) from the data files
=============================================================================
Output: supplementary/SI.tex (compiled separately). Nothing is typed by hand.
"""
import csv, gzip, json, re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data"
OUT = ROOT / "supplementary" / "SI.tex"
OUT.parent.mkdir(exist_ok=True)
WL = {"ai_hardware": "AI hardware", "neuromorphic": "Neuromorphic", "iot_security": "IoT/HW security",
      "quantum_hw": "Quantum comp. eng."}
JOURNALS = {"TCAS-I": "IEEE Trans. Circuits and Systems I: Regular Papers",
            "TCAS-II": "IEEE Trans. Circuits and Systems II: Express Briefs",
            "TVLSI": "IEEE Trans. Very Large Scale Integration (VLSI) Systems",
            "TED": "IEEE Trans. Electron Devices", "EDL": "IEEE Electron Device Letters",
            "JSSC": "IEEE Journal of Solid-State Circuits", "IoT-J": "IEEE Internet of Things Journal",
            "T-NANO": "IEEE Trans. Nanotechnology", "TNNLS": "IEEE Trans. Neural Networks and Learning Systems",
            "T-EDUC": "IEEE Trans. Education", "ACCESS": "IEEE Access",
            "JETCAS": "IEEE J. Emerging and Selected Topics in Circuits and Systems",
            "T-QE": "IEEE Trans. Quantum Engineering"}


def esc(s):
    s = str(s)
    rep = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
           "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(rep.get(c, c) for c in s)


def code(s):
    return r"\texttt{" + esc(s).replace("|", r"\allowbreak|").replace("(", r"\allowbreak(") + "}"


def longtable(cols, head, rows, caption, label):
    out = [r"\begin{longtable}{" + cols + "}", r"\caption{" + caption + r"}\label{" + label + r"}\\",
           r"\toprule", " & ".join(head) + r" \\", r"\midrule", r"\endfirsthead",
           r"\toprule", " & ".join(head) + r" \\", r"\midrule", r"\endhead", r"\bottomrule", r"\endlastfoot"]
    out += [" & ".join(r) + r" \\" for r in rows]
    out.append(r"\end{longtable}")
    return "\n".join(out)


def main():
    kw = json.loads((ROOT / "data" / "ieee_xplore_keywords.json").read_text())["_meta"]["ieee_journals_issn_pool"]
    defs = json.loads((D / "wave_definitions_v2.json").read_text())
    pool = Counter()
    for r in csv.DictReader(open(D / "pool_yearly.csv")):
        pool[r["journal"]] += int(r["n_articles"])
    T = []
    # S1
    T.append(longtable("@{}llll@{}", ["Abbr.", "Journal", "ISSN", "Articles 2015--25"],
                       [[esc(a), esc(JOURNALS[a]), kw[a], f"{pool[a]:,}".replace(",", r"\,")] for a in kw],
                       "Journal pool (research articles after removal of non-research items). Core pool = all except \\emph{IEEE Access} and \\emph{IoT Journal}.", "tab:S1"))
    # S2
    rows = []
    for w, d in defs["waves"].items():
        for p in d["include"]:
            rows.append([esc(WL[w]), "include", code(p)])
        for p in d["exclude"]:
            rows.append([esc(WL[w]), "exclude", code(p)])
    rows.append(["all", "non-research", code(defs["_meta"]["non_research_filter"])])
    T.append(r"\noindent\textbf{Matching.} " + esc(defs["_meta"]["matching"]) + "\n\n" +
             r"\noindent\textbf{Revision log.} " + esc(defs["_meta"]["revision_log"]) + "\n")
    T.append(longtable("@{}lL{1.6cm}L{11.5cm}@{}", ["Wave", "Type", "Regular expression"], rows,
                       "Wave classification rules (final, frozen before the round-3 validation).", "tab:S2"))
    # S3
    summ = list(csv.DictReader(open(D / "bib_summary.csv")))
    rows = [[esc(WL[s["wave"]]), s["precision_k/n"], s["nearmiss_should_match_k/n"], f"{100*float(s['recall_est']):.0f}\\%"] for s in summ]
    T.append(longtable("@{}llll@{}", ["Wave", "Precision (round 3)", "Near-miss should match", "Recall bound"], rows,
                       "Validation summary. Rounds 1--2 (seeds 20261102, 20261103) were used to refine the rules; round 3 (seed 20261104) is the held-out estimate. Coded records of all rounds are in the data release.", "tab:S3"))
    rows = []
    for f, kind, col in (("validation_precision.csv", "P", "relevant(1/0)"), ("validation_nearmiss.csv", "N", "should_match(1/0)")):
        for r in csv.DictReader(open(D / f)):
            rows.append([kind, esc(WL[r["wave"]]), esc(r["title"][:95]), r[col], esc(r["note"][:60])])
    T.append(r"\addtocounter{table}{-1}")  # coded records continue Table S3 (keeps S4-S10 aligned with the manuscript)
    T.append(longtable("@{}llL{8.6cm}lL{4.2cm}@{}", ["S.", "Wave", "Title", "Code", "Note"], rows,
                       "(continued) Round-3 coded records (S.: P = precision sample, code 1 = relevant; N = near-miss sample, code 1 = should have matched).", "tab:S3b"))
    # S4/S5
    aud = list(csv.DictReader(open(D / "catalog_v2" / "coverage_audit.csv")))
    T.append(longtable("@{}llL{11.3cm}@{}", ["Programme", "Region", "Source"],
                       [[esc(a["university"]), esc(a["region"]), r"{\scriptsize\url{" + a["source_url"].split(" ; ")[0] + "}}"] for a in aud],
                       "Programme sample and primary catalogue source (retrieved 2 November 2026; all sources in the data release).", "tab:S4"))
    T.append(longtable("@{}lllrrrlL{6.3cm}@{}", ["Programme", "Status", "Source type", "UG", "UG/G", "G", "Descr.", "Notes"],
                       [[esc(a["university"]), a["status"], esc(a["source_type"]), a["n_UG"], a["n_dual"], a["n_G"],
                         esc(a["descriptions_available"][:10]), esc(a["notes"][:160])] for a in aud],
                       "Catalogue coverage audit. Only catalogues with status `complete' enter the analysis.", "tab:S5"))
    # S6
    src = (ROOT / "scripts" / "23_match_catalogue_v2.py").read_text()
    pats = re.findall(r'"(\w+)": \[(.*?)\],\n', src[src.index("PAT = {"):src.index("EXCL")], re.S)
    rows = []
    for w, body in pats:
        for p in re.findall(r'r"(.*?)"', body):
            rows.append([esc(WL[w]), code(p)])
    T.append(longtable("@{}lL{13cm}@{}", ["Wave", "Pattern (titles and descriptions, lower-cased, hyphens as spaces)"], rows,
                       "Course candidate patterns. Every candidate was then coded manually (Table~S7).", "tab:S6"))
    # S7
    rows = [[esc(r["slug"]), esc(r["code"]), esc(r["title"][:55]), r["level"], esc(WL[r["wave"]]), r["coding"], esc(r["coding_note"][:55])]
            for r in csv.DictReader(open(D / "course_candidates.csv"))]
    T.append(longtable("@{}llL{4.6cm}llll@{}", ["Prog.", "Code", "Title", "Level", "Wave", "Coding", "Justification"], rows,
                       "Course coding sheet (all candidates).", "tab:S7"))
    # S8
    rows = []
    with gzip.open(D / "corpus_titles.csv.gz", "rt") as f:
        for r in csv.DictReader(f):
            if r["journal"] == "T-EDUC" and re.search(r"memris|neural|neuro|spik|accelerat|in-memory|secur|trojan|unclonable|side-channel|quantum|qubit|hardware|machine learning|deep learning|artificial intelligence", r["title"], re.I):
                rows.append([r["year_bucket"], esc(r["title"][:120])])
    T.append(longtable("@{}lL{14cm}@{}", ["Year", "Title"], sorted(rows),
                       "All \\emph{IEEE Trans.\\ Education} titles 2015--2025 containing security, ML, neural, hardware, or quantum terms.", "tab:S8"))
    # S9
    rows = [[esc(WL[r["wave"]]), esc(r["topic"]), r["n_titles"], r["pct"]] for r in csv.DictReader(open(D / "topic_terms.csv"))]
    T.append(longtable("@{}lL{8cm}rr@{}", ["Wave", "Topic group", "Titles", "\\%"], rows,
                       "Topic groups in 2021--2025 classified titles (a-priori term lists in the code); input to module content.", "tab:S9"))
    # S10
    rows = []
    for r in csv.DictReader(open(D / "coverage_by_programme.csv")):
        if r["catalogue_status"] != "complete":
            continue
        for w in WL:
            if r[w + "_ug_dedicated_codes"]:
                rows.append([esc(r["university"]), esc(WL[w]), "UG", esc(r[w + "_ug_dedicated_codes"])])
    for r in csv.DictReader(open(D / "course_candidates.csv")):
        if r["wave"] == "neuromorphic" and r["coding"] == "dedicated" and r["level"] == "G":
            rows.append([esc(r["university"][:30]), "Neuromorphic", "G", esc(r["code"] + " " + r["title"][:45])])
    T.append(longtable("@{}llll@{}", ["Programme", "Wave", "Level", "Course codes"], rows,
                       "Reference implementations: dedicated undergraduate-accessible courses per programme and wave, and graduate neuromorphic courses.", "tab:S10"))

    doc = r"""\documentclass[10pt]{article}
\usepackage[margin=1.8cm,landscape]{geometry}
\usepackage[T1]{fontenc}\usepackage[utf8]{inputenc}\usepackage{lmodern}
\usepackage{booktabs,longtable,array,url}
\DeclareUnicodeCharacter{221E}{$\infty$}\DeclareUnicodeCharacter{2093}{$_x$}\DeclareUnicodeCharacter{03BC}{$\mu$}
\usepackage[hidelinks]{hyperref}
\renewcommand{\thetable}{S\arabic{table}}
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\setlength{\LTcapwidth}{\linewidth}
\begin{document}
\begin{center}{\Large Supplementary Material}\\[4pt]
Mapping AI-Hardware Topics in the Electrical and Computer Engineering Curriculum:
A Bibliometric and Course-Catalogue Analysis and a Data-Informed Modular Track\\[2pt]
Fatih G\"ul\end{center}
\footnotesize
""" + "\n\n".join(T) + "\n\\end{document}\n"
    OUT.write_text(doc)
    print("SI written")


if __name__ == "__main__":
    main()
