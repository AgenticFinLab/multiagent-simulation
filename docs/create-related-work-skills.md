# Skill: Comprehensive Related-Work Documentation Writing

## User Configuration (FILL THIS FIRST)

Before using this skill, configure the following parameters for your research project. These values will be referenced throughout the document as template variables.

```
## Research Project Configuration

- **Research Area**: Simulation of Society, including finance behavrios, markets,...., based on the large language models (LLMs) and LLM-based multi-agent systems.
- **Research Target**: Repeat and Duplicate the society events, finance behaviors, etc.. directly to match the feature of the society
- **Main Motivation**: 

- **Main Idea**: Do not have idea yet. I just want to collect all related works in this area

- **Key Techniques**: Do not have technique yet. I just want to collect all related works in this area

- **Comparison Dimensions**: All kinds of simulation or similar research based on the large language models or LLM-based multi-agent systems.

```

> **Note**: Once configured, replace `{{RESEARCH_TARGET}}`, `{{MAIN_MOTIVATION}}`, `{{MAIN_IDEA}}`, and other template variables throughout this document with your actual values.

---

## Overview

This skill describes the complete workflow, methodology, and best practices for comprehensively writing `docs/related-work.md` — a literature review document for ANY research project. The goal is to ensure every paper entry follows a unified, high-quality template with deep, accurate, and well-structured content.

**Key principle**: This skill is **research-agnostic**. Whether you work on computer vision, NLP, robotics, or systems, the same workflow applies. You configure your research context once (see User Configuration above), then follow the systematic process below.

---

## 1. Unified Paper Entry Template

Every paper MUST contain the following 9 components, in order:

### 1.1 Categorization Tags
```
**[CAT: X] [REL: Y]**
```
- **CAT (Category)**: Core | Efficiency | Training | Analysis | Theory
  - Adapt categories to your field (e.g., for vision: Architecture | Optimization | Data | Evaluation)
- **REL (Relevance)**: Critical | High | Medium | Low
  - Critical: Directly addresses the same problem or uses nearly identical methods
  - High: Strong conceptual overlap or complementary technique
  - Medium: Related area with useful insights
  - Low: Peripheral relevance

### 1.2 Paper Metadata
```
**Paper**: "Full Paper Title"
**Authors**: Author Names (if notable)
**Venue**: Conference/Journal Name Year
**Link**: https://arxiv.org/abs/XXXX.XXXXX
**Code**: https://github.com/... (or **Code**: Null)
```

### 1.3 Summary
- **Length**: 3-6 sentences
- **Content**: Overall motivation, core contribution, and key result
- **Style**: Accessible but technically precise; explain what the paper DOES, not just what it CLAIMS

### 1.4 Core Motivation
- **Question**: Why did the authors write this paper? What problem are they solving?
- **Depth**: Explain the gap in existing work, limitations of prior approaches, and why this matters
- **Style**: Start with the problem, not the solution

### 1.5 Core Idea
- **Question**: What is the single most important insight?
- **Format**: Use ASCII code blocks or equations
- **Style**: Express the idea as a transformation, formula, or before/after comparison

### 1.6 Core Method
- **Question**: How do they implement the core idea?
- **Depth**: Step-by-step technical description with architecture details
- **Format**: Use ASCII diagrams, flowcharts, and pseudocode
- **Include**: Input → Process → Output pipeline

### 1.7 Example
- **Requirement**: A concrete, simple, self-contained example
- **Style**: Use a toy problem appropriate for your domain
  - NLP: Math word problems, logic puzzles
  - Vision: Small image classification, object detection on simple scenes
  - Systems: Toy distributed system, small graph processing
  - Theory: Simple proof walkthrough, small-scale demonstration
- **Format**: Show BEFORE (baseline) and AFTER (their method) side by side
- **Goal**: A reader should understand the paper's contribution from this example alone

### 1.8 Key Results (Optional but Recommended)
- Bullet points with quantitative results
- Include numbers, speedups, accuracy improvements

### 1.9 Relationship to Our Work
- **Brief Text**: 1-2 sentences summarizing the relationship
- **Comparison Table**: MUST include a table comparing at least 3 dimensions
  ```
  | Aspect        | Their Work       | Our Work ({{RESEARCH_TARGET}}) |
  |---------------|------------------|--------------------------------|
  | [Dimension 1] | [Their approach] | [Our approach]                 |
  | [Dimension 2] | [Their approach] | [Our approach]                 |
  | [Dimension 3] | [Their approach] | [Our approach]                 |
  ```
  - Use dimensions from your User Configuration (Comparison Dimensions)
  - Be specific and accurate — never vague

---

## 2. Paper Research Workflow

### Phase 1: Discovery and Reading (CRITICAL)

#### Step 1: Access the Paper
1. **Primary Source**: Click the arXiv link directly
2. **Read the Abstract**: Extract core claim and methodology
3. **Read Introduction**: Understand motivation and problem statement
4. **Read Method Section**: Extract technical details, architecture, training procedure
5. **Read Experiments**: Note datasets, metrics, and key results
6. **Read Conclusion**: Confirm contributions and limitations

#### Step 2: Multi-Source Verification
Never rely on a single source. Verify understanding through:
- **GitHub README**: Often has clearer explanations than the paper
- **OpenReview Forums**: For ICLR/NeurIPS papers — contains author responses and reviewer discussions
- **Blog Posts**: Authors sometimes publish accessible summaries
- **Twitter/X Threads**: Quick insights from the community
- **Related Work Sections**: Of subsequent papers that cite this work
- **Citations**: Check who cites this paper and what they say about it

#### Step 3: Deep Technical Reading
For papers marked [REL: Critical] or [REL: High]:
- Read the full method section carefully
- Understand the mathematical formulation
- Trace the data flow through the architecture
- Identify assumptions and limitations
- Note hyperparameters and training details

For papers marked [REL: Medium] or [REL: Low]:
- Abstract + Introduction + Key Figures are usually sufficient
- Focus on extracting the core insight rather than full implementation details

### Phase 2: Content Extraction

After reading, extract the following structured information:

```
Paper: [Title]
Link: [URL]

1. PROBLEM: [1 sentence — what are they solving?]
2. INSIGHT: [1 sentence — what's the key idea?]
3. METHOD: [3-5 sentences — how do they implement it?]
4. RESULT: [1-2 sentences — what did they achieve?]
5. LIMITATIONS: [1 sentence — what doesn't it do?]
6. CONNECTION: [2-3 sentences — how does this relate to our concept pyramid?]
```

### Phase 3: Writing

#### Writing Order
1. Write **Core Motivation** first — this grounds everything
2. Write **Core Idea** second — the central insight
3. Write **Core Method** third — the technical implementation
4. Write **Example** fourth — concretize with a toy problem
5. Write **Summary** last — synthesize the above into a concise overview
6. Write **Relationship to Our Work** — compare systematically

#### Writing Style Guidelines
- **Accuracy over Hype**: Never exaggerate claims. If the paper shows 5% improvement, say 5%, not "significant improvement"
- **Specific over Vague**: Replace "improves performance" with "improves accuracy by 14.1% on GSM8K"
- **Accessible over Jargony**: Explain technical terms when first used
- **Active Voice**: "The authors propose" not "It is proposed that"
- **Consistent Terminology**: Use the same terms across all paper entries

---

## 3. Search and Verification Methodology

### 3.1 Iterative Search Strategy

Search is not a one-time activity. Use an iterative deepening approach:

#### Round 1: Breadth-First Discovery
- Search for the paper title on arXiv, Google Scholar, and Semantic Scholar
- Read abstract and introduction
- Note: year, venue, authors, key claims

#### Round 2: Depth-First Technical Understanding
- Read the full method section
- Extract architecture diagrams and equations
- Understand training procedures and loss functions

#### Round 3: Cross-Validation
- Search for blog posts, Twitter discussions, or video explanations
- Check OpenReview for reviewer questions and author responses
- Look at citing papers to see how the community interprets this work

#### Round 4: Connection Mapping
- Explicitly map the paper's approach to our approach
- Identify: similarities, differences, complementary aspects, limitations we address

