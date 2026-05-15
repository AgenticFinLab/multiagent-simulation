# Proactive Search Pipeline

## Purpose

This file specifies the **proactive search pipeline** — a systematic, configuration-driven method for discovering papers you don't yet know exist. Reactive search (finding papers you already know about) always leaves blind spots. This pipeline closes them.

**Core principle**: The user fills `00-user-define.md` once. Everything in this file is **automatically derived** from that configuration — no manual conference lists, no manual keyword lists.

**Venue Policy**: Only papers from **CCF-A conferences** or **recognized top non-ranked venues** (COLM, TMLR, CoRL, etc.). Papers from CCF-B/C or below require explicit justification.

---

## §1 Configuration Parsing (Stage 0)

### Why This Comes First

All subsequent stages depend on structured keywords and classified research communities derived from `00-user-define.md`. Skipping this stage means searching blindly.

### What to Extract from Each Field

| Field # | Source Field               | What to Extract                                 | Used For                              |
|---------|----------------------------|-------------------------------------------------|---------------------------------------|
| 1       | Research Area              | Domain classification, community identification | Venue derivation, arXiv categories    |
| 2       | Research Target            | Problem description, goal statement             | Domain keywords, relevance criteria   |
| 3       | Research Direction         | Specific angle or goal                          | Relevance scoring                     |
| 4       | Main Motivation            | Gap in existing work, prior limitations         | Motivation keywords (G1–Gn)           |
| 5       | Main Idea                  | Key insight, central claim                      | Method keywords (M1–Mn)               |
| 6       | Key Methods                | Named algorithms, architectures                 | Method keywords; taxonomy Categories  |
| 7       | Comparison Dimensions      | Evaluation axes                                 | Relationship table columns            |
| 8       | Search Scope Summary       | Broader search direction                        | Domain keywords (D1–Dn); seed queries |
| 9       | Primary Research Community | Which CCF-A venues to target                    | Venue selection                       |
| 10      | Year Range                 | Time window                                     | All venue×year combinations           |

### Extraction Protocol

```
Step 1: Read all 10 fields in 00-user-define.md

Step 2: Extract DOMAIN KEYWORDS (D1–Dn)
  - From: Research Area + Search Scope Summary + Research Target
  - Nouns and noun phrases describing the application domain
  - Include: synonyms, sub-fields, related domains, abbreviations
  - Example: Research Area = "LLM-based simulation of financial markets"
    → D1: financial market, stock market, market simulation
    → D2: society simulation, social simulation, agent-based society
    → D3: economic behavior, behavioral economics, market microstructure
  - Minimum 3, maximum 8

Step 3: Extract METHOD KEYWORDS (M1–Mn)
  - From: Main Idea + Key Methods
  - Named methods, algorithms, model architectures
  - Include: abbreviations, full names, related techniques, hyphen variants
  - Example: Key Methods = "LLM-based multi-agent systems"
    → M1: LLM, large language model, language model
    → M2: multi-agent, multiagent, MAS, agent-based model, ABM
    → M3: generative agent, LLM agent, AI agent
  - Minimum 3, maximum 8

Step 4: Extract MOTIVATION KEYWORDS (G1–Gn)
  - From: Main Motivation
  - Problem statements, limitations, gap terms
  - These catch papers about the same PROBLEM regardless of method
  - Example: Motivation = "rule-based agents cannot capture behavioral complexity"
    → G1: realistic behavior, emergent behavior, behavioral realism
    → G2: rule-based limitations, behavioral complexity, human-like agents
  - Minimum 2

Step 5: Extract COMPARISON DIMENSIONS
  - Directly from field 7 (Comparison Dimensions)
  - These become the column names in "Relationship to Our Work" tables

Step 6: Classify RESEARCH COMMUNITY
  - From field 9 (Primary Research Community) + derived from fields 1, 6
  - Determine: which CCF-A venues, which arXiv categories, which tiers apply
```

### Extraction Output (write to `00-user-define.md` Parsed section)

