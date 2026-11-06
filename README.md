# Research share vs. undergraduate coverage of four AI-era hardware topics in ECE

Data and code for:

> F. Gül, "Mapping AI-Hardware Topics in the Electrical and Computer Engineering
> Curriculum: A Bibliometric and Course-Catalogue Analysis and a Data-Informed
> Modular Track," *IEEE Transactions on Education* (under review).

The study compares how much of the electrical and computer engineering (ECE)
research literature four hardware topics occupy — **AI hardware, neuromorphic
computing, IoT/hardware security, and quantum computing engineering** — with how
often they are taught as dedicated undergraduate courses, and derives a modular
elective track from the comparison.

* **Research side:** all research articles of 13 IEEE journals, 2015–2025
  (161,464 after removing non-research items), classified by exact-phrase title
  rules that were validated on manually coded random samples.
* **Teaching side:** the current course catalogues of 26 ECE departments,
  rebuilt from official sources (23 complete), with every candidate course coded
  manually as dedicated, partial, or not relevant.

Every number, table and figure in the manuscript and its Supplementary Material
is produced by the scripts in this repository.

## Repository layout

```
data/                     derived data and manually coded sheets (see below)
data/catalog_v2/          rebuilt course catalogues, one CSV per department,
                          coverage_audit.csv and a method note (README.md)
scripts/                  analysis pipeline (steps 17–26) and pro_style.py
scripts/catalog_extract/  catalogue acquisition scripts, one per department
figures/                  figures of the manuscript (PDF and PNG)
manuscript/               numbers_*.tex (all numbers quoted in the text) and refs.bib
supplementary/SI.tex      source of Supplementary Tables S1–S10
```

## Reproducing the results

Run every script from the repository root. Step numbers continue the
project's internal numbering.

**From the included data (no download needed)** — regenerates all indicators,
figures, number macros and the Supplementary Material:

```
python3 scripts/20_bib_indicators.py
python3 scripts/21_make_fig1_v2.py
python3 scripts/24_catalogue_indicators.py
python3 scripts/25_topic_terms.py
python3 scripts/26_build_si.py
```

**From scratch:**

| Step | Script | What it does |
|---|---|---|
| 17 | `17_harvest_corpus.py` | downloads all journal articles of the 13 journals from Crossref to `$EDU01_RUN_OUT/corpus` (default `~/run_out/EDU01`, about 55 MB) |
| 18 | `18_classify_corpus.py` | removes non-research items and classifies titles; writes `data/pool_yearly.csv`, `data/wave_matches.csv`, `data/wave_yearly.csv` (needs step 17; `--sample` would redraw the validation samples — do not use it on the coded files) |
| 19 | `19_openalex_robustness.py` | title+abstract counts from OpenAlex (robustness check) |
| 20 | `20_bib_indicators.py` | research shares, precision/recall, growth windows |
| 21 | `21_make_fig1_v2.py` | Fig. 2 of the manuscript (research trends) |
| 22 | `22_build_bib.py` | rebuilds `manuscript/refs.bib` from Crossref |
| 23 | `23_match_catalogue_v2.py` | finds candidate courses; existing manual codes are kept |
| 24 | `24_catalogue_indicators.py` | coverage (Wilson CI), representation ratio (bootstrap), Figs. 3–4 |
| 25 | `25_topic_terms.py` | topic groups of recent research titles (input to module design) |
| 26 | `26_build_si.py` | Supplementary Tables S1–S10 |

The catalogue scripts in `scripts/catalog_extract/` were run on 2 November 2026;
they write raw pages to `raw/` and CSVs to `data/catalog_v2/`. Two of them
(Purdue, Cornell) use headless Google Chrome. Live catalogues change, so
re-running them gives the current, not the November 2026, state.

## Data files

| File | Content |
|---|---|
| `corpus_titles.csv.gz` | DOI, year, journal and title of all 167,269 harvested records (before removal of non-research items) |
| `wave_definitions_v2.json` | final classification rules, non-research filter, and revision log |
| `validation_precision.csv`, `validation_nearmiss.csv` | round-3 (held-out) validation samples, manually coded |
| `validation_round2_*.csv`, `validation_precision_round1_uncoded.csv` | earlier rounds used to refine the rules |
| `wave_matches.csv`, `pool_yearly.csv`, `wave_yearly.csv` | classified articles and yearly counts |
| `bib_summary.csv`, `bib_windows.csv`, `openalex_title_abstract_yearly.csv` | research-side indicators |
| `course_candidates.csv` | all 170 candidate courses with manual code and justification |
| `coverage_by_programme.csv`, `coverage_summary.csv` | teaching-side indicators |
| `topic_terms.csv` | topic groups in 2021–2025 titles |

## Requirements

Python ≥ 3.10 with `requests`, `numpy`, `scipy`, `matplotlib`; Google Chrome
only for two catalogue scripts; a TeX distribution with `IEEEtran` to compile
the manuscript sources.

## Licence

Code: MIT (`LICENSE`). Data compiled by the author: CC BY 4.0 (`LICENSE-DATA`).
Article metadata come from Crossref and OpenAlex. Course titles and descriptions
are quoted from the public catalogues of the respective universities for
research purposes and remain the property of those institutions.
