---
name: create-simulation-target-skill
purpose: Defines the **canonical specification** for the upstream target file `{domain}-{scenario}.md`. This file is the single piece of user-authored input that drives every downstream skill in `masim/skills/` (the top-level pipeline `create-simulation-skill.md`, the per-step guides `create-example-skill/`, and the per-agent handbook `agent-design-skill.md`). Any user — human author or downstream LLM — MUST follow this specification when authoring a scenario target.
status: canonical
audience: Authors and LLMs producing scenario target files; reviewers validating those files before invoking the pipeline.
rfc2119: This document uses MUST / MUST NOT / SHOULD / MAY in the RFC-2119 sense.
invocation: Use this file as the authoring guide and validation reference for `examples/{Scenario}/{domain}-{scenario}.md`. Downstream skills MUST NOT begin scenario construction until a target file conforming to this specification exists and passes §11 validation.
---

# Create-Simulation-Target-Skill — Authoring the Scenario Target File

## 0. What This Skill Defines

This skill defines the **format, content, and quality bar** of a single
upstream file that the user (or a downstream large language model
acting on the user's behalf) MUST author before any simulation
construction begins:

```
examples/{ScenarioName}/{domain}-{scenario}.md
```

Throughout this document we call this file the **scenario target
file**, or simply the **target file**. It declares — in a uniform,
machine-readable, peer-reviewable form — *what* the simulation must
achieve, *which* phenomena it must reproduce, *which* agents must
appear, *which* environment they live in, and *which* numeric and
empirical anchors they rest on. It does **not** specify implementation
details (no code, no YAML, no prompt strings).

Once a conforming target file exists and passes the §11 validation
checklist, the top-level pipeline `masim/skills/create-simulation-skill.md`
can consume it directly without any further interactive Q&A. Every
substantive design decision in `simulation-bases.md`, `analysis-bases.md`,
the variant folders chosen in §10.1, and any AGENT_POOL write-back can be
traced back to a numbered section of the target file.

The target file is **immutable** once locked. The pipeline records its
build log in a separate, sibling file (`simulation-define.md`) so that
the upstream target stays as the canonical statement of user intent.

---

## 1. Authority and Scope

| Concern                                          | Owner                                                  |
|--------------------------------------------------|--------------------------------------------------------|
| **Target file format and validation**            | **This skill** (`create-simulation-target-skill.md`)   |
| Pipeline orchestration                           | `masim/skills/create-simulation-skill.md`              |
| Per-step methodology (research → review → run)   | `masim/skills/create-example-skill/`                   |
| Universal per-agent specification                | `masim/skills/agent-design-skill.md`                   |
| Domain-instantiation rules (finance reference)   | `create-example-skill/02-root-documents-spec.md §4.1`  |

This file is the **single source of truth** for what a target file
must contain. The pipeline and the per-step skills *consume* it; they
MUST NOT redefine its sections, rename its fields, or add silent
defaults for missing entries.

If a target file is missing a required field, the pipeline blocks and
returns control to the author of the target file. Downstream skills
MUST NOT invent missing content.

---

## 2. File Naming and Location

| Rule                            | Value                                                                              |
|---------------------------------|------------------------------------------------------------------------------------|
| Path                            | `examples/{ScenarioName}/{domain}-{scenario}.md`                                   |
| `{ScenarioName}` (folder)       | PascalCase noun phrase, 2 — 4 tokens (e.g., `FlashCrash`, `CarryTradeUnwind`)      |
| `{domain}` (filename prefix)    | lowercase, kebab-case, one token (e.g., `finance`, `opinion`, `epidemics`, `sociology`) |
| `{scenario}` (filename suffix)  | lowercase, kebab-case, matches the PascalCase folder (e.g., `flash-crash`)         |
| Example                         | `examples/FlashCrash/finance-flash-crash.md`                                       |
| Example                         | `examples/EchoChamber/opinion-echo-chamber.md`                                     |
| Example                         | `examples/SuperSpreader/epidemics-super-spreader.md`                               |

If multiple target files attempt to share the same folder, the
pipeline halts and asks the author to merge or rename. Only one target
file may exist per `{ScenarioName}/`.

---

## 3. Mandatory Section Order

A conforming target file MUST contain **exactly the following ten
sections in this order**, with the exact headings shown. Authors MAY
extend a section with additional sub-headings, but MUST NOT delete a
section or change its number.

```
§1  Meta
§2  Phenomenon Statement
§3  Research Goals
§4  Theoretical Anchors
§5  Stylized Facts
§6  Historical / Empirical Anchors
§7  Agent Roster
§8  Environment Specification
§9  Parameter Seeds
§10 Variants and Success Criteria
```

Section-by-section requirements follow. Every requirement is
prefixed with **MUST**, **SHOULD**, or **MAY** to mark its enforcement
strength under §11 Validation.

---

### §1 Meta

A single table identifying the file:

```markdown
## §1 Meta

| Field        | Content                                                |
|--------------|--------------------------------------------------------|
| Name         | {PascalCase scenario name}                             |
| Domain       | finance / opinion / epidemics / sociology / ...        |
| Author       | {full name or organisation}                            |
| Created      | {YYYY-MM-DD}                                           |
| Pipeline     | masim/skills/create-simulation-skill.md                |
| Target Spec  | masim/skills/create-simulation-target-skill.md (v1.0)  |
| Status       | draft / locked / released                              |
```

- **MUST** match `{ScenarioName}` exactly in `Name`.
- **MUST** declare a `Domain` value that has (or will have) a
  corresponding `examples/AGENT_POOL/{domain}/` folder.
- **MUST** start with `Status: draft`; the pipeline upgrades to
  `locked` only after §11 validation passes.

---

### §2 Phenomenon Statement

Four mandatory sub-headings, each one paragraph (3 — 6 sentences):

```markdown
## §2 Phenomenon Statement

### §2.1 Trigger
[What specific initial condition sets the phenomenon in motion?]

### §2.2 Mechanism
[What self-reinforcing or dynamic process amplifies the initial trigger
into the observed phenomenon? Name the feedback loop.]

### §2.3 Participants
[Which categories of agents are causally involved? Name them in
domain-appropriate terms — investors, opinion leaders, infected nodes,
households, etc.]

### §2.4 Resolution
[How does the phenomenon end? What conditions terminate or reverse it?]
```

- **MUST** answer all four questions in concrete, non-tautological
  language. "Prices fall and people panic" is not acceptable; "A
  forced seller hits margin, prime brokers race to liquidate ahead of
  one another, cascading block sales depress prices further" is
  acceptable.
- **MUST NOT** reference implementation artefacts (no
  `simulation.yml`, no `players.py`, no `LLM/`).

---

### §3 Research Goals

A numbered list of **3 — 5 research questions** answerable via the
simulation. Each question must be falsifiable by some metric defined
later in §10.

```markdown
## §3 Research Goals

1. [Research question 1 — should be answerable by a single
   stylized-fact measurement, parameter sweep, or ablation.]
2. [Research question 2]
3. [Research question 3]
```

- **MUST** include at least one question that is answered by an
  **ablation** (turning one agent type off).
- **MUST** include at least one question that is answered by a
  **parameter sweep** (varying one numeric knob declared in §9).
- **SHOULD** include at least one question that compares two of the
  built variants (e.g., Rule vs LLM).

---

### §4 Theoretical Anchors

**3 — 6 theory entries.** Each entry uses the following exact template:

```markdown
### §4.{k} {Theory short name}

| Field                | Content                                                 |
|----------------------|---------------------------------------------------------|
| Full citation        | Author, A., & Author, B. ({year}). Title. *Journal*, vol(iss), pages. https://doi.org/... |
| Key mechanism (≤30 words) | [The single sentence summary of what the theory predicts.] |
| Key equation         | [LaTeX or plain-text form of the central formula, with all symbols defined inline.] |
| Motivates agent      | [Name of the agent in §7 that this theory primarily justifies.] |
| Parameter implication| [Which §9 knob this theory pins down, with a numeric range from the cited work.] |
```

- **MUST** cite a DOI or stable URL for every entry; preprint arXiv
  IDs are allowed only when the work has no published version.
- **MUST** have **one-to-one mapping** between §4 entries and §7 agent
  rows: every agent's primary theory MUST be a §4 entry, and every §4
  entry MUST motivate at least one §7 agent. A theory that motivates
  multiple agents is permitted but discouraged; if used, the
  `Motivates agent` field MUST list all of them.

---

### §5 Stylized Facts

**3 — 6 empirical regularities** that the simulation must reproduce.
Each fact is one row in the following table:

```markdown
## §5 Stylized Facts

| #  | Fact (one sentence)                                                 | Quantitative range            | Citation                                  | Acceptance metric                                   |
|----|---------------------------------------------------------------------|-------------------------------|-------------------------------------------|-----------------------------------------------------|
| F1 | [e.g., "Bubble peak exceeds fundamental by 40 — 80 %."]             | 1.4 ≤ peak/fundamental ≤ 1.8  | Smith (2018, JoF, 10.xxx/yyy)             | `analysis.py: bubble_peak_ratio()` ∈ [1.4, 1.8]     |
| F2 | ...                                                                 | ...                           | ...                                       | ...                                                 |
```

- **MUST** specify a numeric quantitative range for each fact (no
  vague "large", "fast", "many").
- **MUST** specify the acceptance metric in a form that `analysis.py`
  can implement (function name + numeric bound).
- **MUST** include at least one fact that is **dynamic** (depends on
  the trajectory shape — e.g., duration, peak timing, recovery slope)
  rather than purely cross-sectional.

---

### §6 Historical / Empirical Anchors

**1 — 3 real-world events or laboratory experiments** that the
simulation is calibrated against. Each entry uses:

```markdown
### §6.{k} {Event or experiment name}

| Field             | Content                                                          |
|-------------------|------------------------------------------------------------------|
| Name + dates      | [e.g., "1987 Black Monday — 1987-10-19"]                         |
| Trigger           | [What initiated this real event?]                                |
| Quantitative arc  | [Key numeric points: initial level, peak, trough, duration in real units.] |
| Agent mapping     | [Which real-world participants map to which §7 agent? One row per §7 agent.] |
| Primary source(s) | [Citations with DOIs.]                                            |
```

- **MUST** include at least one event that is *not* already used as a
  primary anchor by another scenario in `examples/`. (Run
  `ls examples/` and skim each `simulation-bases.md §1.1.2` to check.)
- **MUST** map every §7 agent to at least one historical participant
  type — agents that have no real-world counterpart are not allowed.

---

### §7 Agent Roster

A single table with **4 — 7 rows**, one per agent archetype:

```markdown
## §7 Agent Roster

| Agent name (kebab) | Real-world counterpart | Theory family (§4 anchor) | Market / domain role           | Primary signals                          | Intent line                                                 | Expected pool match              |
|--------------------|------------------------|---------------------------|--------------------------------|------------------------------------------|-------------------------------------------------------------|----------------------------------|
| trend-follower     | active retail trader   | Quant / Statistical (§4.2)| Destabilising                  | price, return, deviation                 | "Exists to amplify ongoing directional moves."              | examples/AGENT_POOL/finance/momentum-trader.md |
| fundamental-anchor | mutual fund            | Fundamental / Value (§4.1)| Stabilising                    | price, fundamental, deviation            | "Exists to pull price back toward intrinsic value."         | examples/AGENT_POOL/finance/fundamental-analyst.md |
| ...                | ...                    | ...                       | ...                            | ...                                      | ...                                                         | ...                              |
```

Column rules:

- **Agent name** MUST be lowercase kebab-case. It becomes the agent's
  H1 sentence-cased title (`Trend-following Investor`) in the
  AGENT_POOL file and the embedded §4.{N} title in `simulation-bases.md`.
- **Real-world counterpart** MUST come from the chosen domain's
  enumeration (for finance, see `02-root-documents-spec.md §4.1.2`;
  for other domains, see §4 of this file).
- **Theory family** MUST reference a specific §4.{k} anchor by number.
- **Domain role** MUST be one of `Stabilising`, `Destabilising`,
  `Context-dependent`.
- **Primary signals** MUST be a comma-separated list of at most three
  signal names; each signal MUST exist (or be requested) in §8.
- **Intent line** MUST start with `Exists to` and complete in one
  sentence without naming the scenario.
- **Expected pool match** SHOULD point at the most likely AGENT_POOL
  file for the chosen domain; use `(none — likely new)` if the author
  expects this to require a fresh design. The pipeline runs the formal
  three-stage match in Phase 3 regardless.

Diversity rules (enforced in §11 validation):

- **MUST** include at least one agent with `Stabilising` role and at
  least one with `Destabilising` role.
- **MUST NOT** repeat the same theory family across more than two
  agents (no taxonomy collapse).
- **SHOULD** include at least one agent that uses a non-price primary
  signal (volume, news, social, sentiment, fundamental, network).

---

### §8 Environment Specification

A description of the **world the agents inhabit**. This is
domain-specific. The target file MUST pick exactly one of the
sub-templates below based on the §1 `Domain`.

```markdown
## §8 Environment Specification
```

#### §8 sub-templates by domain

**§8 — Finance (`Domain: finance`)**

```markdown
### §8.1 Price Formation
[Choose: dealer market / order book / single-clearing-price; cite source.]

### §8.2 Information Broadcast
[List every field broadcast to agents each round, with a one-line justification.
 Standard fields: price, fundamental, deviation, round. Optional fields require justification.]

### §8.3 Constraints and Frictions
[Short-selling allowed? Margin? Circuit breakers? Trading hours? Each item
 marked Yes/No with rationale.]

### §8.4 Round Granularity
[What does one round represent in real time? Minutes / days / weeks?
 Cite the historical anchor that justifies the choice.]
```

**§8 — Opinion / Sociology (`Domain: opinion` or `sociology`)**

```markdown
### §8.1 Social Graph
[Static / dynamic; degree distribution; rewiring rule (if any); cite source.]

### §8.2 Communication Protocol
[Synchronous / asynchronous; payload type (binary opinion / continuous belief /
 categorical label); rate limits.]

### §8.3 Information Sources
[Exogenous news rate; trust weighting; misinformation channel.]

### §8.4 Round Granularity
[What does one round represent? Minutes of online activity / days / weeks?]
```

**§8 — Epidemics (`Domain: epidemics`)**

```markdown
### §8.1 Contact Network
[Population, contact graph topology, mixing rule, citation.]

### §8.2 Compartment Model
[SIR / SEIR / SEIRS / variant; transition rules with rates.]

### §8.3 Intervention Channels
[Vaccination / quarantine / testing capacity; activation triggers.]

### §8.4 Round Granularity
[Per-day / per-week, with seasonality?]
```

**§8 — Other domains**

The target file MUST add a new domain sub-template here in a follow-up
revision before the pipeline can build the scenario. Until then,
`Status: draft` cannot be upgraded to `locked`.

- **MUST** justify each environment element with a citation or a
  pointer to a §4 theory.
- **MUST NOT** include agent-specific decision logic in §8. Agent
  logic belongs in §7 (the roster) and the downstream
  `simulation-bases.md §4.{N}` blocks.

---

### §9 Parameter Seeds

A single table of every numeric knob that downstream code will need a
default for. Each row is one knob:

```markdown
## §9 Parameter Seeds

| Parameter      | Symbol | Belongs to (agent / market) | Empirical range          | Candidate default | Source citation                       |
|----------------|--------|-----------------------------|--------------------------|-------------------|---------------------------------------|
| price impact   | λ      | market (§8.1)               | 0.01 — 0.05              | 0.03              | Hasbrouck (1991), JoF, 10.xxx/yyy     |
| momentum gain  | α      | trend-follower (§7)         | 0.2 — 0.4 per round      | 0.30              | Jegadeesh & Titman (1993), JoF, 10... |
| ...            | ...    | ...                         | ...                      | ...               | ...                                   |
```

- **MUST** have a `Belongs to` field that resolves to either a §7
  agent name or a §8 sub-section.
- **MUST** cite a primary source for every empirical range; no
  "estimated", no "typical value used in prior work".
- **MAY** mark a knob as `Source: normalization` only for pure scale
  parameters (e.g., `initial_price = 100`); the §11 checklist caps
  these at 10 % of the table.

---

### §10 Variants and Success Criteria

Two sub-sections:

```markdown
## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant   | Build? | Rationale (≤1 sentence)                                 |
|-----------|--------|---------------------------------------------------------|
| Rule      | Yes    | Required baseline                                        |
| LLM       | Yes / No | [Why, citing a research goal from §3 that needs LLM.]  |
| RuleLLM   | Yes / No | [Why, citing a research goal that needs the hybrid.]   |
| Rag       | Yes / No | [Why, citing the §6 historical anchors as the corpus.] |

### §10.2 Pass / Fail Criteria

| Criterion                                              | Status when satisfied                                 |
|--------------------------------------------------------|-------------------------------------------------------|
| All §5 stylized facts reproduced within their ranges   | green                                                 |
| Every §3 research question answerable from analysis    | green                                                 |
| Ablating any §7 agent produces a measurable change     | green                                                 |
| All variants marked `Yes` in §10.1 build without uncaught exceptions | green                                                 |
```

- **MUST** mark at least one variant as `Yes`. Building only the
  `Rule` variant is allowed for prototypes but the pipeline records
  the scenario as `prototype` rather than `released`.
- **MUST** specify all four success criteria; authors MAY add more.

---

## 4. Domain-Instantiation Rules (Brief)

The target file's §7, §8, §9 require domain-specific value palettes.
Authors MUST pick palettes from the per-domain registry:

| Domain     | Theory family palette                          | Real-world counterpart palette                | Environment template     |
|------------|------------------------------------------------|-----------------------------------------------|--------------------------|
| finance    | `02-root-documents-spec.md §4.1.1`             | `02-root-documents-spec.md §4.1.2`            | §8 — Finance sub-template above |
| opinion    | *(to be defined in a sibling appendix)*        | *(to be defined)*                              | §8 — Opinion sub-template above |
| epidemics  | *(to be defined in a sibling appendix)*        | *(to be defined)*                              | §8 — Epidemics sub-template above |
| sociology  | *(to be defined; may extend `opinion`)*        | *(to be defined)*                              | §8 — Opinion sub-template above |

For any domain whose palette has not been written yet, the target
file MUST include an **§A Domain Palette Appendix** that supplies the
three palettes (theory family list, counterpart enumeration, stylized
fact catalogue) before `Status` can move from `draft` to `locked`. The
appendix becomes a candidate for promotion into `02-root-documents-spec.md`
as the project's domain catalogue grows.

---

## 5. Style and Wording Rules

- **MUST** use UTF-8 plain Markdown; no `\u200b`, no smart quotes, no
  em dashes (use commas, parentheses, or semicolons).
- **MUST** use the exact section numbers `§1 — §10`. Sub-sections use
  decimal numbering (`§2.1`, `§4.3`).
- **MUST NOT** include implementation specifics (no Python class names,
  no YAML keys, no CLI commands, no prompt text).
- **MUST NOT** reference any other scenario by name except in §6 (when
  citing a historical event) or in §11 (distinctiveness check).
- **MAY** include figures or diagrams as image references; embedded
  Mermaid is allowed.

---

## 6. The Target File vs. the Pipeline Contract

The pipeline `create-simulation-skill.md` maintains a separate file —
`examples/{ScenarioName}/simulation-define.md` — as its **build log
and gate-record contract**. The relationship is:

```text
{domain}-{scenario}.md            ←  Authored by user / upstream LLM
   │                                  Immutable once locked
   │                                  Spec: this file
   ▼
simulation-define.md              ←  Authored by the pipeline
                                      Refers to the target file by section number
                                      Adds §A AGENT_POOL gate log
                                      Adds §C Open questions accumulated during research
                                      Adds §D Build log (one row per pipeline phase)
```

The pipeline MUST NOT alter the target file. If during research the
pipeline discovers a defect in the target file (e.g., a citation does
not resolve), it raises the defect to the author via
`AskUserQuestion`; the author edits the target file, increments its
`Created` date to `Created / Revised`, and re-locks. The pipeline then
re-validates.

---

## 7. Versioning Rules

- The first authored version of a target file MUST set
  `Status: draft`. The author runs §11 validation locally and only
  then submits the file to the pipeline.
- The pipeline upgrades `Status: draft → locked` only after §11
  validation passes inside the pipeline (the pipeline re-runs the
  check; trust but verify).
- After `Status: locked`, any change to the target file requires the
  author to set `Status: draft` again and to add a `Revised: YYYY-MM-DD`
  field beneath `Created` in §1.
- The pipeline upgrades `Status: locked → released` only when Phase 6
  of `create-simulation-skill.md` completes the smoke test
  successfully.

---

## 8. Worked Example: Skeleton in Practice

The following is the **complete shape** of a conforming target file
for a finance scenario. It is illustrative only — real content
omitted.

```markdown
# Carry Trade Unwind — Scenario Target

## §1 Meta

| Field        | Content                                                |
|--------------|--------------------------------------------------------|
| Name         | CarryTradeUnwind                                       |
| Domain       | finance                                                |
| Author       | Sijia Chen                                             |
| Created      | 2026-06-29                                             |
| Pipeline     | masim/skills/create-simulation-skill.md                |
| Target Spec  | masim/skills/create-simulation-target-skill.md (v1.0)  |
| Status       | draft                                                  |

## §2 Phenomenon Statement

### §2.1 Trigger
...

### §2.2 Mechanism
...

### §2.3 Participants
...

### §2.4 Resolution
...

## §3 Research Goals

1. ...
2. ...
3. ...

## §4 Theoretical Anchors

### §4.1 Funding-Liquidity Spiral
| Field | Content |
| ... | ... |

### §4.2 ...

## §5 Stylized Facts

| #  | Fact | Quantitative range | Citation | Acceptance metric |
| ...|

## §6 Historical / Empirical Anchors

### §6.1 2024 Yen Carry Unwind
| Field | Content |
| ... | ... |

## §7 Agent Roster

| Agent name | Real-world counterpart | Theory family | Market role | Primary signals | Intent line | Expected pool match |
| ...|

## §8 Environment Specification

### §8.1 Price Formation
...

### §8.2 Information Broadcast
...

### §8.3 Constraints and Frictions
...

### §8.4 Round Granularity
...

## §9 Parameter Seeds

| Parameter | Symbol | Belongs to | Empirical range | Candidate default | Source |
| ...|

## §10 Variants and Success Criteria

### §10.1 Variants to Build
| Variant | Build? | Rationale |
| ...|

### §10.2 Pass / Fail Criteria
| Criterion | Status when satisfied |
| ...|
```

For full, fully-populated examples, see (once available):

- `examples/AssetBubble/finance-asset-bubble.md` (reference, finance)
- `examples/EchoChamber/opinion-echo-chamber.md` (reference, opinion)

If no fully-populated reference exists for the chosen domain, the
author SHOULD propose to add one in the same revision.

---

## 9. Authoring Workflow (for a Human + LLM Pair)

A typical authoring loop with an LLM assistant looks like:

1. **Pick scenario name and domain.** Decide `{ScenarioName}` and
   `{domain}`. Confirm the folder `examples/{ScenarioName}/` does not
   yet exist.
2. **Draft §1 — §2.** The human gives a one-paragraph phenomenon
   sketch; the LLM expands it into the four §2 sub-headings.
3. **Draft §3 Research Goals.** The LLM proposes 4 — 5 research
   questions; the human picks 3 — 5 and marks which is the
   ablation / sweep / variant comparison.
4. **Draft §4 Theoretical Anchors.** The LLM searches for canonical
   theories and produces DOI-cited entries; the human verifies each
   DOI resolves and trims to 3 — 6.
5. **Draft §5 Stylized Facts.** The LLM proposes facts grounded in
   the cited theories; the human ensures each has a numeric range
   and a concrete acceptance metric.
6. **Draft §6 Historical Anchors.** The human picks 1 — 3 events; the
   LLM looks up dates and quantitative arcs.
7. **Draft §7 Agent Roster.** The LLM proposes 4 — 7 agents and maps
   each to an AGENT_POOL candidate by browsing
   `examples/AGENT_POOL/{domain}/`; the human edits.
8. **Draft §8 Environment.** Pick the domain sub-template and fill it.
9. **Draft §9 Parameter Seeds.** The LLM emits a parameter table
   with citations from §4; the human verifies sources.
10. **Draft §10 Variants and Success Criteria.** The human picks the
    variant set; the LLM mirrors the §3 — §5 anchors into the
    pass/fail table.
11. **Run §11 Validation.** The human (or a separate LLM reviewer)
    runs every checklist item. Failures return to the relevant
    section.
12. **Submit to pipeline.** The human (or the LLM) saves with
    `Status: draft` and invokes `create-simulation-skill.md`. The
    pipeline re-validates and, on success, upgrades to `locked`.

The pipeline never starts before step 12.

---

## 10. Anti-Patterns (Reject on Sight)

- **Implementation creep.** Any line that names a Python class, a
  YAML key, a config path, or a prompt string. → Strip it; that
  belongs in `simulation-bases.md` or `explain.md`.
- **Hand-wavy ranges.** "α is small", "λ is moderate", "high
  volatility". → Replace with a numeric interval and a citation.
- **Free-text agents.** A §7 agent without a §4 theory anchor or
  without a §8 signal. → Either ground the agent or remove it.
- **Domain mixing.** A `Domain: finance` file with §7 agents whose
  real-world counterparts are exclusively from
  `02-root-documents-spec.md §4.1.2`'s sociology list (or vice
  versa). → Re-pick the domain or move the agent.