### 3.2 Parallel Browser Agent Strategy

When upgrading multiple papers simultaneously, use parallel browser agents:

```
Agent 1: Read Paper A on arXiv → Extract structured content
Agent 2: Read Paper B on arXiv → Extract structured content
Agent 3: Read Paper C GitHub → Extract implementation details
Agent 4: Read Paper D OpenReview → Extract reviewer insights
```

#### Agent Prompt Design for Maximum Yield

The quality of agent output depends heavily on prompt design. Use this structure:

```
Research these N papers and return structured information for each.
I need: exact paper title, arxiv/conference link, core motivation,
core idea, core method, and a concrete simple example.

For each paper, search arxiv, openreview, google scholar.
Return for each:
- Exact title
- Link (arxiv URL or conference page)
- 2-3 sentence core motivation
- 2-3 sentence core idea
- Core method description (with ASCII diagram if possible)
- Concrete simple example (e.g., math word problem)

Be thorough and accurate. Search multiple sources if needed.
```

**Key Prompting Principles**:
- **Explicit output structure**: Tell the agent exactly what fields to return
- **Multi-source mandate**: Require searching arxiv, openreview, AND google scholar
- **ASCII diagram request**: Explicitly ask for visual representations
- **Concrete example requirement**: Specify the example domain (math word problems work best)
- **Accuracy enforcement**: "Be thorough and accurate" reduces hallucination

**Agent Grouping Strategy**:
- Group 3-4 related papers per agent (they share context)
- Group by topic (e.g., all latent reasoning papers together)
- Group by venue/year (e.g., all ICLR 2026 papers together)
- Avoid grouping papers that might confuse each other (e.g., a survey + a specific method)

Each agent returns:
- Core Motivation
- Core Method
- Concrete Example
- Key Results

Then integrate all outputs into the markdown file.

### 3.3 Source Quality Hierarchy

| Priority | Source                      | Reliability | Use For                                    |
|----------|-----------------------------|-------------|--------------------------------------------|
| 1        | arXiv PDF / Official Paper  | Highest     | All technical details                      |
| 2        | GitHub Repository           | High        | Implementation details, code verification  |
| 3        | OpenReview Forum            | High        | Clarifications, limitations, author intent |
| 4        | Author Blog Posts           | Medium      | Accessible explanations, motivation        |
| 5        | Twitter/X Threads           | Medium      | Community interpretation, quick insights   |
| 6        | Citing Papers' Related Work | Medium      | How the field views this work              |
| 7        | Third-Party Summaries       | Low         | Initial orientation only                   |

> **Critical distinction**: Sections 3.1–3.3 are **reactive** — they help you understand papers you already know about. Sections 3.4–3.12 below are **proactive** — they help you DISCOVER papers you don't know exist. The entire proactive pipeline is **configuration-driven**: it reads `## Research Project Configuration` and automatically derives keywords, venues, and search strategies. No manual specification of conferences or keywords is needed — just fill in the configuration.

---

### 3.4 Configuration-Driven Proactive Search Pipeline

The iterative search in 3.1 is reactive — it finds papers you already know about. This section adds a proactive pipeline that **automatically** derives all search parameters from `## Research Project Configuration` and systematically scans every relevant venue to guarantee no paper is missed.

#### Why Reactive-Only Search Fails

| Failure Mode          | Example                                  | Root Cause                        |
|-----------------------|------------------------------------------|-----------------------------------|
| Unknown paper title   | Relevant paper at an unfamiliar venue    | No keyword led to its discovery   |
| Workshop invisibility | Papers at conference workshops           | Aggregators underindex workshops  |
| Cross-domain papers   | Papers at the intersection of two fields | Not in your primary keyword space |
| Recent publications   | This year's papers                       | Indexing delay on Google Scholar  |
| Niche venue papers    | Papers at domain-specific conferences    | You never searched that venue     |

#### Pipeline Overview: From Configuration to Complete Literature

```
┌─────────────────────────────────────────────────────────────────────┐
│ Stage 0: Parse Configuration  → Extract keywords from config fields│
│ Stage 1: Auto-Generate Venues → Derive conference/journal list     │
│ Stage 2: Auto-Generate Matrix → Derive keyword cross-product       │
│ Stage 3: Proceedings Scan     → Scan each venue × year             │
│ Stage 4: Workshop Scan        → Scan workshops (often missed)      │
│ Stage 5: Preprint Scan        → Scan arXiv and recurring alerts    │
│ Stage 6: Coverage Tracking    → Track WHAT has been searched       │
│ Stage 7: Gap Detection        → Find what is STILL missing         │
│ Stage 8: Iterative Refinement → Repeat until coverage is complete  │
└─────────────────────────────────────────────────────────────────────┘
```

**Core principle**: The user ONLY fills in `## Research Project Configuration`. Every subsequent stage is **automatically derived** — no manual conference lists, no manual keyword lists.

---

### 3.5 Configuration Parsing (Stage 0)

This is the most critical stage. The LLM reads the 6 fields in `## Research Project Configuration` and extracts all information needed for the entire search pipeline.

#### What to Extract from Each Configuration Field

| Config Field          | What to Extract                                          | Used For                                         |
|-----------------------|----------------------------------------------------------|--------------------------------------------------|
| Research Area         | Domain classification, research community identification | Conference/journal/auto-derivation               |
| Research Target       | Problem description, goal statement                      | Domain keywords, relevance criteria              |
| Main Motivation       | Gap in existing work, limitations of prior approaches    | Core Motivation matching, motivation keywords    |
| Main Idea             | Key insight, central claim                               | Method keywords, technique identification        |
| Key Techniques        | Named methods, algorithms, architectures                 | Method keywords, cross-product generation        |
| Comparison Dimensions | Evaluation aspects, comparison axes                      | Relationship table dimensions, relevance scoring |

#### Extraction Protocol

```
Step 1: Read all 6 fields in ## Research Project Configuration

Step 2: Extract DOMAIN KEYWORDS
  - From Research Area + Research Target
  - Nouns and noun phrases describing the application domain
  - Include: synonyms, sub-fields, related domains
  - Example: if Research Area = "simulation of society based on LLMs"
    → {society, social, simulation, agent-based, economic, market, ...}

Step 3: Extract METHOD KEYWORDS
  - From Main Idea + Key Techniques
  - Named methods, algorithms, model architectures
  - Include: abbreviations, full names, related techniques
  - Example: if Key Techniques = "LLM-based multi-agent systems"
    → {LLM, large language model, multi-agent, agent-based, MAS, GPT, ...}

Step 4: Extract MOTIVATION KEYWORDS
  - From Main Motivation
  - Problem statements, limitations, gaps
  - Example: if Motivation = "existing simulations lack realistic behavior"
    → {realistic behavior, emergent behavior, behavioral simulation, ...}

Step 5: Extract COMPARISON DIMENSIONS
  - From Comparison Dimensions field
  - These become the columns in every "Relationship to Our Work" table

Step 6: Classify RESEARCH COMMUNITY
  - Based on all extracted information, determine:
    * Which academic communities publish in this area
    * Which arXiv categories are relevant
    * Which conference tiers apply
    * Which journal types are relevant
```

#### Extraction Output Template

After parsing, produce this structured output:

```
## Parsed Search Configuration

### Research Community Classification
- Primary field: [e.g., "AI/ML", "NLP", "Computer Vision", "Multi-Agent Systems"]
- Secondary fields: [e.g., "Economics", "Finance", "Social Science"]
- Research paradigm: [e.g., "empirical", "theoretical", "applied", "systems"]

### Domain Keywords (D1–Dn)
D1: [primary domain term + synonyms]
D2: [secondary domain term + synonyms]
D3: [tertiary domain term + synonyms]
...

### Method Keywords (M1–Mn)
M1: [primary method term + synonyms]
M2: [secondary method term + synonyms]
M3: [tertiary method term + synonyms]
...

### Motivation Keywords
- [gap/limitation term 1]
- [gap/limitation term 2]
...

### Comparison Dimensions (for Relationship tables)
- [Dimension 1 from config]
- [Dimension 2 from config]
- [Dimension 3 from config]
...
```

