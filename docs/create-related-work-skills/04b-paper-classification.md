# Paper Classification and Taxonomy

## Purpose

Organize all read papers into a two-level hierarchy (Category → Sub-Category) derived from `00-user-define.md`. This taxonomy defines the section structure of `docs/related-work.md`.

**Core rule**: Every Category must trace back to at least one field in `00-user-define.md`. No free-floating categories allowed.

**When to run this stage**: After `04-reading-extraction.md` — once the Paper Database is populated with CAT/REL tags and structured extractions.

---

## §1 Input

| Source                     | What to Read                                                                               |
|----------------------------|--------------------------------------------------------------------------------------------|
| `00-user-define.md`        | Fields 1–8: Research Area, Target, Direction, Motivation, Idea, Methods, Dimensions, Scope |
| `04-reading-extraction.md` | Paper Database with CAT/REL tags, structured extractions                                   |

---

## §2 Taxonomy Derivation — From Stage 0 Fields

### Derivation Rules

```
Rule 1: Each Key Method from field 6 → one Category
  Example: Key Methods = "LLM-based agents, Behavioral finance, RAG, Rule+LLM hybrids"
  → Category 1: LLM-Based Agent Architectures
  → Category 2: Behavioral Finance in Simulation
  → Category 3: Knowledge-Augmented Agents
  → Category 4: Hybrid Rule-LLM Systems

Rule 2: Main Motivation (field 4) → one Category for problem-oriented papers
  Example: Motivation = "Rule-based agents cannot capture behavioral complexity"
  → Category: Agent-Based Market Simulation (prior approaches)

Rule 3: Main Idea (field 5) → one Category for the core approach papers
  Example: Idea = "LLM agents with behavioral biases produce emergent dynamics"
  → Category: Emergent Behavior in LLM Multi-Agent Systems

Rule 4: Search Scope Summary (field 8) → one Category per distinct research thread
  Example: Scope = "LLM agents, social simulation, financial market simulation, ABM"
  → Each thread maps to or merges into a Category

Rule 5: Comparison Dimensions (field 7) → validation axes for each Category
  These become TABLE COLUMNS in synthesis sections, not categories themselves.
```

### Category Naming Rules

```
Rule A: Name = "[Technical Descriptor] [Approach/Problem]"
  Good:  "Latent-Space Reasoning Methods"
  Good:  "Multi-Scale Generative Models"
  Bad:   "Other Methods"          (vague)
  Bad:   "Background"             (non-technical)

Rule B: Each Category name must clearly differentiate from others
  Good:  "Token-Level CoT Compression" vs "Latent-Space Reasoning"
  Bad:   "LLM Methods 1" vs "LLM Methods 2"

Rule C: Category names map directly to related-work.md section headers
  Category 1 name → ## 1. [Category 1 Name]
  Category 2 name → ## 2. [Category 2 Name]
  ...
```

### Scale Constraints

| Level                       | Minimum | Typical | Maximum |
|-----------------------------|---------|---------|---------|
| Categories                  | 3       | 5–7     | 10      |
| Sub-categories per Category | 2       | 2–4     | 6       |
| Total sub-categories        | 6       | 10–20   | 40      |

---

## §3 Category Construction Protocol

### Step-by-Step Process

```
Step 1: List all Key Methods from 00-user-define.md (field 6)
  M1: [method 1]
  M2: [method 2]
  M3: [method 3]
  ...

Step 2: List all Search Scope threads from field 8
  S1: [scope thread 1]
  S2: [scope thread 2]
  ...

Step 3: Extract Main Motivation (field 4) as a problem-oriented thread
  G: [motivation / gap — what prior work failed to do]

Step 4: Extract Main Idea (field 5) as the core approach thread
  I: [core insight]

Step 5: Group related threads into Categories
  - Merge threads that address the same problem or use the same technique
  - Split threads that cover clearly distinct aspects

Step 6: For each Category, define Sub-Categories
  Based on: different architectures, different problem formulations,
  different training paradigms, different representation spaces
```

---

## §4 Sub-Category Construction

### Sub-Category Derivation Methods