```
## Parsed Search Configuration

### Research Community Classification
- Primary field:    [e.g., "AI/ML + Multi-Agent Systems"]
- Secondary fields: [e.g., "Economics/Finance"]
- arXiv categories: [e.g., "cs.MA, cs.AI, q-fin.GN"]

### Domain Keywords (D1–Dn)
D1: [primary domain term, synonym1, synonym2, abbreviation]
D2: [secondary domain term, synonym1, synonym2]
D3: [tertiary domain term, synonym1, synonym2]
...

### Method Keywords (M1–Mn)
M1: [primary method term, synonym1, synonym2, abbreviation]
M2: [secondary method term, synonym1, synonym2]
M3: [tertiary method term, synonym1, synonym2]
...

### Motivation Keywords (G1–Gn)
G1: [gap/limitation term, related phrase]
G2: [gap/limitation term, related phrase]
...

### Comparison Dimensions (for Relationship tables)
- [Dimension 1 from field 7]
- [Dimension 2 from field 7]
...

### Selected Venues (CCF-A + Recognized Top)
| # | Venue | Tier | Community | Years | Rationale |
|---|-------|------|-----------|-------|-----------|
| 1 | ...   | ...  | ...       | ...   | ...       |
```

---

## §2 Venue Selection — CCF-A + Recognized Top Venues ONLY

### CCF-A Conference Registry

Select venues based on **Primary Research Community** (field 9 of `00-user-define.md`):

| Community             | CCF-A Conferences                    | Recognized Top Non-Ranked |
|-----------------------|--------------------------------------|---------------------------|
| AI/ML (general)       | NeurIPS, ICML, ICLR, AAAI, IJCAI     | COLM, TMLR                |
| NLP / Language        | ACL, EMNLP                           | COLM, TMLR                |
| Computer Vision       | CVPR, ICCV, ECCV                     | —                         |
| Multi-Agent Systems   | AAMAS                                | —                         |
| Robotics              | ICRA, IROS                           | CoRL                      |
| Systems / DB          | OSDI, SOSP, SIGMOD, VLDB             | —                         |
| Security / Privacy    | IEEE S&P, CCS, USENIX Security, NDSS | —                         |
| HCI                   | CHI                                  | —                         |
| Theoretical CS        | STOC, FOCS, SODA                     | —                         |
| Information Retrieval | SIGIR, WWW                           | —                         |
| Software Engineering  | ICSE, FSE                            | —                         |
| Data Mining           | KDD                                  | —                         |
| Economics / Finance   | (no formal CCF-A)                    | ICAIF, ESA, CESC          |
| Social Simulation     | AAMAS                                | JASSS, WSC                |

### Venue Selection Rules

```
Given: Primary Research Community from 00-user-define.md field 9

Rule 1: Select ALL CCF-A conferences in the primary community
Rule 2: Add recognized non-ranked top venues relevant to the community
Rule 3: If cross-domain (e.g., AI + Finance), include CCF-A from BOTH
Rule 4: If Research Area involves language modeling, ADD COLM and TMLR
Rule 5: Year range from field 10 applies to ALL selected venues
Rule 6: Workshops at Tier 1 venues MUST be scanned (see §5)
```

### Venue Output Template

```
## Selected Venues for {{Research Target}}

| #   | Venue   | Tier  | Community | Years     | Rationale                   |
|-----|---------|-------|-----------|-----------|-----------------------------|
| 1   | NeurIPS | CCF-A | AI/ML     | 2022–2026 | Primary ML venue            |
| 2   | ICML    | CCF-A | AI/ML     | 2022–2026 | Primary ML venue            |
| 3   | ICLR    | CCF-A | AI/ML     | 2022–2026 | Primary ML venue (OpenRev.) |
| 4   | AAMAS   | CCF-A | MAS       | 2022–2026 | Primary multi-agent venue   |
| 5   | COLM    | Top   | LM        | 2024–2026 | Top language modeling venue |
| 6   | TMLR    | Top   | ML        | 2022–2026 | High-quality ML journal     |
| ... | ...     | ...   | ...       | ...       | ...                         |
```

**Minimum**: 4 venues. **Typical**: 6–8 venues. **Maximum**: 12 venues.

---

## §3 Keyword Matrix Construction (Stage 2)

### Cross-Product Generation

Generate ALL D_i × M_j combinations from the extracted keywords. **No combination may be skipped.**

```
| Combo | Query String                           |
|-------|----------------------------------------|
| D1×M1 | "D1" AND "M1" OR "D1_syn" AND "M1_syn" |
| D1×M2 | "D1" AND "M2" OR "D1_syn" AND "M2_syn" |
| D1×M3 | "D1" AND "M3" OR "D1_syn" AND "M3_syn" |
| D2×M1 | "D2" AND "M1" OR "D2_syn" AND "M1_syn" |
| D2×M2 | "D2" AND "M2" OR "D2_syn" AND "M2_syn" |
| ...   | ...                                    |
```