---

### 3.6 Auto-Generate Venue Taxonomy (Stage 1)

Based on the Research Community Classification from Stage 0, automatically determine which venues to search. Do NOT hardcode venue lists — derive them from the research area.

#### Venue Derivation Guide

For each research community, determine relevant venues using this classification:

| Research Community  | Tier 1 Venues                    | Tier 2 Venues       | Key Workshops                 |
|---------------------|----------------------------------|---------------------|-------------------------------|
| AI/ML (general)     | NeurIPS, ICML, ICLR, AAAI, IJCAI | AISTATS, UAI, EAAMO | Varies by topic               |
| NLP / Language      | ACL, EMNLP, NAACL, NeurIPS       | COLING, EACL, AACL  | Varies by topic               |
| Computer Vision     | CVPR, ICCV, ECCV, NeurIPS        | BMVC, WACV          | Varies by topic               |
| Multi-Agent Systems | AAMAS, NeurIPS, IJCAI, AAAI      | IAT, PRIMA, EUMAS   | Agent workshops at top venues |
| Robotics            | ICRA, IROS, CoRL, RSS            | RoboCup, HRI        | Embodied AI workshops         |
| Systems / DB        | OSDI, SOSP, SIGMOD, VLDB         | ICDE, CIDR, NSDI    | Varies by topic               |
| Security / Privacy  | IEEE S&P, CCS, USENIX, NDSS      | ACSAC, ESORICS      | Varies by topic               |
| HCI                 | CHI, CSCW, UIST, SIGCHI          | IUI, UbiComp        | Varies by topic               |
| Economics / Finance | ESA, CESC, IEEE ICAIF            | AEA, EFA            | FinAI workshops at top venues |
| Social Simulation   | JASSS, AAMAS, WSC                | SpringSim, SSC      | Social simulation workshops   |
| Theory / Algorithms | STOC, FOCS, SODA, ITCS           | ICALP, ESA          | Varies by topic               |

**Rules for cross-domain research:**
1. If the research spans multiple communities, include Tier 1 venues from ALL relevant communities
2. If the research applies AI to a domain (e.g., AI for Finance), include both AI venues AND domain venues
3. Workshops are always derived from the intersection of the research topic and the conference

#### Auto-Generation Protocol

```
Given: Research Community Classification from Stage 0

Step 1: Identify primary community → get Tier 1 venues
Step 2: Identify secondary communities → get Tier 2 venues
Step 3: Identify domain-specific venues → get Tier 3 venues
Step 4: For each Tier 1-2 conference, derive relevant workshops
  - Search: "[Conference] [Year] workshop" + any domain keyword
  - Identify workshops whose topic overlaps with the research area
Step 5: Identify relevant journals
  - Based on the domain: use the community's top journals
Step 6: Determine year range
  - Default: [current year - 4] to [current year]
  - Widen to [current year - 6] for mature fields
  - Narrow to [current year - 2] for rapidly evolving fields

Output: Complete venue taxonomy with Tier 1/2/3 + Workshops + Journals
```

#### Generated Output Template

```
## Venue Taxonomy (auto-generated for {{RESEARCH_AREA}})

### Tier 1 — Core Venues (MUST scan every year, ALL papers)
| Venue          | Focus          | Years        |
|----------------|----------------|--------------|
| [Auto-derived] | [Why relevant] | [Year range] |
...

### Tier 2 — Related Venues (scan with keyword filter)
| Venue          | Focus          | Years        |
|----------------|----------------|--------------|
| [Auto-derived] | [Why relevant] | [Year range] |
...

### Tier 3 — Domain-Specific Venues
| Venue          | Focus          | Years        |
|----------------|----------------|--------------|
| [Auto-derived] | [Why relevant] | [Year range] |
...

### Workshops to Scan
| Conference     | Workshop Pattern | Years        |
|----------------|------------------|--------------|
| [Auto-derived] | [Topic keywords] | [Year range] |
...

### Journals
| Journal        | Focus          | Scan Frequency |
|----------------|----------------|----------------|
| [Auto-derived] | [Why relevant] | Quarterly      |
...
```

---

### 3.7 Auto-Generate Keyword Matrix (Stage 2)

Using the Domain Keywords (D1–Dn) and Method Keywords (M1–Mn) extracted in Stage 0, generate a systematic cross-product. **Every combination must be searched.** This is the single most important step for avoiding missed papers.

#### Keyword Matrix Generation Protocol

```
Given: D1–Dn (domain keywords) and M1–Mn (method keywords) from Stage 0

Step 1: For each D_i, expand synonyms
  - Include: abbreviation expansions, hyphen variants, related terms
  - Example: D_i = "multi-agent" → also include "multiagent", "MAS", "agent-based"

Step 2: For each M_j, expand synonyms
  - Include: abbreviation expansions, full names, related methods
  - Example: M_j = "LLM" → also include "large language model", "language model", "GPT"

Step 3: Generate ALL D_i × M_j combinations
  - Total combinations = |D| × |M|
  - Do NOT skip any combination

Step 4: For each combination, construct search queries
  - Use OR for synonyms: "LLM simulation" OR "large language model simulation"
  - Use quotes for exact phrases when needed

Step 5: Add MOTIVATION-based queries
  - From Motivation Keywords extracted in Stage 0
  - These catch papers about the same PROBLEM even if they use different METHODS
  - Example: "emergent behavior" OR "realistic social simulation"
```

#### Generated Output Template

```
## Keyword Matrix (auto-generated from configuration)

### Domain Keywords
D1: [primary domain term, synonym1, synonym2]
D2: [secondary domain term, synonym1, synonym2]
...

### Method Keywords
M1: [primary method term, synonym1, synonym2]
M2: [secondary method term, synonym1, synonym2]
...

### Cross-Product Search Queries (|D| × |M| combinations)
D1×M1: "[D1] [M1]" OR "[D1_syn] [M1_syn]"
D1×M2: "[D1] [M2]" OR "[D1_syn] [M2_syn]"
D2×M1: "[D2] [M1]" OR "[D2_syn] [M1_syn]"
... (all combinations)

### Motivation-Based Queries
- "[motivation keyword 1]" + "[method keyword]"
- "[motivation keyword 2]" + "[domain keyword]"
...
```

#### Keyword Matrix Rules

1. **Exhaustive cross-product**: Search every D×M combination — no skipping
2. **Include synonyms**: Always OR together synonyms ("LLM" OR "large language model")
3. **Include hyphens and spaces**: "multi-agent" OR "multiagent"
4. **Include abbreviation expansions**: "ABM" OR "agent-based model"
5. **Include variant spellings if applicable**: "modeling" OR "modelling"
6. **Add new terms as they emerge**: If you discover a new keyword during search, add it to the matrix and re-search
7. **Search in title AND abstract**: Keywords in title alone miss many papers

---

### 3.8 Proceedings Search Protocol (Stage 3)

For each (Conference × Year) in the auto-generated venue taxonomy, execute this protocol:

```
Step 1: Access proceedings
  - DBLP: https://dblp.org/db/conf/[conf]/index.html
  - Semantic Scholar API: search by venue + year + keywords
  - Conference website: official accepted papers list
  - OpenReview: for ICLR/NeurIPS/other supported venues

Step 2: Filter by keyword matrix
  - Tier 1 venues: scan ALL paper titles and abstracts
  - Tier 2-3 venues: filter using keyword matrix (at least 1 domain + 1 method keyword)

Step 3: Read abstracts of filtered papers
  - Mark as RELEVANT / POSSIBLY_RELEVANT / NOT_RELEVANT
  - RELEVANT: immediately add to related-work.md as stub or full entry
  - POSSIBLY_RELEVANT: read introduction before deciding

Step 4: Extract structured information for relevant papers
  - Use the Phase 2 extraction template from Section 2

Step 5: Update coverage tracker (Section 3.11)
```

#### API Search Templates

**DBLP Search (generic):**
```
https://dblp.org/search/publ/api?q={{KEYWORD_QUERY}}&venue={{VENUE}}&year={{YEAR}}&format=json&h=1000
```