- **Stylized fact without metric.** "Bubbles get big." → Replace with
  "peak/fundamental ∈ [1.4, 1.8] within 6 — 18 rounds, F1 in §5".
- **Recycled history.** Using `1987 Black Monday` as the §6 anchor
  while it is already the primary anchor of `examples/AssetBubble/`.
  → Pick a less-used event or extend the existing scenario instead.
- **Phantom citations.** A DOI that does not resolve, an APA entry
  without the article title. → Replace with a verified citation.
- **Locked-without-validation.** Setting `Status: locked` manually
  without running §11. → Only the pipeline upgrades the status.

---

## 11. Validation Checklist

Every item is a blocker. Run all items. Three consecutive PASS runs
are required, in the style of `agent-design-skill.md §6` and
`create-simulation-skill.md §6.4`.

**Structural completeness**

- [ ] All ten sections §1 — §10 are present in order.
- [ ] §1 Meta has every row filled; `Status` is `draft`.
- [ ] §2 has all four sub-headings (Trigger, Mechanism, Participants,
      Resolution), each with at least three sentences.
- [ ] §3 lists 3 — 5 numbered research questions; one is an ablation,
      one is a sweep.
- [ ] §4 has 3 — 6 theory entries, each with the five-row table.
- [ ] §5 has 3 — 6 stylized-fact rows, each with a numeric range and
      an acceptance metric.