### Motivation-Based Queries

```
| Combo | Query String                                 |
|-------|----------------------------------------------|
| G1×M1 | "G1" AND "M1" — gap1 addressed using method1 |
| G1×M2 | "G1" AND "M2" — gap1 addressed using method2 |
| G2×M1 | "G2" AND "M1" — gap2 addressed using method1 |
| ...   | ...                                          |
```

### Total Query Count

```
Total = |D| × |M| + |G| × |M|
Minimum: 3×3 + 2×3 = 15 queries
Typical: 5×5 + 3×5 = 40 queries
Maximum: 8×8 + 4×8 = 96 queries
```

### Keyword Matrix Rules

1. **Exhaustive cross-product**: Search every D×M combination — no skipping
2. **Include synonyms**: Always OR together synonyms
3. **Include hyphen variants**: "multi-agent" OR "multiagent"
4. **Include abbreviation expansions**: "ABM" OR "agent-based model"
5. **Include variant spellings**: "modeling" OR "modelling"
6. **Dynamic matrix**: If you discover a new keyword during reading, add it and re-search
7. **Search title AND abstract**: Title-only misses many relevant papers

---

## §4 Search URL Registry

### Academic Search Platforms

| Platform             | URL Template                                                                                                                                                     | Coverage                   |
|----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------|
| Semantic Scholar API | `https://api.semanticscholar.org/graph/v1/paper/search?query=KEYWORDS&venue=VENUE&year=START-END&limit=100&fields=title,authors,abstract,venue,year,externalIds` | All CS, includes abstracts |
| Semantic Scholar Web | `https://www.semanticscholar.org/search?q=KEYWORDS&year%5B0%5D=START&year%5B1%5D=END`                                                                            | Web interface              |
| DBLP API             | `https://dblp.org/search/publ/api?q=KEYWORDS&format=json&h=1000`                                                                                                 | All CS proceedings         |
| DBLP Browse          | `https://dblp.org/db/conf/VENUE/index.html`                                                                                                                      | Browse proceedings         |
| Google Scholar       | `https://scholar.google.com/scholar?q=KEYWORDS&as_ylo=START&as_yhi=END`                                                                                          | Broadest coverage          |
| arXiv Search         | `https://arxiv.org/search/?query=KEYWORDS&searchtype=all`                                                                                                        | Preprints                  |
| arXiv API            | `http://export.arxiv.org/api/query?search_query=all:KEYWORDS&start=0&max_results=100`                                                                            | Programmatic               |

### Venue-Specific Proceedings URLs

| Venue          | URL                                                       | Format               |
|----------------|-----------------------------------------------------------|----------------------|
| NeurIPS        | `https://papers.nips.cc/`                                 | Official proceedings |
| ICML           | `https://proceedings.mlr.press/`                          | Official proceedings |
| ICLR           | `https://openreview.net/group?id=ICLR.cc/YEAR/Conference` | OpenReview           |
| AAAI           | `https://ojs.aaai.org/index.php/AAAI/issue/archive`       | Official archive     |
| ACL / EMNLP    | `https://aclanthology.org/`                               | ACL Anthology        |
| CVPR/ICCV/ECCV | `https://dblp.org/db/conf/cvpr/index.html`                | DBLP                 |
| COLM           | `https://openreview.net/group?id=COLM.cc/YEAR/Conference` | OpenReview           |
| AAMAS          | `https://dblp.org/db/conf/atal/index.html`                | DBLP                 |

### Cross-Reference Tools

| Tool                        | URL                                                                                          | Use For            |
|-----------------------------|----------------------------------------------------------------------------------------------|--------------------|
| Google Scholar Cited By     | `https://scholar.google.com/scholar?cites=PAPER_ID`                                          | Find citing papers |
| Semantic Scholar Citations  | `https://api.semanticscholar.org/graph/v1/paper/PAPER_ID/citations?fields=title,venue,year`  | Citation graph     |
| Semantic Scholar References | `https://api.semanticscholar.org/graph/v1/paper/PAPER_ID/references?fields=title,venue,year` | Reference graph    |

---

## §5 Proceedings Search Protocol (Stage 3)

For each (Conference × Year) in the selected venues:

```
Step 1: Access proceedings
  - Use venue-specific URL from §4
  - Fallback: DBLP https://dblp.org/db/conf/[conf]/index.html

Step 2: Scan by keyword matrix
  - CCF-A primary venues: scan ALL paper titles and abstracts
  - CCF-A secondary / recognized top: filter by keyword matrix first

Step 3: Read abstracts of keyword-matching papers
  - RELEVANT: immediately add to Candidate Paper List
  - POSSIBLY_RELEVANT: read introduction before deciding
  - NOT_RELEVANT: skip

Step 4: Record in Candidate Paper List (see §8)
  - Set Source = "Phase A: [Venue] [Year]"
  - Set Status = FOUND

Step 5: Update Coverage Tracker (see §7)
```

### Tier-Specific Search Depth

| Venue Type                  | Papers to Scan   | Depth                        | Time Budget            |
|-----------------------------|------------------|------------------------------|------------------------|
| CCF-A (primary community)   | ALL papers       | Title + Abstract             | 1–2 hrs per venue×year |
| CCF-A (secondary community) | Keyword-filtered | Title + Abstract for matches | 30 min per venue×year  |
| Recognized Top (COLM/TMLR)  | ALL papers       | Title + Abstract             | 1 hr per venue×year    |

---

## §6 Venue Verification — Confirm Acceptance for arXiv Preprints

When a paper is found on arXiv without a clear venue, **you MUST verify** whether it was accepted at a CCF-A or recognized top venue before including it.

### Verification Methods

**Method 1: arXiv Comments field**
```
URL: https://arxiv.org/abs/ARXIV_ID

Look for Comments field patterns:
  "Accepted to NeurIPS 2025"
  "Published at ICML 2025"
  "To appear at ICLR 2025"
  "Camera-ready for ACL 2025"
  "Oral presentation at EMNLP 2024"

Programmatic: http://export.arxiv.org/api/query?search_query=id:ARXIV_ID
  → <arxiv:comment> field contains acceptance info
```

**Method 2: OpenReview**
```
URL: https://openreview.net/forum?id=PAPER_ID
- Look for "Accepted" / "Rejected" badge
- ICLR: https://openreview.net/group?id=ICLR.cc/YEAR/Conference
- COLM: https://openreview.net/group?id=COLM.cc/YEAR/Conference
- API: https://api2.openreview.net/notes?content.venueid=ICLR.cc/YEAR/Conference&content.title=TITLE
```

**Method 3: Semantic Scholar venue field**
```
API: https://api.semanticscholar.org/graph/v1/paper/arxiv:ARXIV_ID?fields=venue,publicationVenue
Returns:
  "venue": "NeurIPS"   → confirmed published at a known venue
  "venue": "ArXiv"     → still a preprint only
  "venue": ""          → no venue info
```

**Method 4: DBLP lookup**
```
API: https://dblp.org/search/publ/api?q=PAPER_TITLE&format=json
DBLP only indexes papers that appeared in proceedings or journals.
If found → confirmed published. If not found → likely still a preprint.
```

### Decision Matrix for arXiv Preprints

| arXiv Comment             | Semantic Scholar | DBLP      | Decision                              |
|---------------------------|------------------|-----------|---------------------------------------|
| "Accepted to [CCF-A]"     | Any              | Any       | **KEEP** — confirmed CCF-A            |
| "Under review at [CCF-A]" | Any              | Any       | **DISCARD** — not yet accepted        |
| "Accepted at [CCF-B/C]"   | Any              | Any       | **DISCARD** — wrong tier              |
| No comment                | CCF-A venue      | Found     | **KEEP** — confirmed via DBLP/SS      |
| No comment                | ArXiv / empty    | Not found | **KEEP as TENTATIVE** — revisit later |
| No comment                | CCF-B/C venue    | Found     | **DISCARD** — wrong tier              |

**Tentative papers**: Mark as `TENTATIVE` in the Candidate Paper List. Re-check before writing.

---

## §7 Workshop and Preprint Search (Stages 4–5)

### Why Workshops Are Critical

Workshops are the **#1 source of missed papers**. They contain cutting-edge work that hasn't yet appeared in main proceedings. Standard aggregators frequently miss them entirely.

### Workshop Search Protocol

