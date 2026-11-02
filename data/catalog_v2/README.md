# Course-catalogue dataset v2 (26 ECE/EE programmes): method note

Retrieval: all sources fetched on 2026-11-02 (UTC). The per-row timestamp is in `retrieved_utc`.
Raw files (HTML, JSON, PDF and headless-Chrome DOM dumps), one folder per programme, each with a `_fetch_log.tsv`: `~/run_out/EDU01/catalog_v2_raw/<slug>/`.
Extraction scripts: `~/run_out/EDU01/catalog_v2_raw/_scripts/` (shared helper `catv2.py`, plus one script per programme).

## Principles

1. **No imputation.** Every row was parsed from a saved source document. When a source gives no description, credits or code, the field is left empty. We did not translate, paraphrase or infer anything.
   - As a check, every title in every CSV was matched against the saved raw files for that programme. All titles were found; the only mismatches were Unicode-escape differences in the TU Delft JSON.
2. **Unreachable is not zero.** Any programme or part of a programme that could not be obtained is marked `partial` in `coverage_audit.csv`, with the reason. Analyses should treat missing parts as missing data, not as absence of a topic.
3. **Level comes from the institution's own convention.** Each row's `level_rule` records the rule that was applied. In order of preference, we used:
   - a per-course field (MIT U/G tag, Stanford `academicCareer`, Imperial FHEQ level, KTH cycle, METU "Level of Study");
   - membership in a UG or graduate catalogue, study plan or section (TAMU, Georgia Tech, UMD, KAIST, HKUST, ETH, EPFL, TU Delft, NTU, Boğaziçi);
   - the institution's published numbering rule (UIUC, UCSD, Purdue, UT Austin, Cornell, NUS, CMU).

   Where no rule is published, the numbering convention was used and labelled as such (Bilkent, part of METU, Tsinghua UG/G).
4. **Level codes.**
   - `UG/G` is used only where the institution itself designates a course as both. Examples: UIUC 400-level ("upper level undergraduate and graduate"), UMD 400-level listed in both catalogues, Purdue 50000-level "dual-level", and courses listed in both the BSc and MSc sections at ETH, NTU or Cambridge Group S.
   - For integrated UK MEng programmes, the final-year modules are coded `G` because the institution treats them as Masters level:
     - Imperial uses the per-module FHEQ level 7.
     - Oxford Part C is an "integrated Masters taught to FHEQ Level 7", and students leaving before Part C receive a BA.
     - Cambridge Part IIB honours entitles a student to the MEng.
   - The Oxford and Cambridge rows can be recoded to UG by selecting on their `level_rule` text.
5. **Scope.** The dataset covers department-owned courses only, including cross-listed courses that carry the department code.
   - Special topics, seminars, thesis and research credits are included as published, so filter them if the analysis needs taught content only.
   - European and Asian programmes that publish study plans are represented by the EE programme's module list, which can include service courses such as mathematics and physics.

CSV columns: `university, code, title, description, level, level_rule, credits, source_url, retrieved_utc`. Where a row combines two sources, both URLs are joined with ` ; `.

## Per-programme notes

### United States

**MIT (`mit`)**
- Source: all Course 6 (EECS) subjects at https://catalog.mit.edu/subjects/6/, the current Bulletin. No edition year is printed on the page.
- Level: the U or G tag in each subject's level line.
- Joint subjects that only say "see description under …" take the master subject's description, and both URLs are recorded.
- Includes 119 6.S special-subject shells.

**Georgia Tech (`gatech`)**
- Source: 2026-27 catalogue, Undergraduate-Level (1000-4999) and Graduate-Level (6000+) ECE course pages. Each page determines the level.
- Transfer-credit placeholders were excluded. Special-topics shells have no description.

**UIUC (`uiuc`)**
- Source: 2026-27 catalogue. Level follows the catalogue's numbering statement:
  - 100-399: UG
  - 400-499: "upper level undergraduate and graduate", coded UG/G
  - 500+: G
- Descriptions for cross-listed courses come from the owning department's entry.