- [ ] §6 has 1 — 3 anchor entries with quantitative arcs.
- [ ] §7 has 4 — 7 agent rows with all seven columns.
- [ ] §8 picks the correct domain sub-template and fills every
      sub-section.
- [ ] §9 lists every parameter that will appear in `simulation-bases.md
      §6`, each with a cited empirical range.
- [ ] §10.1 marks at least one variant `Yes`; §10.2 lists the four
      success criteria.

**Cross-section consistency**

- [ ] Every §7 agent's `Theory family` references an existing §4.{k}.
- [ ] Every §4 theory motivates at least one §7 agent.
- [ ] Every §7 agent's `Primary signals` are declared in §8 (or
      requested as broadcast fields).
- [ ] Every §9 parameter `Belongs to` resolves to a §7 agent name or
      a §8 sub-section.
- [ ] Every §5 stylized fact's `Acceptance metric` references a
      function name compatible with the §10.1 variants.

**Evidence provenance**

- [ ] Every §4 theory cites a resolvable DOI / stable URL.
- [ ] Every §5 stylized fact cites a primary source.
- [ ] Every §6 historical anchor cites a primary source.
- [ ] Every §9 parameter empirical range cites a primary source.
- [ ] At most 10 % of §9 rows are marked `Source: normalization`.