```
For each Tier 1–2 conference in the selected venues:
  1. Find all workshops: search "[Conference] [Year] workshops"
  2. For each workshop whose topic overlaps with the research area:
     a. Find accepted papers list (workshop website or OpenReview)
     b. Filter by keyword matrix
     c. Read abstracts of filtered papers
     d. Add relevant papers to Candidate Paper List
  3. Pay special attention to:
     - Workshops whose title contains any keyword from the matrix
     - First-year workshops (emerging topics)
     - Workshops organized by prominent researchers in the area
```

### Workshop Discovery Sources

| Source               | URL Pattern                                      | Covers                         |
|----------------------|--------------------------------------------------|--------------------------------|
| OpenReview Workshops | `openreview.net/group?id=[Conf]/[Year]/Workshop` | Supported conference workshops |
| Conference Website   | `[conf][year].github.io/workshops`               | Official workshop lists        |
| DBLP Workshops       | `dblp.org/db/conf/[conf][year]-w`                | Workshop proceedings in DBLP   |
| Google Search        | `"[Conference] [Year] workshop accepted papers"` | General discovery              |

### arXiv Category Selection

Based on Primary Research Community (field 9 of `00-user-define.md`):

| Community         | Primary arXiv Categories | Secondary Categories |
|-------------------|--------------------------|----------------------|
| AI/ML             | cs.AI, cs.LG             | stat.ML              |
| NLP               | cs.CL                    | cs.AI                |
| Computer Vision   | cs.CV                    | cs.AI, cs.LG         |
| Multi-Agent       | cs.MA                    | cs.AI                |
| Robotics          | cs.RO                    | cs.AI                |
| Systems           | cs.DC, cs.DB             | cs.SE                |
| Security          | cs.CR                    | cs.AI                |
| Economics/Finance | q-fin.GN, q-fin.CP       | econ.GN, cs.CE       |
| Social Simulation | cs.MA, cs.AI             | econ.GN, q-fin.*     |
| Theory            | cs.CC, cs.DS             | math.CO              |

**For cross-domain research: combine categories from ALL relevant communities.**

---

## §8 Coverage Tracking and Candidate Paper List

### Coverage Tracker

Initialize before starting. Update after every search session.

```
## Coverage Tracker for {{Research Target}}

### Proceedings Coverage
| Venue   | Year | Total Papers | Scanned | Relevant | Status      |
|---------|------|--------------|---------|----------|-------------|
| NeurIPS | 2026 | ~4000        | 0       | 0        | NOT_STARTED |
| NeurIPS | 2025 | ~4000        | 0       | 0        | NOT_STARTED |
| ICML    | 2025 | ~3000        | 0       | 0        | NOT_STARTED |
| ...     | ...  | ...          | ...     | ...      | ...         |

### Workshop Coverage
| Conference | Workshop        | Year | Papers | Relevant | Status      |
|------------|-----------------|------|--------|----------|-------------|
| NeurIPS    | [Workshop name] | 2025 | ~50    | 0        | NOT_STARTED |
| ...        | ...             | ...  | ...    | ...      | ...         |

### Keyword Matrix Coverage
| Combination | Searched | Papers Found | Status      |
|-------------|----------|--------------|-------------|
| D1×M1       | NO       | 0            | NOT_STARTED |
| D1×M2       | NO       | 0            | NOT_STARTED |
| G1×M1       | NO       | 0            | NOT_STARTED |
| ...         | ...      | ...          | ...         |

### Cross-Reference Coverage
| Seed Paper | References Checked | Citations Checked | Status |
|------------|--------------------|-------------------|--------|
| [none yet] | —                  | —                 | —      |
```

**Status values**: NOT_STARTED → IN_PROGRESS → COMPLETE

**Rule**: A venue is NOT complete until ALL its workshops are also scanned.

### Candidate Paper List

All papers discovered during search go here BEFORE reading (Stage 3):

```
## Candidate Papers for {{Research Target}}

| #   | Title   | Venue   | Year   | Link  | Relevance    | Source      | Status             |
|-----|---------|---------|--------|-------|--------------|-------------|--------------------|
| 1   | [title] | [venue] | [year] | [url] | HIGH/MED/LOW | Phase A/B/C | FOUND/READ/WRITTEN |
| ... |         |         |        |       |              |             |                    |
```

**Status flow**: FOUND → READ (04-reading-extraction.md) → WRITTEN (05-writing-guidelines.md)

**Typical output**: 20–60 candidate papers for a well-defined research area.

---

## §9 Iterative Refinement and Cross-Reference Expansion

### Keyword Expansion Loop