**UMD (`umd`)**
- Source: 2026-27 undergraduate approved-courses and graduate ENEE lists.
- Level: a course on both lists is UG/G. This matches UMD's rule that 400-level courses are "acceptable for credit toward some graduate degrees".

**UCSD (`ucsd`)**
- Source: General Catalog 2026-27.
- Level: courses numbered 1-199 (lower and upper division) are UG; 200-299 are G, per the catalogue's numbering rule.

**Purdue (`purdue`)**
- Source: Acalog 2026-27 catalogue (catoid 19), prefix ECE. Pages were rendered with headless Chrome because plain requests return HTTP 202 with an empty body.
- Level follows Purdue's Course Numbering Information:
  - below 50000: UG
  - 50000-59999 ("dual-level"): UG/G
  - 60000+: G

**UT Austin (`utaustin`)**
- Source: 2026-27 General Information Catalog, ECE A-to-Z page. The CourseLeaf search API returns the same 333 courses.
- Level follows UT's course-number rule (second and third digits 01-19 lower-division, 20-79 upper-division, 80-99 graduate).
- 170 rows are graduate topic sub-numbers (e.g. "ECE X80L.11"), leaving 163 base courses.
- No credits are available, because the catalogue prints "X" in place of the credit digit.

**Stanford (`stanford`)**
- Source: ExploreCourses XML API, subject EE, AY2026-27.
- Level: the `academicCareer` field (UG or GR). Many 100-299 courses are open to both levels, but each record carries a single career, so none are coded UG/G.

**Cornell (`cornell`)**
- Source: Courses of Study 2026-27, ECE subject (headless Chrome).
- Completeness check: the Class Roster API for FA25, SP26 and FA26 found one roster-only course, which was added.
- Level follows Cornell's course-numbering table: 1000-4999 UG; 5000+ G. The 5000 level is "graduate and professional" (MEng) and accounts for 65 courses.

**Texas A&M (`tamu`)**
- Source: 2026-27 Undergraduate and Graduate & Professional catalogues, ECEN course descriptions.
- Level: which catalogue lists the course.