Within each Category, split into Sub-Categories using ONE of:

| Split Method           | When to Use                           | Example                                    |
|------------------------|---------------------------------------|--------------------------------------------|
| By architecture        | Same problem, different designs       | "Parallel vs Sequential"                   |
| By representation      | Same goal, different spaces           | "Continuous Latent vs Discrete Token"      |
| By training paradigm   | Same architecture, different training | "RL-based vs SFT-based vs Self-supervised" |
| By problem formulation | Same area, different angles           | "Efficiency-focused vs Quality-focused"    |
| By modality            | Different input/output types          | "Text-only vs Multimodal"                  |
| By scale               | Different granularity                 | "Single-scale vs Multi-scale"              |
| By application         | Same technique, different domains     | "Finance vs Social vs Political"           |

### Sub-Category Naming Rules

```
Rule 1: Name must indicate the SPLIT CRITERION
  Good:  "Continuous Latent Representations"
  Good:  "Discrete Token Compression"
  Bad:   "Sub-method A"

Rule 2: Sub-categories within a Category must be MUTUALLY EXCLUSIVE
  A paper should fit in exactly ONE sub-category per Category.

Rule 3: Each sub-category must have at least 2 papers
  If only 1 paper → merge into the closest sub-category.
```

---

## §5 Example Taxonomy

Using the LLM financial simulation example from `00-user-define.md`:

```
## 1. Agent-Based Financial Market Simulation (Prior Work)
### 1.1 Rule-Based Agent Systems          (ABIDES, JAX-LOB, classic ABMs)
### 1.2 Behavioral Agent Models           (prospect theory, bounded rationality)
### 1.3 Zero-Intelligence Agent Models    (market microstructure focus)

## 2. LLM Multi-Agent Systems
### 2.1 General-Purpose LLM Agent Frameworks   (AutoGen, LangGraph, MetaGPT)
### 2.2 Role-Playing and Persona Agents        (character simulation, behavioral prompting)
### 2.3 LLM Agents for Social Simulation       (generative agents, social dynamics)

## 3. LLM Agents in Financial Domains
### 3.1 LLM for Market Decision Making         (trading agents, portfolio optimization)
### 3.2 LLM for Financial Analysis             (report analysis, sentiment, prediction)
### 3.3 LLM-Based Financial Multi-Agent Sims   (our core related work)

## 4. Behavioral Finance and Cognitive Models
### 4.1 Classical Behavioral Finance Theory    (Kahneman, Thaler, etc.)
### 4.2 Computational Models of Bias           (bias in ML systems)

## 5. RAG and Knowledge-Augmented Agents
### 5.1 Retrieval-Augmented Generation         (RAG foundations)
### 5.2 Knowledge-Augmented Decision Making    (domain knowledge in LLM agents)
```

---

## §6 Paper Assignment Protocol

### Assign Each Paper to Category + Sub-Category

```
For each paper in the Paper Database (from 04-reading-extraction.md):

Step 1: Read its PROBLEM + INSIGHT + METHOD fields
Step 2: Match against Category definitions
  - Primary Category: where the paper's CORE contribution fits
  - A paper goes in exactly ONE Category
Step 3: Match against Sub-Category definitions within that Category
  - A paper goes in exactly ONE Sub-Category
Step 4: If a paper fits multiple Categories:
  - Place in the Category closest to its CORE contribution
  - Add a cross-reference note: "Also relevant to Category X.Y"
Step 5: If a paper fits NO Category:
  - Create a new Sub-Category under the closest Category
  - Create a new Category only if the gap is significant
```

### Assignment Table Template

```
## Paper Assignments for {{Research Target}}

### Category 1: [Name]
| Sub-Category | Papers                    | Count |
|--------------|---------------------------|-------|
| 1.1 [Name]   | Paper A, Paper B, Paper C | 3     |
| 1.2 [Name]   | Paper D, Paper E          | 2     |

### Category 2: [Name]
| Sub-Category | Papers                    | Count |
|--------------|---------------------------|-------|
| 2.1 [Name]   | Paper F, Paper G          | 2     |
| 2.2 [Name]   | Paper H, Paper I, Paper J | 3     |

### Unassigned Papers
| Paper   | Reason                  | Action                      |
|---------|-------------------------|-----------------------------|
| Paper K | Doesn't fit any sub-cat | Create new sub-category 3.4 |
```