**Domain compatibility**

- [ ] `examples/AGENT_POOL/{Domain}/` exists, OR the file includes
      `§A Domain Palette Appendix` with the three required palettes.
- [ ] §7 real-world counterparts all come from the chosen domain's
      enumeration.
- [ ] §8 sub-template matches the chosen domain.

**Distinctiveness**

- [ ] Scenario name does not collide with any folder under
      `examples/`.
- [ ] §6 historical anchor is not already the primary anchor of an
      existing scenario.
- [ ] At least two §7 agents differ from those already used as
      primary archetypes in any existing scenario.

**Style hygiene**

- [ ] No em dashes; no implementation specifics; no free-text
      agents; no hand-wavy ranges.
- [ ] All file paths use forward slashes and are rooted at
      `masim/skills/...` or `examples/...`.

A run is **PASS** if every box is checked. **FAIL** if any box is
unchecked. Three consecutive PASS runs are required before the
target file is considered ready for the pipeline. After the third
PASS, the author leaves `Status: draft` and lets the pipeline
upgrade.

---

## 12. Skill References

| Topic                                       | File                                                              |
|---------------------------------------------|-------------------------------------------------------------------|
| Top-level pipeline (consumes this file)     | `masim/skills/create-simulation-skill.md`                         |
| Per-step methodology                        | `masim/skills/create-example-skill/`                              |
| Universal Agent Design Handbook             | `masim/skills/agent-design-skill.md`                              |
| Domain-instantiation rules (finance)        | `masim/skills/create-example-skill/02-root-documents-spec.md §4.1` |
| Step 0 contract template                    | `masim/skills/create-example-skill/04-step0-define.md`            |
| AGENT_POOL directory                        | `examples/AGENT_POOL/`                                            |
| Project structure overview                  | `docs/structure.md`                                               |

---

## 13. Status

| Field   | Content                                            |
|---------|----------------------------------------------------|
| Version | 1.0.0                                              |
| Created | 2026-06-29                                         |
| Status  | canonical                                          |