The keyword matrix is NOT static. It grows as you learn:

```
1. Read a paper → discover new term (e.g., "generative agents")
2. Add new term to keyword matrix as D_new or M_new
3. Generate new D×M combinations involving the new term
4. Re-search all venue×year with the new combinations
5. Add newly discovered papers to Candidate Paper List
6. Repeat whenever a new significant term is discovered
```

### Cross-Reference Expansion

```
For each RELEVANT paper found:
  1. Read its "Related Work" section → papers not yet in Candidate List
  2. Check its references → older foundational papers
  3. Check who cites it (Google Scholar "Cited by") → newer papers
  4. Check the authors' other publications → related work by same group
  5. Filter all discovered papers by venue policy (CCF-A only)
  6. Add to Candidate Paper List

Stopping criteria for cross-reference expansion:
  - 3 consecutive papers yield no new candidates
  - All HIGH-relevance papers have been cross-referenced
  - Candidate List exceeds 50 papers
```

### Iterative Search Schedule

| Frequency        | Action                                   | Rationale                      |
|------------------|------------------------------------------|--------------------------------|
| First pass       | Complete all phases (A–D)                | Baseline coverage              |
| After first pass | Re-search with newly discovered keywords | New terms expand search space  |
| Weekly           | Check arXiv new submissions              | Catch new preprints            |
| Monthly          | Re-check proceedings for current year    | Newly accepted papers appear   |
| Quarterly        | Full re-run of gap detection             | Verify no new blind spots      |
| Before writing   | Final verification pass                  | Completeness before submission |

---

## §10 Gap Detection

After each search session, check for these failure modes:

| Gap Type                 | Detection Condition                                  | Fix                                |
|--------------------------|------------------------------------------------------|------------------------------------|
| Zero-paper venue         | Venue in taxonomy has 0 papers in related-work.md    | Not searched — search it now       |
| Year gaps                | Papers from some years but not others for same venue | Fill the missing years             |
| Venue concentration      | >60% of papers from 1–2 venues                       | Search too narrow — expand         |
| Missing workshops        | 0 workshop papers in related-work.md                 | Workshops missed — scan them       |
| Single arXiv category    | All papers from one arXiv category                   | Other categories may be missed     |
| Uncovered keyword combos | Some D×M combinations have 0 results                 | Verify they were actually searched |
| Temporal skew            | All papers from same year                            | Widen year range                   |
| New terms pending        | Discovered new terms but not re-searched             | Add to matrix and re-search        |

### Automated Gap Detection Script

```python
import re
from collections import Counter

with open('docs/related-work.md') as f:
    content = f.read()

venues = re.findall(r'\*\*Venue\*\*:\s*(.+?)\n', content)
years = re.findall(r'\b(20[12]\d)\b', content)

if not venues:
    print("No papers with **Venue** field found.")
else:
    print(f"Total papers with venue: {len(venues)}")
    print(f"Year range: {min(years)}-{max(years)}")
    print(f"Year distribution: {sorted(set(years))}")
    venue_counts = Counter(venues)
    for venue, count in venue_counts.most_common():
        pct = count / len(venues) * 100
        flag = " ← CONCENTRATED (>30%)" if pct > 30 else ""
        print(f"  {venue}: {count} ({pct:.0f}%){flag}")
    print("\nCompare against expected venues from §2 to identify coverage gaps.")
```

---

## §11 Parallel Agent Deployment

### Agent Template: Conference Proceedings Scan

```
You are a literature search agent. Scan [CONFERENCE] [YEAR] proceedings
for papers related to: {{Research Area from 00-user-define.md}}

Search keywords: {{Keyword Matrix from §3}}

Step 1: Go to [VENUE_URL] and find the full list of accepted papers.
Step 2: For each paper, check title or abstract for ANY search keyword.
Step 3: For matches, read their abstracts.
Step 4: Return ALL relevant papers with:
  - Exact title
  - Authors (first 2-3)
  - Link (arxiv or conference page)
  - 2-sentence relevance summary
  - Relevance: HIGH / MEDIUM / LOW

IMPORTANT: Only include CCF-A or recognized top venues.
Be exhaustive. Return ALL matches, not just top ones.
```

### Agent Template: Workshop Scan