**CMU (`cmu`)**
- Source: ECE department course list (https://courses.ece.cmu.edu/) and the course pages, plus the 2026-27 undergraduate catalogue.
- Inclusion: the department list goes back to 2004, so only courses offered in AY2022-23 or later, or present in the 2026-27 catalogue, were kept. The full list with offering history is in the raw folder.
- Level: the department's Undergraduate (≤18-5xx) and Graduate (18-6xx+) sections.
- Campus duplicates (Silicon Valley, Rwanda) of Pittsburgh courses were removed.

### Europe

**Cambridge (`cambridge`): partial**
- Sources:
  - Module list for Engineering Tripos Parts IIA and IIB 2025-26: University Reporter No. 6788.
  - Parts IA and IB at examination-paper level: Statutes & Ordinances 2025, Engineering Tripos regulations.
- No descriptions: the Department's teaching site (teaching.eng.cam.ac.uk) is behind a university login.
- Level: IA, IB and IIA are UG; IIB is G; Group S modules shared between IIA and IIB are UG/G.
- Electrical and information modules are the 3B*, 3F*, 4B* and 4F* codes.

**Imperial (`imperial`)**
- Source: EEE module catalogue 2026-27 (Years 1-4 EEE/EIE and MSc) plus module-specification PDFs.
- Level: the FHEQ level printed in each specification (4-6 UG, 7 G).
- 34 modules have no parsable specification. Their level was taken from the code's level digit, as stated in `level_rule`.

**Oxford (`oxford`)**
- Source: Engineering Science Prelims and FHS handbooks 2026-27, and the 3rd- and 4th-year syllabi 2025-26 (PDF). The unit is the examination paper.
- No descriptions for Part A (A1-A5): the year-2 syllabus is only on Canvas, which needs a login.
- The department has no taught EE MSc. The old admissions URL returned HTTP 403.

**TU Delft (`tudelft`)**
- Source: the public JSON API behind the study guide (curriculum.tudelft.nl), academic year 2025-26. The 2026-27 data was still incomplete when retrieved.
- Level: BSc Electrical Engineering courses are UG; MSc Electrical Engineering courses are G.

**KTH (`kth`)**
- Source: KTH course-catalogue pages for the EECS Department of Electrical Engineering (JJ and sub-units) and the electrical divisions JRL, JRO and JRQ. The Kopps API has been retired (HTTP 404).
- Level: first cycle is UG; second and third cycle are G. The 158 third-cycle (PhD) courses can be identified by their `level_rule` text.

**ETH Zürich (`eth`)**
- Source: VVZ, HS25 and FS26, "Catalogue data" for the BSc EEIT, MSc EEIT and Doctorate ITET sections (D-ITET is deptId 18).
- Level: the programme section. A course listed in both the BSc and an MSc or Doctorate section is UG/G.

**EPFL (`epfl`)**
- Source: 2026-27 EE study plans (propaedeutic, bachelor, master) and coursebook pages.
- 44 descriptions are in French, kept verbatim.

### Asia

**NUS (`nus`)**
- Source: NUSMods API, AY2026-27.
- Scope: modules whose department is "Electrical and Computer Engineering", plus CG-prefix modules.
- Level follows the NUS Registrar: course levels 1000-4000 are UG; 5000-6000 are G.

**NTU Singapore (`ntu`): partial**
- UG source: the "Content of Courses" system, which shows only courses offered in the semesters queried (AY2025 S1, S2 and Special Term; AY2026 S1).
- G source: the five EEE MSc curriculum tables. PhD-only EE7xxx courses are not published as a list.
- Level: which list a course appears on. Numbering is not used, because EE5xxx courses are UG electives at NTU.

**KAIST (`kaist`)**
- Source: English Undergraduate and Graduate Subject Lists of the School of EE (undated, current listing).
- Level: which list a course appears on.
- Special-topics offerings with distinct subtitles are separate rows.

**HKUST (`hkust`)**
- Source: prog-crs catalogue 2026-27 — ELEC and CPEG (UG), ELEC and EESM (PG).
- Level: UG versus PG catalogue.

**Tsinghua (`tsinghua`): partial**
- Scope: the Department of Electronic Engineering only.
- UG source: the English undergraduate curriculum page, restricted to courses offered by the department.
- G source: the department's Chinese graduate-course page. It lists 40 course names without codes or credits, while stating that more than 90 graduate courses exist.
- No descriptions are publicly available; university systems need a login.
- 11 UG-curriculum courses with 6/7/8-series codes are coded UG/G by inference from Tsinghua graduate programme documents. No numbering rule is published.
- Chinese names were not translated. As a result, about 10 courses may appear twice: once with an English UG/G title and once with a Chinese G title.

### Türkiye

**METU (`metu`)**
- Course list: the department's "All Courses" page (eee.metu.edu.tr).
- Descriptions and the official "Level of Study" field: 2026 Internet Archive captures of the official catalogue, because catalog.metu.edu.tr timed out from our host.
- 36 rows are levelled by numbering; 34 rows have no description.

**Boğaziçi (`bogazici`)**
- Source: the department's undergraduate and graduate course pages (ee.bogazici.edu.tr). No year is stated on them.
- Level: which page lists the course. Two titles that are only published in Turkish are kept in Turkish.

**Bilkent (`bilkent`)**
- Source: Online Academic Catalog, EEE course list and per-course pages (regenerated 22 Oct 2026).
- Level: numbering convention (1xx-4xx UG, 5xx+ G). No published rule was found.

## Known limitations

- Catalogue listings show courses that are approved, not necessarily taught every year. MIT, Cornell, NUS and CMU flag their non-offered courses differently, and only CMU was filtered by offering history.
- The unit of analysis differs between sources. Cambridge Parts IA/IB and Oxford are recorded at paper level, while UT Austin and KAIST include topic or section variants. Normalise before making count comparisons across programmes, for example by using distinct base codes.