---

## §7 Mapping to `related-work.md` Structure

The taxonomy directly defines the document header hierarchy:

```
# Related Work

## 1. [Category 1 Name]                          ← ORGANIZATION header (no template)
### 1.1 [Sub-Category 1.1 Name]                  ← ORGANIZATION header
#### 1.1.1 [Paper Title (Year)]                  ← PAPER entry (needs 9-component template)
#### 1.1.2 [Paper Title (Year)]                  ← PAPER entry
### 1.2 [Sub-Category 1.2 Name]
#### 1.2.1 [Paper Title (Year)]
### 1.N Synthesis: [Category 1 Summary]           ← SYNTHESIS (see 05-writing-guidelines.md §5)

## 2. [Category 2 Name]
### 2.1 [Sub-Category 2.1 Name]
#### 2.1.1 [Paper Title (Year)]
...
### 2.N Synthesis: [Category 2 Summary]

## N. Overall Positioning                         ← Final section
  How our work relates to ALL categories
  Key differentiator from each category
```

### Header Level Rules

| Level                | Format                          | Content Type                | Needs 9-Component Template? |
|----------------------|---------------------------------|-----------------------------|-----------------------------|
| `## N.`              | `## 1. Category Name`           | Category (ORGANIZATION)     | No                          |
| `### N.M`            | `### 1.1 Sub-Category Name`     | Sub-Category (ORGANIZATION) | No                          |
| `#### N.M.K`         | `#### 1.1.1 Paper Title (Year)` | Paper entry                 | **Yes**                     |
| `### N.N Synthesis:` | `### 1.4 Synthesis: ...`        | Synthesis table             | No (own format)             |

---

## §8 Taxonomy Validation

### Completeness Checks

| Check              | Condition                         | Fix                             |
|--------------------|-----------------------------------|---------------------------------|
| Empty Category     | Category has 0 papers             | Remove or merge with adjacent   |
| Empty Sub-Category | Sub-Category has 0 papers         | Remove or merge                 |
| Unassigned papers  | Papers not in any Category        | Create Sub-Category or reassign |
| Oversized Category | One Category has >40% of papers   | Split into two                  |
| Overlap            | Same paper in multiple Categories | Choose primary, add cross-ref   |

### Alignment Checks (against `00-user-define.md`)

| Check                  | Condition                                          | Fix                           |
|------------------------|----------------------------------------------------|-------------------------------|
| Orphan Category        | No field in Stage 0 maps to this Category          | Justify or remove             |
| Missing Method         | A Key Method from field 6 has no Category          | Create Category for it        |
| Missing Scope          | A Search Scope thread from field 8 has no Category | Create or merge               |
| No motivation Category | Main Motivation (field 4) not reflected            | Add problem-oriented Category |

### Structural Checks

| Check             | Condition                               | Fix                                  |
|-------------------|-----------------------------------------|--------------------------------------|
| Flat Category     | Only 1 Sub-Category                     | Add Sub-Categories or merge up       |
| Deep Sub-Category | >8 papers in one Sub-Category           | Split into finer Sub-Categories      |
| Imbalance         | Some Categories very large, others tiny | May indicate search bias; revisit §3 |

---

## Validation Checklist for Stage 04b

- [ ] Every Category traces back to a field in `00-user-define.md`
- [ ] Every Category has at least 2 Sub-Categories
- [ ] Every Sub-Category has at least 2 papers
- [ ] No paper assigned to more than one Category (cross-references OK)
- [ ] No papers remain unassigned
- [ ] No Category has >40% of all papers
- [ ] Each Key Method from field 6 has a corresponding Category
- [ ] Main Motivation (field 4) is reflected in at least one Category
- [ ] Category names are technical and specific (no "Other" or "Background")
- [ ] Sub-Category names indicate the split criterion
- [ ] Assignment Table is complete
- [ ] Taxonomy mapped to `related-work.md` header structure