```
You are a literature search agent. Find ALL workshops at [CONFERENCE] [YEAR]
related to: {{Research Area from 00-user-define.md}}

Keywords: {{Keyword Matrix from §3}}

Step 1: Search "[CONFERENCE] [YEAR] workshops" — find the full workshop list.
Step 2: For each workshop whose topic overlaps with the research area:
  a. Find the accepted papers list (workshop website or OpenReview)
  b. Read titles and abstracts, filter by keywords
  c. Note relevant papers
Step 3: Return:
  - Workshop name and URL
  - Relevant papers (title, authors, link, relevance level)
  - Total papers in workshop vs. relevant found
```

### Agent Template: Keyword Combination Scan

```
You are a literature search agent. Search for papers matching: "[D_i] [M_j]"

Search on ALL of these sources:
1. Semantic Scholar: https://www.semanticscholar.org/search?q=D_i+M_j
2. Google Scholar: https://scholar.google.com/scholar?q=D_i+M_j
3. arXiv: https://arxiv.org/search/?query=D_i+M_j&searchtype=all
4. DBLP: https://dblp.org/search/publ/api?q=D_i+M_j

For each paper: title, authors, link, venue, year, 1-sentence relevance, level.
IMPORTANT: Only include papers from: {{CCF-A venue list from §2}}
Deduplicate across sources.
```

### Parallel Deployment Strategy

```
# Phase A: Main proceedings scan (4–6 agents in parallel)
Agent 1: Scan {{TIER1_VENUE_1}} {{CURRENT_YEAR}}
Agent 2: Scan {{TIER1_VENUE_1}} {{CURRENT_YEAR-1}}
Agent 3: Scan {{TIER1_VENUE_2}} {{CURRENT_YEAR}}
Agent 4: Scan {{TIER1_VENUE_3}} {{CURRENT_YEAR}}
Agent 5: Scan {{TIER1_VENUE_4}} {{CURRENT_YEAR}}
Agent 6: Scan {{TIER1_VENUE_5}} {{CURRENT_YEAR}}

# Phase B: Workshop scan (4–6 agents in parallel, after Phase A)
Agent 1: Scan {{TIER1_VENUE_1}} {{CURRENT_YEAR}} workshops
Agent 2: Scan {{TIER1_VENUE_2}} {{CURRENT_YEAR}} workshops
Agent 3: Scan {{TIER1_VENUE_3}} {{CURRENT_YEAR}} workshops
Agent 4: Scan {{TIER1_VENUE_4}} {{CURRENT_YEAR}} workshops

# Phase C: Keyword combination scan (parallel with Phase B)
Agent 1: Search D1×M1 through D1×Mn on Semantic Scholar
Agent 2: Search D2×M1 through D2×Mn on Semantic Scholar
Agent 3: Search D3×M1 through D4×Mn on Google Scholar
Agent 4: Search G1×M1 through Gn×Mn on arXiv
```

After all agents complete: merge results, deduplicate, update Coverage Tracker, add new papers to `related-work.md`.

---

## §12 End-to-End Search Execution Checklist

Run at the START of every related-work session:

- [ ] **`00-user-define.md` is filled**: All 10 fields completed
- [ ] **Configuration parsed**: D/M/G keywords extracted, communities classified (§1)
- [ ] **Venues selected**: CCF-A + recognized top, with year ranges (§2)
- [ ] **Keyword matrix built**: All D×M and G×M combinations enumerated (§3)
- [ ] **Coverage tracker initialized**: All venue×year and keyword combinations tracked (§8)
- [ ] **Agent templates prepared**: Filled with values from `00-user-define.md`
- [ ] **All Phase A complete**: Every Tier 1 venue×year scanned
- [ ] **All Phase B complete**: Every workshop at Tier 1–2 conferences scanned
- [ ] **All Phase C complete**: Every D×M and G×M keyword combination searched
- [ ] **arXiv categories scanned**: All auto-derived categories checked
- [ ] **Cross-reference expansion done**: Related Work and citations of RELEVANT papers checked (§9)
- [ ] **Keyword expansion loop completed**: New terms added and re-searched (§9)
- [ ] **Venue verification done**: All arXiv preprints checked for CCF-A acceptance (§6)
- [ ] **Gap detection passed**: No zero-paper venues, no year gaps, no concentration >60% (§10)
- [ ] **Candidate Paper List finalized**: At least 15 papers, all from CCF-A/top venues

**Rule of thumb**: If you haven't searched at least 5 conferences × 3 years = 15 venue×year combinations, your search is almost certainly incomplete.