**Semantic Scholar Search (generic):**
```
https://api.semanticscholar.org/graph/v1/paper/search?query={{KEYWORD_QUERY}}&venue={{VENUE}}&year={{START}}-{{END}}&limit=100&fields=title,authors,abstract,venue,year,externalIds
```

**OpenReview Search (for supported venues):**
```
https://api.openreview.net/notes?content.venue={{VENUE}}+{{YEAR}}+workshop&content.keywords={{KEYWORD}}
```

#### Tier-Specific Search Depth

| Venue Tier | Papers to Scan        | Depth                                 | Time Budget              |
|------------|-----------------------|---------------------------------------|--------------------------|
| Tier 1     | ALL papers            | Title + Abstract                      | 1-2 hours per venue×year |
| Tier 2     | Keyword-filtered only | Title + Abstract for matches          | 30 min per venue×year    |
| Tier 3     | Keyword-filtered only | Title only, then abstract for matches | 15 min per venue×year    |

---

### 3.9 Workshop and Preprint Search (Stages 4–5)

Workshops are the **#1 source of missed papers**. They often contain the most cutting-edge work that hasn't yet made it to main conference proceedings. Standard aggregator searches frequently miss workshop papers entirely.

#### Workshop Search Protocol

```
For each Tier 1-2 conference in the auto-generated venue taxonomy:
  1. Find all workshops: search "[Conference] [Year] workshops"
  2. For each workshop:
     a. Find accepted papers list (workshop website or OpenReview)
     b. Filter by keyword matrix
     c. Read abstracts of filtered papers
     d. Add relevant papers to related-work.md
  3. Pay special attention to:
     - Workshops whose title contains any keyword from the matrix
     - First-year workshops (emerging topics)
     - Workshops organized by prominent researchers in the research area
```

#### Workshop Discovery Sources

| Source               | URL Pattern                                    | Covers                               |
|----------------------|------------------------------------------------|--------------------------------------|
| OpenReview Workshops | openreview.net/group?id=[Conf]/[Year]/Workshop | Supported conference workshops       |
| Conference Website   | [conf][year].github.io/workshops               | Official workshop lists              |
| DBLP Workshops       | dblp.org/db/conf/[conf][year]-w                | Workshop proceedings indexed by DBLP |
| Google Search        | "[Conference] [Year] workshop accepted papers" | General discovery                    |

#### Preprint Search Protocol

arXiv categories are **auto-derived** from the Research Community Classification:

| Research Community | Primary arXiv Categories | Secondary Categories |
|--------------------|--------------------------|----------------------|
| AI/ML              | cs.AI, cs.LG             | stat.ML              |
| NLP                | cs.CL                    | cs.AI                |
| Computer Vision    | cs.CV                    | cs.AI, cs.LG         |
| Multi-Agent        | cs.MA                    | cs.AI, cs.MAS        |
| Robotics           | cs.RO                    | cs.AI                |
| Systems            | cs.DC, cs.DB             | cs.SE                |
| Security           | cs.CR                    | cs.AI                |
| Economics/Finance  | q-fin.GN, q-fin.CP       | econ.GN, cs.CE       |
| Social Simulation  | cs.MA, cs.AI             | econ.GN, q-fin.*     |
| Theory             | cs.CC, cs.DS             | math.CO              |

**For cross-domain research, combine categories from ALL relevant communities.**

```
1. arXiv periodic scan:
   - For each auto-derived arXiv category:
     * Search: https://arxiv.org/list/[category]/recent
     * Filter by keyword matrix
   - Also search arXiv broadly: https://arxiv.org/search/?query={{KEYWORD_QUERY}}

2. Recurring alerts:
   - Google Scholar alerts for top 5 keyword combinations
   - Semantic Scholar topic feed
   - arXiv daily/weekly digest for primary categories

3. Community monitoring:
   - Twitter/X lists of key researchers in the area
   - Reddit communities relevant to the research area
   - Papers With Code: track relevant benchmark leaderboards
```

---

### 3.10 Iterative Refinement and Re-Search (Stage 8)

Search is NEVER a one-time activity. Even after a complete pass, new papers appear and previously undiscovered connections emerge.

#### Iterative Search Schedule

| Frequency        | Action                                        | Rationale                                              |
|------------------|-----------------------------------------------|--------------------------------------------------------|
| First pass       | Complete Stages 0-7                           | Baseline coverage                                      |
| After first pass | Re-search with DISCOVERED keywords            | New terms found during reading expand the search space |
| Weekly           | Check arXiv new submissions                   | Catch new preprints                                    |
| Monthly          | Re-check conference proceedings for this year | Newly accepted papers appear                           |
| Quarterly        | Full re-run of gap detection                  | Verify no new blind spots                              |
| Before writing   | Final verification pass                       | Ensure completeness before paper submission            |

#### Keyword Expansion Loop

During the search and reading process, you will discover new terms that should be added to the keyword matrix:

```
1. Read a paper → discover new term (e.g., "social simulation" → "generative agents")
2. Add new term to keyword matrix as D7 or M6
3. Re-search all venue×year combinations with the new term
4. Add newly discovered papers to related-work.md
5. Repeat whenever a new term is discovered
```

This is critical: the keyword matrix is NOT static. It grows as you learn more about the field.

#### Cross-Reference Expansion

```
For each RELEVANT paper found:
  1. Read its "Related Work" section → discover papers you haven't found
  2. Check its references → discover older foundational papers
  3. Check who cites it (Google Scholar "Cited by") → discover newer papers
  4. Check its authors' other publications → discover related work by same group
  5. Add all discovered papers to the search queue
```

---

### 3.11 Coverage Tracking and Gap Detection (Stages 6–7)

Maintain a coverage tracker to ensure no venue is missed. This is the accountability mechanism that makes the pipeline work.

#### Coverage Tracker Template (auto-populated from venue taxonomy)

```
## Coverage Tracker for {{RESEARCH_AREA}}

### Main Conference Proceedings
| Venue       | Year       | Total Papers | Scanned | Relevant Found | Status        |
|-------------|------------|--------------|---------|----------------|---------------|
| {{VENUE_1}} | {{YEAR}}   | ~N           | 0       | 0              | ❌ Not started |
| {{VENUE_1}} | {{YEAR-1}} | ~N           | 0       | 0              | ❌ Not started |
| {{VENUE_2}} | {{YEAR}}   | ~N           | 0       | 0              | ❌ Not started |
| ...         | ...        | ...          | ...     | ...            | ...           |

### Workshop Proceedings
| Workshop               | Year     | Total Papers | Scanned | Relevant Found | Status        |
|------------------------|----------|--------------|---------|----------------|---------------|
| {{VENUE}} {{WORKSHOP}} | {{YEAR}} | ~N           | 0       | 0              | ❌ Not started |
| ...                    | ...      | ...          | ...     | ...            | ...           |

### Preprint Sources
| Source                       | Last Scanned | Status        |
|------------------------------|--------------|---------------|
| arXiv {{PRIMARY_CATEGORY}}   | [Date]       | ❌ Not started |
| arXiv {{SECONDARY_CATEGORY}} | [Date]       | ❌ Not started |
| Google Scholar alerts        | [Date]       | ❌ Not started |

### Keyword Matrix Coverage
| Combination | Searched | Papers Found | Status      |
|-------------|----------|--------------|-------------|
| D1×M1       | ❌        | 0            | Not started |
| D1×M2       | ❌        | 0            | Not started |
| ...         | ...      | ...          | ...         |
```

**Status values:**
- ❌ Not started
- 🔄 In progress
- ✅ Complete

**Rule**: A venue is NOT complete until ALL its workshops are also scanned.

#### Gap Detection Rules

After each search session, run these automated checks:

1. **Zero-paper venues**: If a venue in the taxonomy has 0 papers in related-work.md → it hasn't been searched → search it
2. **Year gaps**: If you have papers from some years but not others for the same venue → fill the gap
3. **Venue concentration**: If >60% of papers come from 1-2 venues → search is too narrow → expand search
4. **Missing workshops**: If you have 0 workshop papers → workshops definitely missed → scan workshops
5. **Missing arXiv categories**: If all papers come from one arXiv category → other categories may have been missed
6. **Keyword coverage**: If some D×M combinations have 0 results → verify those were actually searched
7. **Temporal coverage**: If all papers are from the same year → widen year range
8. **New keyword check**: If you've discovered new terms during reading but haven't re-searched with them → re-search

#### Automated Gap Detection Script (generic)

```python
import re
from collections import Counter

# Read related-work.md
with open('docs/related-work.md') as f:
    content = f.read()

# Extract venues and years from paper entries
venue_pattern = r'\*\*Venue\*\*:\s*(.+?)\n'
year_pattern = r'\b(20[12]\d)\b'

venues = re.findall(venue_pattern, content)
years = re.findall(year_pattern, content)

if not venues:
    print("No papers with **Venue** field found. Ensure paper entries have metadata.")
    exit()

# Check for gaps
print(f"Total papers with venue: {len(venues)}")
print(f"Unique venues: {set(venues)}")
print(f"Year range: {min(years)}-{max(years)}")
print(f"Year distribution: {sorted(set(years))}")

# Check venue concentration
venue_counts = Counter(venues)
for venue, count in venue_counts.most_common():
    pct = count / len(venues) * 100
    flag = "CONCENTRATED" if pct > 30 else ""
    print(f"  {venue}: {count} ({pct:.0f}%) {flag}")

# Generic check: list venues that have papers vs. expected
# User should fill in expected_venues based on their Research Area
print("\n--- Gap Analysis ---")
print("Update expected_venues list in this script based on your venue taxonomy.")
```

---

### 3.12 Agent-Based Search Automation

Use parallel browser agents to automate the proceedings search. This is how you search 10+ venue×year combinations efficiently.

#### Agent Template — Conference Proceedings Scan

```
You are a literature search agent. Your task is to scan the proceedings
of [CONFERENCE] [YEAR] for papers related to: {{RESEARCH_AREA}}.

Search keywords: {{KEYWORD_LIST}}

Step 1: Go to DBLP (dblp.org) or the conference website and find the full
        list of accepted papers for [CONFERENCE] [YEAR].
Step 2: For each paper, check if the title or abstract contains any of
        the search keywords.
Step 3: For papers with keyword matches, read their abstracts.
Step 4: Return a structured list of ALL relevant papers with:
        - Exact title
        - Authors
        - Link (arxiv or conference page)
        - 2-sentence summary of relevance
        - Relevance level: HIGH / MEDIUM / LOW

Be exhaustive. Do not skip any paper. Return ALL matches, not just the top ones.
```

#### Agent Template — Workshop Scan

```
You are a literature search agent. Your task is to find ALL workshops at
[CONFERENCE] [YEAR] that may contain papers related to: {{RESEARCH_AREA}}.

Search keywords: {{KEYWORD_LIST}}

Step 1: Search for "[CONFERENCE] [YEAR] workshops" and find the full
        workshop list.
Step 2: For each workshop whose topic overlaps with {{RESEARCH_AREA}}:
        a. Find the accepted papers list
        b. Read paper titles and abstracts
        c. Note any relevant papers
Step 3: Return structured output:
        - Workshop name and URL
        - Relevant papers found (title, authors, link, relevance)
        - Total papers in workshop vs. relevant to our area

Pay special attention to workshops whose titles contain any keyword from
the keyword matrix.
```

#### Agent Template — Keyword Combination Scan

```
You are a literature search agent. Search for papers matching this
keyword combination: "[D_i] [M_j]"

Search on ALL of these sources:
1. Google Scholar: "[D_i] [M_j]"
2. Semantic Scholar: search with same keywords
3. arXiv: search with same keywords
4. DBLP: search with same keywords

For each paper found:
- Exact title
- Authors
- Link
- Venue and year
- 1-sentence relevance summary
- Relevance level: HIGH / MEDIUM / LOW

Return ALL unique papers. Deduplicate across sources.
```

#### Parallel Agent Deployment Strategy

```
# Phase A: Main proceedings scan (run 4-6 agents in parallel)
Agent 1: Scan {{TIER1_VENUE_1}} {{CURRENT_YEAR}} main proceedings
Agent 2: Scan {{TIER1_VENUE_1}} {{CURRENT_YEAR-1}} main proceedings
Agent 3: Scan {{TIER1_VENUE_2}} {{CURRENT_YEAR}} proceedings
Agent 4: Scan {{TIER1_VENUE_3}} {{CURRENT_YEAR}} proceedings
Agent 5: Scan {{TIER1_VENUE_4}} {{CURRENT_YEAR}} proceedings
Agent 6: Scan {{TIER1_VENUE_5}} {{CURRENT_YEAR}} proceedings

# Phase B: Workshop scan (run after Phase A, 4-6 agents in parallel)
Agent 1: Scan {{TIER1_VENUE_1}} {{CURRENT_YEAR}} workshops
Agent 2: Scan {{TIER1_VENUE_2}} {{CURRENT_YEAR}} workshops
Agent 3: Scan {{TIER1_VENUE_3}} {{CURRENT_YEAR}} workshops
Agent 4: Scan {{TIER1_VENUE_4}} {{CURRENT_YEAR}} workshops

# Phase C: Keyword combination scan (run in parallel with Phase B)
Agent 1: Search D1×M1 through D1×M{{n}} on Google Scholar
Agent 2: Search D2×M1 through D2×M{{n}} on Google Scholar
Agent 3: Search D3×M1 through D4×M{{n}} on Semantic Scholar
Agent 4: Search D5×M1 through D{{n}}×M{{n}} on arXiv
```

After all agents complete: merge results, deduplicate, update coverage tracker, add new papers to related-work.md.

---

### 3.13 End-to-End Search Execution Checklist

Run this checklist at the START of every related-work session:

- [ ] **Configuration parsed**: All 6 fields in `## Research Project Configuration` have been read and keywords extracted
- [ ] **Venue taxonomy auto-generated**: All Tier 1-3 venues listed with year ranges based on research area
- [ ] **Keyword matrix auto-generated**: All D×M combinations enumerated from config fields
- [ ] **Coverage tracker initialized**: All venue×year combinations and keyword combinations tracked
- [ ] **Agent templates prepared**: Conference scan, workshop scan, keyword scan templates filled with config values
- [ ] **Tier 1 venues ALL scanned**: Every Tier 1 venue×year has been searched
- [ ] **Tier 2-3 venues keyword-filtered**: Keyword matrix applied to all Tier 2-3 venues
- [ ] **Workshops ALL scanned**: Every workshop at Tier 1-2 conferences checked
- [ ] **arXiv categories scanned**: All auto-derived arXiv categories checked
- [ ] **Cross-reference expansion done**: Related Work sections and citations of found papers checked
- [ ] **Keyword expansion loop completed**: New terms discovered during reading have been added and re-searched
- [ ] **Zero gap-detected issues**: No missing venues, no year gaps, no venue concentration
- [ ] **All D×M keyword combinations searched**: None skipped

**Rule of thumb**: If you haven't searched at least 5 conferences × 3 years = 15 venue×year combinations, your search is incomplete.

## 4. Visualization and Diagram Techniques

### 4.1 ASCII Architecture Diagrams

Use ASCII art to illustrate model architectures:

```
Input: Question Q
    ↓
[Embedding Layer]
    ↓
┌─────────────────────────────────────┐
│  Level 0: 1 concept (coarsest)      │
│  c_0 = f_0(Q)                       │
│         ↓                           │
│  Level 1: 2 concepts                │
│  c_1 = f_1(c_0) + residual_0        │
│         ↓                           │
│  Level 2: 4 concepts                │
│  c_2 = f_2(c_1) + residual_1        │
│         ↓                           │
│  Level 5: 32 concepts (finest)      │
│  c_5 = f_5(c_4) + residual_4        │
└─────────────────────────────────────┘
    ↓
[Decoder] → Solution
```

### 4.2 Before/After Comparison Diagrams

```
Standard CoT:
  Q → "Step 1: ..." → "Step 2: ..." → "Step 3: ..." → Answer
      [100 tokens]     [120 tokens]     [80 tokens]
      
Their Method:
  Q → [latent vector h] → Answer
      [1 vector, 2048-dim]
```

### 4.3 Data Flow Diagrams

```
Generic Two-Phase Architecture Example:

Phase 1: Training (Feature/Structure Extraction)
  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
  │   Input     │────→│  Ground     │────→│   Output    │
  │   Data      │     │  Truth      │     │   Target    │
  └─────────────┘     └─────────────┘     └─────────────┘
         │                   │                   │
         └───────────────────┴───────────────────┘
                             ↓
                    [{{YOUR_EXTRACTOR_COMPONENT}}]
                             ↓
                    Extracted Structure/Features

Phase 2: Inference (Prediction/Generation)
  ┌─────────────┐
  │   Input     │────→ [{{YOUR_PREDICTOR_COMPONENT}}] ──→ Output
  └─────────────┘              ↓
                    Predicted Structure
```

### 4.4 Formula Blocks

Use LaTeX-style math in code blocks for clarity:

```
Mathematical Notation Example:
  Y = f(X) + ε
  
  where:
    Y     = output/prediction
    f(X)  = model function of input X
    ε     = error/residual term

Or for decomposition methods:
  Z_total = Z_coarse + Z_fine
  
  where:
    Z_total  = full representation
    Z_coarse = low-resolution/base component
    Z_fine   = high-resolution/detail component
```

### 4.5 Comparison Tables

Always use tables for systematic comparisons:

```
| Dimension   | Their Approach  | Our Approach                | Key Difference |
|-------------|-----------------|-----------------------------|----------------|
| Space       | Discrete tokens | Continuous concepts         | Representation |
| Structure   | Flat sequence   | Hierarchical pyramid        | Organization   |
| Training    | End-to-end      | Two-phase (Extract→Predict) | Paradigm       |
| Compression | None            | 6-level compression         | Efficiency     |
```

### 4.6 ASCII Diagram Best Practices

**Use box-drawing characters for clean architecture diagrams:**
```
┌─────────────────────────────────────┐
│  Component Name                     │
├─────────────────────────────────────┤
│  Input: X                           │
│    ↓                                │
│  Process: f(X)                      │
│    ↓                                │
│  Output: Y                          │
└─────────────────────────────────────┘
```

**Use arrows to show data flow:**
```
Q → [Encoder] → h → [Decoder] → A
```

**Use indentation for hierarchical relationships:**
```
Level 0 (coarse)
  └─→ Level 1
        └─→ Level 2
              └─→ Level 3 (fine)
```

**Label dimensions and shapes:**
```
h ∈ R^{batch×seq×dim}  →  h' ∈ R^{batch×seq×dim}
```

**Common diagram types and when to use them:**

| Diagram Type     | Best For                 | Example             |
|------------------|--------------------------|---------------------|
| Architecture box | Model structure          | Core Method section |
| Data flow arrows | Input→Output pipeline    | Core Idea section   |
| Before/After     | Comparison of approaches | Example section     |
| Step-by-step     | Algorithm walkthrough    | Core Method section |
| State evolution  | Temporal progression     | Example section     |

---

## 5. Section-by-Section Writing Guidelines

### Section 1-6: Foundational Papers
- These are the most important papers — write with maximum detail
- Include extensive ASCII diagrams
- Provide thorough comparison tables
- Verify all quantitative claims against the original paper

### Section 14-16: Core Technical Papers
- Focus on architectural details and methodological innovations
- Map technical contributions to our approach explicitly
- Include implementation-level details (loss functions, training procedures)

### Section 17: Conference Overview Sections
- These contain sub-papers (17.1.1, 17.1.2, etc.)
- Each sub-paper should follow the same 9-component template
- Add a synthesis table at the end of each conference section
- **Header Hierarchy**: Main conference section uses `### 17.X`, sub-papers use `#### 17.X.Y`, internal sections use `##### Section Name`
- **Critical distinction**: `### 7.1 Classification by...` is an ORGANIZATION header (not a paper), while `### 10.1 ∇-Reasoner...` is a PAPER

#### Distinguishing Papers from Organization Headers

Use this checklist:
- **Has Link/Paper line?** → It's a paper (needs full template)
- **No Link, no Paper line?** → Organization header (section intro, synthesis, classification)
- **Has `[CAT:X] [REL:Y]`?** → Already marked as paper
- **One-line description only?** → Stub paper (needs full upgrade)

**Common organization headers to SKIP**:
- `### 3.1 Taxonomy of Methods` (section taxonomy)
- `### 5.1 Our Core Research Objective` (our work description)
- `### 6.1 Open Questions` (discussion section)
- `### 8.1 Categorization of Approaches` (subsection intro)
- `### 12.5 Synthesis: Trade-offs in the Field` (synthesis)
- `### 15.3 Synthesis: Future Directions` (synthesis)

**Pattern**: Any header that describes a classification, synthesis, questions, or objectives — rather than a specific paper — is an organization header.

### Section 18: Analysis and Position Papers
- Focus on insights, findings, and implications
- Core Method may be shorter (these are often empirical studies)
- Example should illustrate the key phenomenon they discover
- Relationship to Our Work should discuss how the finding supports or cautions our approach

---

## 6. Quality Checklist

Before marking any paper as complete, verify:

- [ ] `[CAT:X] [REL:Y]` tags are present and accurate
- [ ] Paper title is exact (match the PDF title)
- [ ] Link is clickable and resolves correctly
- [ ] Summary explains what the paper DOES, not just claims
- [ ] Core Motivation states the problem, not the solution
- [ ] Core Idea is expressed as a single, clear insight
- [ ] Core Method includes step-by-step technical details
- [ ] Example is concrete, simple, and self-contained
- [ ] Relationship to Our Work includes a comparison table
- [ ] All technical terms are used consistently
- [ ] Quantitative claims match the original paper
- [ ] ASCII diagrams are readable and accurate
- [ ] No placeholder text (e.g., "TBD", "TODO", "...")

---

## 7. Common Pitfalls and How to Avoid Them

### Pitfall 1: Shallow Summaries
**Bad**: "This paper proposes a new method for image classification."
**Good**: "This paper proposes a vision transformer with hierarchical attention, which processes images at multiple scales using windowed self-attention and achieves 87.2% accuracy on ImageNet with 30% fewer FLOPs than ViT-Base."

**Bad**: "This paper proposes a new training method."
**Good**: "This paper proposes contrastive self-supervised pre-training that learns visual representations by maximizing agreement between differently augmented views of the same image, eliminating the need for labeled data."

**Why**: Specificity builds credibility. Include the method name, key mechanism, and quantitative result.

### Pitfall 2: Confusing Motivation with Method
**Bad**: "They use reinforcement learning to train the model." (This is a method, not a motivation)
**Good**: "Prior latent reasoning methods require expensive curriculum learning that suffers from catastrophic forgetting. The authors seek a single-stage training approach that avoids this issue."

### Pitfall 3: Missing Concrete Examples
**Bad**: "Their method compresses reasoning traces."
**Good**: "For the problem 'If a train travels 60 km/h for 2 hours, how far does it go?', standard CoT generates: 'First, I need to find distance. Distance = speed × time. Speed is 60 km/h. Time is 2 hours. So distance = 60 × 2 = 120 km.' (45 tokens). Their method compresses this into a single 2048-dimensional latent vector that encodes the same reasoning."

### Pitfall 4: Vague Relationship Statements
**Bad**: "This is related to our work."
**Good**: "Both approaches use multi-scale feature processing, but their method processes scales sequentially (coarse → fine), while our {{RESEARCH_TARGET}} processes all scales in parallel with cross-scale attention, reducing latency by 40%."

**Why**: Specific comparisons demonstrate deep understanding and clearly position your contribution.

### Pitfall 5: Inconsistent Terminology
**Bad**: Using "latent vectors" in one paper, "hidden states" in another, and "concept embeddings" in a third to describe the same thing.
**Good**: Choose one term (e.g., "concept vectors") and use it consistently, noting when a paper uses a different term.

### Pitfall 6: Unchecked Claims
**Bad**: "Their method achieves 10× speedup." (from memory)
**Good**: "Their method achieves 1.6–2.0× speedup on math reasoning benchmarks (Section 4.2, Table 3)."

### Pitfall 7: Garbled Text from Bulk Scripts
**Bad**: "Proposes Latent Guidance... Existing methods face challenges in efficiency, scalability, or adaptability. The authors seek to overcome these limitations through novel latent-space techniques..." (generic bulk-script text appended to actual content)
**Good**: "Small LLMs struggle with complex reasoning tasks due to limited capacity for multi-step planning, yet deploying large models at inference time is prohibitively expensive. The authors ask: can we decouple cognitive planning from linguistic execution by having the large model generate compact latent guidance vectors?"

**How to avoid**: After running bulk scripts, grep for the phrase "Existing methods face challenges" or "novel latent-space techniques" and replace with paper-specific content.

### Pitfall 8: Papers Appearing in Multiple Sections
**Bad**: Writing completely different descriptions of the same paper in Section 10 and Section 14.
**Good**: Consistent core facts (method, key result) with section-appropriate emphasis (Section 10 focuses on brief overview, Section 14 focuses on technical depth).

**How to avoid**: Search for the paper title across the entire document before writing. If it appears elsewhere, read that entry first and maintain consistency.

---

## 8. Validation-Driven Development Workflow

The validation script is not just a final check — it is the **primary navigation tool** throughout the upgrade process.

### 8.1 Iterative Validation Loop

```
Run Validation → Identify Incomplete Papers → Fix Batch → Re-validate → Repeat
```

**Why iterative?**
- Prevents "surprise" missing sections at the end
- Provides concrete progress metrics ("69/116 complete → 89/116 → 116/116")
- Identifies patterns in missing sections (e.g., "all missing Core Method")

### 8.2 Automated Validation
Run the Python validation script to check for missing sections:

```python
import re

with open('docs/related-work.md') as f:
    content = f.read()

# Find all paper headers
papers = re.findall(r'^(### \d+\.\d+ .*?)\n', content, re.MULTILINE)
positions = [m.start() for m in re.finditer(r'^### \d+\.\d+ ', content, re.MULTILINE)]

required_sections = ['Summary', 'Core Motivation', 'Core Idea', 'Core Method', 'Example', 'Relationship to Our Work']

incomplete = []
for i, pos in enumerate(positions):
    end_pos = positions[i+1] if i+1 < len(positions) else len(content)
    block = content[pos:end_pos]
    
    has_tags = '[CAT:' in block and '[REL:' in block
    missing = [s for s in required_sections if not re.search(r'####\s+' + re.escape(s), block)]
    
    if not has_tags or missing:
        incomplete.append((papers[i], missing, not has_tags))

print(f"Total papers: {len(papers)}")
print(f"Complete: {len(papers) - len(incomplete)}")
print(f"Incomplete: {len(incomplete)}")
for title, missing, no_tags in incomplete:
    print(f"  {title}: missing {missing}, tags_ok={not no_tags}")
```

### 8.3 Content Verification After Large Edits

After large `search_replace` operations (especially when the tool reports "save file failed"):

1. **Grep spot-check**: Search for the modified paper headers to confirm they exist
2. **Read sample sections**: Read 20-30 lines after each modified header to confirm content
3. **Line count check**: Compare before/after file sizes to confirm additions
4. **Tag verification**: Confirm `[CAT:X] [REL:Y]` tags were saved correctly

**Common issue**: The `search_replace` tool may report "save file failed, reason: unknown" but the content IS actually saved. Always verify with `grep_code` before retrying.

### 8.4 Manual Validation
For papers marked [REL: Critical] or [REL: High]:
1. Re-read the written summary against the paper abstract
2. Verify the Core Idea matches the paper's central claim
3. Check that the Example accurately illustrates the method
4. Confirm the comparison table is fair and accurate
5. **NEW**: Verify the Core Motivation does not contain garbled text from bulk scripts
6. **NEW**: Check that ASCII diagrams render correctly in markdown preview

---

## 9. Batch Processing Strategy

When upgrading many papers (e.g., 20+ in a section), use this phased approach:

### Phase 1: Preparation
1. Run validation script to identify ALL incomplete papers
2. Categorize by relevance (Critical/High get more attention)
3. Group by topic for efficient context switching
4. **Distinguish papers from organization headers** (see Section 5)

### Phase 2: Parallel Research (Browser Agents)
1. Launch 4 browser agents simultaneously
2. Each agent reads 3-4 papers and extracts structured content
3. While agents run, write content for papers you already understand
4. **Agent prompt template**: See Section 3.2 for proven prompt design

### Phase 3: Bulk Generic Content (Optional but Efficient)

For papers that only need "good enough" content (Medium/Low relevance), use a Python script to add generic but structurally complete sections:

```python
# Example: Add generic Core Motivation, Core Method, Example to multiple papers
import re

with open('docs/related-work.md', 'r') as f:
    content = f.read()

# Find all papers missing Core Method
pattern = r'(#### Core Idea\n.*?)(\n#### Relationship to Our Work)'
def add_method(match):
    return match.group(1) + '\n\n#### Core Method\n```\n[Generic method description]\n```\n\n#### Example\n[Generic example]\n' + match.group(2)

content = re.sub(pattern, add_method, content, flags=re.DOTALL)
```

**When to use bulk scripts**:
- 20+ papers need the same missing sections
- Papers are [REL: Medium] or [REL: Low]
- Time is limited and manual upgrade of every paper is impractical
- Creates structural completeness that can be refined later

**When NOT to use bulk scripts**:
- [REL: Critical] or [REL: High] papers (need accurate content)
- Papers with unique or complex methods
- Synthesis or survey papers

### Phase 4: Manual Upgrade of Critical Papers
1. Focus on [REL: Critical] and [REL: High] papers
2. Use agent research outputs for accurate content
3. Write custom Core Method with ASCII diagrams
4. Write concrete, paper-specific Examples

### Phase 5: Incremental Refinement
1. Re-run validation script
2. Identify papers still missing sections
3. Apply targeted fixes (not bulk)
4. **Spot-check bulk-generated content** for garbled text or inaccuracies

### Phase 6: Final Validation
1. Run the automated validation script
2. Confirm 0 incomplete papers (excluding organization headers)
3. Do a final manual read-through of [REL: Critical] papers

---

## 9.5 Stub-to-Full Entry Pipeline

Many papers start as one-line stubs:

```
### 10.5 Latent Thinking Optimization (LTO) (2025)
Shows that latent thoughts naturally encode reward signals.
```

Transforming a stub into a full entry requires a systematic pipeline:

### Step 1: Research the Paper
- Search arxiv for the exact title
- Read abstract and introduction
- Note: year, venue, authors, core claim

### Step 2: Extract Structured Information
```
Paper: [Exact Title]
Link: [arxiv URL]
Problem: [1 sentence]
Insight: [1 sentence]
Method: [3-5 sentences]
Result: [1-2 sentences]
```

### Step 3: Write Tags and Metadata
```
**[CAT: Core] [REL: High]**

**Paper**: "Exact Title"
**Link**: https://arxiv.org/abs/XXXX.XXXXX
**Code**: Null
```

### Step 4: Expand Each Section
- **Summary**: 3-6 sentences synthesizing problem + method + result
- **Core Motivation**: Why did authors write this? What gap do they fill?
- **Core Idea**: Single insight as transformation/before-after
- **Core Method**: Step-by-step with ASCII diagram
- **Example**: Concrete toy problem with BEFORE/AFTER
- **Relationship to Our Work**: Comparison table

### Step 5: Verify with Validation Script
- Confirm all 6 required sections are present
- Confirm tags are correct
- Confirm link is valid

---

## 9.6 Cross-Section Consistency

Some papers appear in multiple sections (e.g., ReLaX in Section 10 and Section 14). Maintain consistency:

### Consistency Rules
1. **Same core facts everywhere**: Method description, key results, and links must match
2. **Section-appropriate emphasis**:
   - Section 10 (Brief Overview): Shorter, focuses on high-level contribution
   - Section 14 (Core Technical): Longer, focuses on technical details and architecture
3. **Same comparison table columns**: Use consistent aspect names across sections
4. **Reference the other section**: "See Section 14.10 for detailed technical discussion"

### How to Check
```bash
# Search for paper title across entire document
grep -n "ReLaX" docs/related-work.md

# Compare the two entries for consistency
```

---

## 9.7 Synthesis Section Writing

Synthesis sections (e.g., `### 16.7 Synthesis: Compression Spectrum`) tie together multiple papers:

### Structure
1. **Theme identification**: What connects these papers?
2. **Spectrum/table**: Organize papers along key dimensions
3. **Gap analysis**: What is missing from the literature?
4. **Our position**: Where does our work fit?

### Example Synthesis Table
```
| Method   | Space  | Structure    | Speed | Accuracy | Our Advantage      |
|----------|--------|--------------|-------|----------|--------------------|
| Method A | Token  | Linear       | 1×    | High     | Baseline           |
| Method B | Latent | Flat         | 2×    | Medium   | Efficient          |
| Method C | Latent | Flat         | 3×    | High     | End-to-end         |
| Ours     | Latent | Hierarchical | 5×    | High     | {{YOUR_ADVANTAGE}} |
```

### Writing Tips
- Use synthesis sections to tell a STORY about the field's evolution
- Highlight tensions and tradeoffs (e.g., speed vs. accuracy)
- Explicitly position our work in the landscape

---

## 10. Our Work Reference Template

When writing "Relationship to Our Work", always compare against YOUR approach. Use the template below, filled in from your User Configuration section:

```
**Our Approach: {{RESEARCH_TARGET}}**
- **Goal**: {{MAIN_MOTIVATION}}
- **Core Idea**: {{MAIN_IDEA}}
- **Key Techniques**:
  - {{KEY_TECHNIQUE_1}}
  - {{KEY_TECHNIQUE_2}}
  - {{KEY_TECHNIQUE_3}}
- **Architecture/Method**: {{METHOD_DESCRIPTION}}
- **Training**: {{TRAINING_APPROACH}}
- **Output**: {{OUTPUT_DESCRIPTION}}
```

**Example (filled in for a latent reasoning project):**
```
**Our Approach: Neural Latent Concept Pyramid (NLCP V3)**
- **Goal**: Compress Chain-of-Thought reasoning into hierarchical latent concepts
- **Core Idea**: A hierarchical concept pyramid that compresses CoT into multi-scale representations
- **Key Techniques**:
  - Hierarchical concept pyramid (1→2→4→8→16→32 concepts)
  - Residual decomposition (coarse-to-fine refinement)
  - Cross-attention refinement between levels
- **Architecture**: 6-level concept pyramid with residual flow
- **Training**: Two-phase (extraction → prediction)
- **Output**: Compact hierarchical concept representation → decoded solution
```

**Example (filled in for a computer vision project):**
```
**Our Approach: Hierarchical Patch Transformer (HPT)**
- **Goal**: Efficient high-resolution image understanding with adaptive patch granularity
- **Core Idea**: Process images at multiple patch scales simultaneously, fusing coarse semantic features with fine spatial details
- **Key Techniques**:
  - Multi-scale patch embedding (8×8 → 16×16 → 32×32 patches)
  - Cross-scale feature fusion with attention
  - Adaptive patch selection based on content complexity
- **Architecture**: Pyramid feature extractor with scale fusion modules
- **Training**: End-to-end with scale consistency losses
- **Output**: Multi-scale feature pyramid for downstream tasks
```

---

## 11. Terminology Glossary

### Creating Your Own Glossary

Based on your User Configuration, create a terminology table. Here is the template:

```
| Term            | Meaning        | When to Use |
|-----------------|----------------|-------------|
| {{YOUR_TERM_1}} | {{Definition}} | {{Context}} |
| {{YOUR_TERM_2}} | {{Definition}} | {{Context}} |
```

### Example Glossaries by Domain

**For NLP / Latent Reasoning:**
| Term            | Meaning                               | When to Use                    |
|-----------------|---------------------------------------|--------------------------------|
| Concept Pyramid | Our hierarchical latent structure     | When describing our work       |
| Concept Vector  | A single latent representation        | General term for latent states |
| CoT             | Chain-of-Thought                      | Standard abbreviation          |
| Residual Flow   | Our level-wise residual decomposition | Specific to our method         |

**For Computer Vision:**
| Term           | Meaning                              | When to Use               |
|----------------|--------------------------------------|---------------------------|
| Patch Pyramid  | Our multi-scale patch hierarchy      | When describing our work  |
| Scale Fusion   | Cross-resolution feature combination | Specific to our method    |
| Adaptive Patch | Dynamically-sized spatial tokens     | General term in our paper |

**For Systems / Databases:**
| Term           | Meaning                             | When to Use              |
|----------------|-------------------------------------|--------------------------|
| Query Graph    | Our structured query representation | When describing our work |
| Execution Plan | Optimized operator ordering         | General database term    |
| Index Shard    | Partitioned index segment           | Specific to our method   |

### General Rules
- Define YOUR terms clearly and use them consistently
- Note when a paper uses a DIFFERENT term for the same concept
- Keep the glossary short (8-12 terms max) — only domain-specific terms

---

## 12. Relationship Table Design Patterns

Comparison tables in "Relationship to Our Work" should follow consistent patterns:

### Standard Dimensions
Always include these core dimensions:
- **Representation/Space**: What kind of latent space?
- **Structure**: Flat, hierarchical, sequential?
- **Training**: How is it trained?
- **Key Difference**: One-line summary of the main distinction

### Optional Dimensions (add as relevant)
- **Optimization**: Test-time vs training-time?
- **Interpretability**: Can you inspect intermediate steps?
- **Efficiency**: Token reduction, speedup?
- **Supervision**: What data is needed?
- **Generalization**: Cross-domain, zero-shot?

### Table Templates by Paper Type

**For architecture papers:**
```
| Aspect     | Their Work     | Our Work             | Key Difference |
|------------|----------------|----------------------|----------------|
| Structure  | Flat residuals | Pyramid (1→2→4→...)  | Hierarchy      |
| Training   | Single-phase   | Two-phase            | Paradigm       |
| Refinement | Sequential     | Scale-level parallel | Efficiency     |
```

**For training papers:**
```
| Aspect      | Their Work  | Our Work             | Key Difference |
|-------------|-------------|----------------------|----------------|
| Supervision | (Q,A) only  | (Q,CoT,A)            | Data required  |
| Signal      | Self-reward | Residual loss        | Training obj   |
| Exploration | RL sampling | Autoregressive scale | Method         |
```

**For analysis papers:**
```
| Aspect        | Their Work            | Our Work               | Key Difference |
|---------------|-----------------------|------------------------|----------------|
| Analysis type | Causal intervention   | Reconstruction         | Approach       |
| Structure     | Discovers implicit    | Explicitly designed    | Design         |
| Finding       | Non-local propagation | Hierarchical attention | Insight        |
```

---

## 13. Summary of Key Principles

1. **Every paper gets the full template** — no shortcuts, no "Summary only" entries
2. **Read before writing** — never write content without reading the paper
3. **Multi-source verification** — confirm understanding across arXiv, GitHub, OpenReview
4. **Concrete examples** — every paper needs a toy problem illustration
5. **Systematic comparison** — every paper needs a comparison table with our work
6. **Visual explanations** — use ASCII diagrams extensively
7. **Iterative refinement** — write, validate, revise
8. **Consistency** — use the same terminology, style, and depth across all entries
9. **Validate iteratively** — run the validation script after every batch, not just at the end
10. **Bulk then refine** — use bulk scripts for structural completeness, manual upgrades for accuracy
11. **Distinguish headers** — organization headers don't need the full template
12. **Cross-check duplicates** — papers in multiple sections must have consistent facts

---

*This skill document should be referenced whenever adding or upgrading paper entries in `docs/related-work.md`.*
