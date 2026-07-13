---
name: define-simulation-scenario-skill
purpose: An **executable skill** that produces the upstream target file `{domain}-{scenario}.md` given minimal user inputs (scenario name + phenomenon sketch + domain). The generated file is the single upstream artefact that drives every downstream skill in `masim/skills/` (the top-level pipeline `create-simulation-pipeline.md`, the per-step guides `implement-simulation-skill/`, and the per-agent handbook `agent-design-skill.md`). The user MUST NOT hand-author the target file; instead, the invoking LLM agent runs this skill and produces the file end-to-end.
status: canonical
audience: The invoking LLM agent that runs this skill on the user's behalf; the user who supplies the minimal inputs; reviewers that re-validate the produced file before the pipeline consumes it.
rfc2119: This document uses MUST / MUST NOT / SHOULD / MAY in the RFC-2119 sense.
invocation: An LLM agent runs this skill by (a) collecting minimal inputs from the user (see §9 Skill Invocation Workflow), (b) generating every §1 — §10 section per the spec below, (c) running §11 validation three consecutive times, and (d) writing the final file to `examples/{ScenarioName}/{domain}-{scenario}.md` with `Status: draft`. Downstream skills MUST NOT begin scenario construction until the produced file passes §11 validation.
---

# Define-Simulation-Scenario-Skill — Executable Skill for Producing the Scenario Target File

## 0. What This Skill Defines

This skill is **executable**: an invoking LLM agent runs it end-to-end
to **produce** a single upstream file, given minimal user inputs
(scenario name, domain, and a short phenomenon sketch). The output is
written to:

```
examples/{ScenarioName}/{domain}-{scenario}.md
```

Throughout this document we call this file the **scenario target
file**, or simply the **target file**. Users MUST NOT hand-author the
target file. The user's role is limited to (i) supplying the minimal
inputs listed in §9.1 and (ii) confirming the invoking agent's
research results at a small number of interactive checkpoints
described in §9.2. The invoking agent — not the user — is responsible
for expanding the sketch into every §1 — §10 section, running the
research needed to fill in citations and numeric ranges, and writing
the final file.

The produced target file declares — in a uniform, machine-readable,
peer-reviewable form — *what* the simulation must achieve, *which*
phenomena it must reproduce, *which* agents must appear, *which*
environment they live in, and *which* numeric and empirical anchors
they rest on. It does **not** specify implementation details (no code,
no YAML, no prompt strings).

Once a conforming target file exists and passes the §11 validation
checklist, the top-level pipeline `masim/skills/create-simulation-pipeline.md`
can consume it directly without any further interactive Q&A. Every
substantive design decision in `simulation-bases.md`, `analysis-bases.md`,
the variant folders chosen in §10.1, and any AGENT_POOL write-back can be
traced back to a numbered section of the target file.

The target file is **immutable** once locked. The pipeline records its
build log in a separate, sibling file (`simulation-build-log.md`) so that
the upstream target stays as the canonical statement of user intent.

---

## 1. Authority and Scope

| Concern                                            | Owner                                                       |
|----------------------------------------------------|-------------------------------------------------------------|
| **Target file production, format, and validation** | **This skill** (`define-simulation-scenario-skill.md`)      |
| Pipeline orchestration                             | `masim/skills/create-simulation-pipeline.md`                |
| Per-step methodology (research → review → run)     | `masim/skills/implement-simulation-skill/`                  |
| Universal per-agent specification                  | `masim/skills/agent-design-skill.md`                        |
| Domain-instantiation rules (finance reference)     | `implement-simulation-skill/02-root-documents-spec.md §4.1` |

This file is the **single source of truth** for what a target file
must contain and how it is produced. The pipeline and the per-step
skills *consume* the produced target file; they MUST NOT redefine its
sections, rename its fields, or add silent defaults for missing
entries.

If the invoking agent cannot fill a required field (e.g., no
resolvable DOI for a needed theory), it MUST NOT write the file with a
placeholder or a silent default. Instead, it raises the gap to the
user via `AskUserQuestion`, resolves it, and only then writes the
section. Downstream skills MUST NOT invent missing content.

---

## 2. File Naming and Location

| Rule                           | Value                                                                                   |
|--------------------------------|-----------------------------------------------------------------------------------------|
| Path                           | `examples/{ScenarioName}/{domain}-{scenario}.md`                                        |
| `{ScenarioName}` (folder)      | PascalCase noun phrase, 2 — 4 tokens (e.g., `FlashCrash`, `CarryTradeUnwind`)           |
| `{domain}` (filename prefix)   | lowercase, kebab-case, one token (e.g., `finance`, `opinion`, `epidemics`, `sociology`) |
| `{scenario}` (filename suffix) | lowercase, kebab-case, matches the PascalCase folder (e.g., `flash-crash`)              |
| Example                        | `examples/FlashCrash/finance-flash-crash.md`                                            |
| Example                        | `examples/EchoChamber/opinion-echo-chamber.md`                                          |
| Example                        | `examples/SuperSpreader/epidemics-super-spreader.md`                                    |

If multiple target files attempt to share the same folder, the
pipeline halts and asks the user to merge or rename (via a fresh
invocation of this skill). Only one target file may exist per
`{ScenarioName}/`.

---

## 3. Mandatory Section Order

A conforming target file MUST contain **exactly the following ten
sections in this order**, with the exact headings shown. The invoking
agent MAY extend a section with additional sub-headings, but MUST NOT
delete a section or change its number.

The file MUST NOT introduce any top-level `## §N` heading other than
§1 — §10. No `§0`, no `§11`, no unnumbered `##` headings. Auxiliary
content (changelogs, traceability matrices, build audit trails) MUST
be recorded in the sibling `simulation-build-log.md`, never inside the
target file itself (see §6 "The Target File vs. the Pipeline
Contract").

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
strength under §11 Validation. Requirements bind the invoking agent
that produces the file; the user is only responsible for the minimal
inputs collected in §9.1 and for confirming the checkpoint outputs
listed in §9.2.

---

### §1 Meta

A single table identifying the file:

```markdown
## §1 Meta

| Field        | Content                                                                                |
|--------------|----------------------------------------------------------------------------------------|
| Name         | {PascalCase scenario name}                                                             |
| Domain       | finance / opinion / epidemics / sociology / ...                                        |
| Requested By | {human user's full name or organisation}                                               |
| Produced By  | define-simulation-scenario-skill.md v{X.Y.Z} (invoking agent: {model / harness label}) |
| Created      | {YYYY-MM-DD}                                                                           |
| Pipeline     | masim/skills/create-simulation-pipeline.md                                             |
| Target Spec  | masim/skills/define-simulation-scenario-skill.md (v1.0)                                |
| Status       | draft / locked / released                                                              |
```

- **MUST** match `{ScenarioName}` exactly in `Name`.
- **MUST** declare a `Domain` value that has (or will have) a
  corresponding `examples/AGENT_POOL/{domain}/` folder.
- **MUST** record the human user in `Requested By` and the invoking
  skill + agent in `Produced By`. The user does NOT hand-author the
  file.
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
  language. "Prices fall and people panic" is not acceptable
  (finance-appendix example); "A forced seller hits margin, prime
  brokers race to liquidate ahead of one another, cascading block
  sales depress prices further" (finance-appendix example) is
  acceptable. Non-finance analogue: "A super-spreader event seeds a
  cluster; local cases exceed hospital-triage capacity, staff shift
  to acute care and delay testing, undetected transmission chains
  extend into low-immunity groups" (epidemics-appendix example) is
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
  built variants declared in §10.1 (finance-default example: Rule vs
  LLM; opinion-default example: bounded-confidence baseline vs LLM
  persona variant).

---

### §4 Theoretical Anchors

**3 — 6 theory entries.** Each entry uses the following exact template:

```markdown
### §4.{k} {Theory short name}

| Field                     | Content                                                                                   |
|---------------------------|-------------------------------------------------------------------------------------------|
| Full citation             | Author, A., & Author, B. ({year}). Title. *Journal*, vol(iss), pages. https://doi.org/... |
| Key mechanism (≤30 words) | [The single sentence summary of what the theory predicts.]                                |
| Key equation              | [LaTeX or plain-text form of the central formula, with all symbols defined inline.]       |
| Motivates agent           | [Name of the agent in §7 that this theory primarily justifies.]                           |
| Parameter implication     | [Which §9 knob this theory pins down, with a numeric range from the cited work.]          |
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

| #  | Fact (one sentence)                                                        | Quantitative range           | Citation                      | Acceptance metric                               |
|----|----------------------------------------------------------------------------|------------------------------|-------------------------------|-------------------------------------------------|
| F1 | (finance-appendix example) "Bubble peak exceeds fundamental by 40 — 80 %." | 1.4 ≤ peak/fundamental ≤ 1.8 | Smith (2018, JoF, 10.xxx/yyy) | `analysis.py: bubble_peak_ratio()` ∈ [1.4, 1.8] |
| F2 | ...                                                                        | ...                          | ...                           | ...                                             |
```

<!--
Non-finance instantiations of §5 stylized-fact rows (illustrative):

  Opinion domain:
    | F1 | "Opinion distribution bimodalises within 40 — 80 rounds." | bimodality coefficient ≥ 0.55 | Baldassarri & Bearman (2007, ASR, 10.xxx/yyy) | analysis.py: bimodality_coefficient() ≥ 0.55 |

  Epidemics domain:
    | F1 | "Peak infected fraction reaches 8 — 15 % of population." | 0.08 ≤ peak_infected ≤ 0.15 | Ferguson et al. (2020, Nature, 10.xxx/yyy) | analysis.py: peak_infected_fraction() ∈ [0.08, 0.15] |

  Sociology domain:
    | F1 | "Adoption S-curve reaches 50 % between rounds 20 — 40." | 20 ≤ round(adoption ≥ 0.5) ≤ 40 | Rogers (2003, DoI 5th ed.) | analysis.py: adoption_midpoint_round() ∈ [20, 40] |
-->


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

| Field             | Content                                                                      |
|-------------------|------------------------------------------------------------------------------|
| Name + dates      | [e.g., "1987 Black Monday — 1987-10-19"]                                     |
| Trigger           | [What initiated this real event?]                                            |
| Quantitative arc  | [Key numeric points: initial level, peak, trough, duration in real units.]   |
| Agent mapping     | [Which real-world participants map to which §7 agent? One row per §7 agent.] |
| Primary source(s) | [Citations with DOIs.]                                                       |
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

| Agent name (kebab) | Real-world counterpart | Theory family (§4 anchor)  | Domain role   | Primary signals               | Intent line                                         | Expected pool match                                |
|--------------------|------------------------|----------------------------|---------------|-------------------------------|-----------------------------------------------------|----------------------------------------------------|
| trend-follower     | active retail trader   | Quant / Statistical (§4.2) | Destabilising | price, return, deviation      | "Exists to amplify ongoing directional moves."      | examples/AGENT_POOL/finance/momentum-trader.md     |
| fundamental-anchor | mutual fund            | Fundamental / Value (§4.1) | Stabilising   | price, fundamental, deviation | "Exists to pull price back toward intrinsic value." | examples/AGENT_POOL/finance/fundamental-analyst.md |
| ...                | ...                    | ...                        | ...           | ...                           | ...                                                 | ...                                                |
```

<!--
Non-finance instantiations of the §7 Agent Roster (illustrative — the invoking agent adapts columns to the chosen §1 Domain):

  Opinion domain:
    | echo-amplifier    | partisan influencer      | Bounded Confidence (§4.1) | Destabilising | opinion, network-neighbour opinions | "Exists to reinforce like-minded views."           | examples/AGENT_POOL/opinion/echo-amplifier.md    |
    | bridge-moderator  | cross-community journalist | Deliberative Democracy (§4.2) | Stabilising | opinion, out-group signals         | "Exists to bring dissonant views into contact."    | examples/AGENT_POOL/opinion/bridge-moderator.md  |

  Epidemics domain:
    | high-mixer        | frontline service worker | Contact Heterogeneity (§4.1) | Destabilising | contact_rate, symptom, testing     | "Exists to sustain many daily contacts."           | examples/AGENT_POOL/epidemics/high-mixer.md      |
    | cautious-isolator | vulnerable resident      | Behavioural Response (§4.2)  | Stabilising   | prevalence, symptom, testing        | "Exists to reduce exposure when risk is high."     | examples/AGENT_POOL/epidemics/cautious-isolator.md |

  Sociology domain:
    | early-adopter     | urban innovator          | Threshold Model (§4.1)      | Destabilising | neighbour-adoption, media          | "Exists to trigger cascades at low thresholds."     | examples/AGENT_POOL/sociology/early-adopter.md   |
    | conformist        | community elder          | Social Proof (§4.2)         | Stabilising   | neighbour-adoption                 | "Exists to hold out until majority adoption."       | examples/AGENT_POOL/sociology/conformist.md      |
-->


Column rules:

- **Agent name** MUST be lowercase kebab-case. It becomes the agent's
  H1 sentence-cased title (finance-appendix example: `Trend-following Investor`;
  opinion-appendix example: `Echo Amplifier`) in the AGENT_POOL file
  and the embedded §4.{N} title in `simulation-bases.md`.
- **Real-world counterpart** MUST come from the chosen domain's
  enumeration (for finance, see `02-root-documents-spec.md §4.1.2`;
  for other domains, see §4 of this file — the invoking agent MUST
  either point to an existing palette or produce an §A Domain Palette
  Appendix).
- **Theory family** MUST reference a specific §4.{k} anchor by number.
- **Domain role** MUST be one of `Stabilising`, `Destabilising`,
  `Context-dependent`. The role describes the agent's effect on the
  environment-state trajectory (finance-appendix example: destabilising
  = amplifies price moves away from fundamentals; opinion-appendix
  example: destabilising = polarises opinion distribution; epidemics-appendix
  example: destabilising = increases effective reproduction number).
- **Primary signals** MUST be a comma-separated list of at most three
  signal names; each signal MUST exist (or be requested) in §8.
- **Intent line** MUST start with `Exists to` and complete in one
  sentence without naming the scenario.
- **Expected pool match** SHOULD point at the most likely AGENT_POOL
  file for the chosen domain; use `(none — likely new)` if the
  invoking agent expects this to require a fresh design. The pipeline
  runs the formal
  three-stage match in Phase 3 regardless.

Diversity rules (enforced in §11 validation):

- **MUST** include at least one agent with `Stabilising` role and at
  least one with `Destabilising` role.
- **MUST NOT** repeat the same theory family across more than two
  agents (no taxonomy collapse).
- **SHOULD** include at least one agent that uses a non-state primary
  signal — i.e., a signal that is not the environment's headline state
  variable (finance-appendix example: not `price`; opinion-appendix
  example: not the agent's own opinion). Candidate categories: volume,
  news, social, sentiment, fundamental, network, contact, symptom.

---

### §8 Environment Specification

A description of the **world the agents inhabit**. This is
domain-specific. The invoking agent MUST pick exactly one of the
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

For a domain whose sub-template is not listed above, the invoking
agent MUST first extend this skill with a new domain sub-template (in
a follow-up revision) before it can produce a valid target file for
that domain. Until then, the invoking agent MUST NOT emit the target
file with `Status: draft` — it MUST halt and ask the user to authorise
the palette extension.

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

| Parameter                   | Symbol | Belongs to (agent / environment) | Empirical range     | Candidate default | Source citation                       |
|-----------------------------|--------|----------------------------------|---------------------|-------------------|---------------------------------------|
| price impact (finance ex.)  | λ      | environment (§8.1)               | 0.01 — 0.05         | 0.03              | Hasbrouck (1991), JoF, 10.xxx/yyy     |
| momentum gain (finance ex.) | α      | trend-follower (§7)              | 0.2 — 0.4 per round | 0.30              | Jegadeesh & Titman (1993), JoF, 10... |
| ...                         | ...    | ...                              | ...                 | ...               | ...                                   |
```

<!--
Non-finance instantiations of §9 parameter rows (illustrative):

  Opinion domain:
    | confidence bound       | ε      | echo-amplifier (§7)      | 0.15 — 0.35              | 0.25   | Deffuant et al. (2000, ACS, 10.xxx/yyy)   |
    | opinion update rate    | μ      | environment (§8.2)       | 0.20 — 0.50              | 0.30   | Hegselmann & Krause (2002, JASSS)         |

  Epidemics domain:
    | transmission rate      | β      | environment (§8.2)       | 0.15 — 0.35 per contact  | 0.25   | Ferguson et al. (2006, Nature, 10.xxx/yyy)|
    | recovery rate          | γ      | environment (§8.2)       | 0.10 — 0.20 per day      | 0.14   | Anderson & May (1991, ID Dynamics)        |

  Sociology domain:
    | adoption threshold     | θ      | conformist (§7)          | 0.30 — 0.60              | 0.50   | Granovetter (1978, AJS, 10.xxx/yyy)        |
-->


- **MUST** have a `Belongs to` field that resolves to either a §7
  agent name or a §8 environment sub-section.
- **MUST** cite a primary source for every empirical range; no
  "estimated", no "typical value used in prior work".
- **MAY** mark a knob as `Source: normalization` only for pure scale
  parameters (finance-appendix example: `initial_price = 100`;
  epidemics-appendix example: `population_size = 10000`); the §11
  checklist caps these at 10 % of the table.

---

### §10 Variants and Success Criteria

Two sub-sections:

```markdown
## §10 Variants and Success Criteria

### §10.1 Variants to Build

The variant set is **declared here** and drives every downstream
skill (`create-simulation-pipeline.md`, the per-step guides, the
polish audit). The invoking agent MUST populate the table with rows
drawn from the chosen domain's variant palette. The finance-default
palette contains four rows (`Rule` / `LLM` / `RuleLLM` / `Rag`); other
domains MAY drop, rename, or add rows so long as at least one
deterministic-baseline variant remains marked `Yes`.

| Variant        | Build?   | Rationale (≤1 sentence)                                           |
|----------------|----------|-------------------------------------------------------------------|
| {V1 baseline}  | Yes      | Required deterministic baseline (finance-default: Rule).          |
| {V2 LLM-based} | Yes / No | [Why, citing a §3 research goal that needs an LLM-based variant.] |
| {V3 hybrid}    | Yes / No | [Why, citing a §3 research goal that needs the hybrid.]           |
| {V4 retrieval} | Yes / No | [Why, citing §6 historical anchors as the retrieval corpus.]      |

<details>
<summary>Finance-appendix (§4.1.F) instantiation — default four-variant scheme</summary>

| Variant | Build?   | Rationale (≤1 sentence)                                |
|---------|----------|--------------------------------------------------------|
| Rule    | Yes      | Required baseline                                      |
| LLM     | Yes / No | [Why, citing a research goal from §3 that needs LLM.]  |
| RuleLLM | Yes / No | [Why, citing a research goal that needs the hybrid.]   |
| Rag     | Yes / No | [Why, citing the §6 historical anchors as the corpus.] |

</details>

<!--
Non-finance instantiations of §10.1 (illustrative — the invoking agent chooses a variant palette that fits the domain and its §3 research goals):

  Opinion domain (typical): Rule (bounded-confidence baseline) / LLM (persona-driven speech acts) / RuleLLM (rule-guided persona) — Rag optional if a discourse corpus exists.

  Epidemics domain (typical): Rule (compartmental / mechanistic baseline) / LLM (behavioural-response reasoning) — RuleLLM optional; Rag rarely used unless a public-health-guideline corpus is available.

  Sociology domain (typical): Rule (threshold / social-proof baseline) / LLM (narrative-driven adoption reasoning) — RuleLLM and Rag optional depending on §3 research goals.
-->

### §10.2 Pass / Fail Criteria

| Criterion                                                            | Status when satisfied |
|----------------------------------------------------------------------|-----------------------|
| All §5 stylized facts reproduced within their ranges                 | green                 |
| Every §3 research question answerable from analysis                  | green                 |
| Ablating any §7 agent produces a measurable change                   | green                 |
| All variants marked `Yes` in §10.1 build without uncaught exceptions | green                 |
```

- **MUST** mark at least one variant as `Yes`. Building only the
  deterministic-baseline variant (finance-default: `Rule`) is allowed
  for prototypes; the invoking agent records the scenario as
  `prototype` in `Status` rather than allowing it to progress to
  `released`.
- **MUST** specify all four success criteria; the invoking agent MAY
  add more when the user's phenomenon sketch demands them.

---

## 4. Domain-Instantiation Rules (Brief)

The target file's §7, §8, §9 require domain-specific value palettes.
The invoking agent MUST pick palettes from the per-domain registry:

| Domain    | Theory family palette                   | Real-world counterpart palette     | Environment template              |
|-----------|-----------------------------------------|------------------------------------|-----------------------------------|
| finance   | `02-root-documents-spec.md §4.1.1`      | `02-root-documents-spec.md §4.1.2` | §8 — Finance sub-template above   |
| opinion   | *(to be defined in a sibling appendix)* | *(to be defined)*                  | §8 — Opinion sub-template above   |
| epidemics | *(to be defined in a sibling appendix)* | *(to be defined)*                  | §8 — Epidemics sub-template above |
| sociology | *(to be defined; may extend `opinion`)* | *(to be defined)*                  | §8 — Opinion sub-template above   |

For any domain whose palette has not been written yet, the invoking
agent MUST include an **§A Domain Palette Appendix** in the produced
target file that supplies the three palettes (theory family list,
counterpart enumeration, stylized fact catalogue) before `Status` can
move from `draft` to `locked`. The appendix becomes a candidate for
promotion into `02-root-documents-spec.md` as the project's domain
catalogue grows.

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

The pipeline `create-simulation-pipeline.md` maintains a separate file —
`examples/{ScenarioName}/simulation-build-log.md` — as its **build log
and gate-record contract**. The relationship is:

```text
{domain}-{scenario}.md            ←  Produced by this skill (invoking agent)
   │                                  from minimal user inputs (§9.1)
   │                                  Immutable once locked
   │                                  Spec + producer: this file
   ▼
simulation-build-log.md              ←  Authored by the pipeline
                                      Refers to the target file by section number
                                      Adds §A AGENT_POOL gate log
                                      Adds §C Open questions accumulated during research
                                      Adds §D Build log (one row per pipeline phase)
```

The pipeline MUST NOT alter the target file. If during research the
pipeline discovers a defect in the target file (e.g., a citation does
not resolve), it raises the defect via `AskUserQuestion`; the user
authorises a re-run of this skill in **revise mode** (§9.3), the
invoking agent produces an updated target file, increments its
`Created` date to `Created / Revised`, and re-locks. The pipeline then
re-validates.

---

## 7. Versioning Rules

- The invoking agent MUST write the first version of a target file
  with `Status: draft`. The agent runs §11 validation three
  consecutive times **inside the skill** before writing the file to
  disk; only then does it hand the file to the pipeline.
- The pipeline upgrades `Status: draft → locked` only after §11
  validation passes inside the pipeline (the pipeline re-runs the
  check; trust but verify).
- After `Status: locked`, any change to the target file requires the
  user to authorise a re-run of this skill in **revise mode** (§9.3);
  the invoking agent then re-emits the file with `Status: draft` and
  adds a `Revised: YYYY-MM-DD` field beneath `Created` in §1. Users
  MUST NOT edit the file by hand, even to fix a typo — every change
  is skill-mediated and audit-trailed.
- The pipeline upgrades `Status: locked → released` only when Phase 6
  of `create-simulation-pipeline.md` completes the smoke test
  successfully.

---

## 8. Worked Example: Skeleton in Practice

The following is the **complete shape** of a conforming target file
for a finance scenario. It is illustrative only — real content
omitted.

```markdown
# Carry Trade Unwind — Scenario Target

## §1 Meta

| Field        | Content                                                                |
|--------------|------------------------------------------------------------------------|
| Name         | CarryTradeUnwind                                                       |
| Domain       | finance                                                                |
| Requested By | Sijia Chen                                                             |
| Produced By  | define-simulation-scenario-skill.md v1.0.0 (invoking agent: QoderWork) |
| Created      | 2026-06-29                                                             |
| Pipeline     | masim/skills/create-simulation-pipeline.md                             |
| Target Spec  | masim/skills/define-simulation-scenario-skill.md (v1.0)                |
| Status       | draft                                                                  |

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

| Agent name | Real-world counterpart | Theory family | Domain role | Primary signals | Intent line | Expected pool match |
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

For full, fully-populated examples produced by prior invocations of
this skill (once available):

- `examples/AssetBubble/finance-asset-bubble.md` (reference, finance)
- `examples/EchoChamber/opinion-echo-chamber.md` (reference, opinion)

If no fully-populated reference exists for the chosen domain, the
invoking agent SHOULD propose to add one in the same revision, subject
to user confirmation.

---

## 9. Skill Invocation Workflow

This section is normative for the **invoking LLM agent** (e.g., a
QoderWork / Codex / Claude Code session that has this skill loaded).
The user's involvement is limited to §9.1 (initial inputs) and §9.2
(a small number of confirmation checkpoints). The invoking agent —
not the user — produces every §1 — §10 section, runs the required
research, and writes the final file to disk.

### 9.1 Minimal User Inputs

Before the invoking agent begins production, it MUST collect exactly
the following inputs from the user (via `AskUserQuestion` or
equivalent). Nothing else is required from the user:

| # | Input                        | Format / Example                                                                                                                                           |
|---|------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | `{ScenarioName}`             | PascalCase, 2 — 4 tokens (e.g., `CarryTradeUnwind`).                                                                                                       |
| 2 | `{Domain}`                   | One of `finance / opinion / epidemics / sociology / ...`.                                                                                                  |
| 3 | Phenomenon sketch            | 3 — 10 sentences of plain English describing what the phenomenon is, why it matters, and roughly which participants are involved. This is the seed for §2. |
| 4 | Optional: variant preference | Any subset of `Rule / LLM / RuleLLM / Rag`. If omitted, the agent decides based on §3 research goals it derives from the sketch.                           |
| 5 | Optional: fixed anchor event | A specific historical/laboratory event the user wants pinned into §6. If omitted, the agent picks candidates and confirms at checkpoint C-3 below.         |

The invoking agent MUST NOT ask the user to write any of §1 — §10
directly. If the user offers hand-written §-content, the agent SHOULD
politely decline and instead treat that content as an extended
phenomenon sketch (input #3).

### 9.2 Production Sequence and Checkpoints

Once inputs 1 — 3 are fixed, the invoking agent MUST run the following
steps in order. Steps marked **[C-*]** are user checkpoints — short
confirmations, not co-authoring sessions.

1. **Verify inputs.** Confirm `examples/{ScenarioName}/` does not yet
   exist. Confirm `{Domain}` has a matching AGENT_POOL folder or
   trigger the §4 palette-appendix branch.
2. **Draft §1 — §2.** Expand the phenomenon sketch into the four §2
   sub-headings (Trigger / Mechanism / Participants / Resolution).
3. **Derive §3 Research Goals.** Propose 4 — 5 questions consistent
   with §2 and the diversity rules; select 3 — 5; mark which is the
   ablation, which the sweep, which the variant comparison.
4. **[C-1] Confirm §2 — §3 with the user.** Present the four §2
   sub-headings and the 3 — 5 research questions in a single
   `AskUserQuestion` block; let the user accept, edit, or reject.
   Loop until accepted.
5. **Research §4 Theoretical Anchors.** Search for canonical theories
   with resolvable DOIs; produce 3 — 6 five-row entries. Never invent
   a citation.
6. **Research §5 Stylized Facts.** For each fact, produce a numeric
   range and an acceptance metric expressible as a Python function
   name.
7. **Research §6 Historical / Empirical Anchors.** If the user pinned
   an anchor at §9.1 input #5, use it; otherwise propose 1 — 3
   candidates.
8. **[C-2] Confirm §4 — §6 with the user.** Present the theory list,
   stylized-fact table, and historical anchor(s). Any user pushback
   returns to the relevant research step.
9. **Draft §7 Agent Roster.** For each row, run the AGENT_POOL
   filename scan and record the `Expected pool match` column. Enforce
   the diversity rules (§7 column rules, plus at-least-one
   Stabilising / Destabilising).
10. **Draft §8 Environment Specification.** Pick the domain
    sub-template; justify each element with a §4 or citation
    reference.
11. **Draft §9 Parameter Seeds.** Every row cites a primary source
    from §4 or §6; no `estimated`; ≤10 % of rows may be
    `Source: normalization`.
12. **[C-3] Confirm §7 — §9 with the user.** Present the agent
    roster, environment table, and parameter seeds. Loop until
    accepted.
13. **Draft §10 Variants and Success Criteria.** Use the user's
    variant preference (§9.1 input #4) if given; otherwise pick a
    minimal set justified by §3.
14. **Run §11 Validation — three consecutive PASS runs.** Any FAIL
    resets the count. The agent MUST NOT skip a checkbox.
15. **Write the file to disk.** Path
    `examples/{ScenarioName}/{domain}-{scenario}.md`, with
    `Status: draft`. Report the file path back to the user; do not
    attempt to invoke the pipeline in the same turn.

The pipeline `create-simulation-pipeline.md` never starts before
step 15.

### 9.3 Revise Mode (Post-Lock Updates)

After the pipeline has upgraded `Status: draft → locked`, any change
to the target file MUST also go through this skill, in **revise
mode**:

1. The pipeline (or the user) lists the required change (e.g., a
   citation must be replaced; a §7 row must be added because AGENT_POOL
   research surfaced a missing archetype).
2. The user authorises a re-run of this skill with `mode = revise`
   and the change list.
3. The invoking agent re-loads the current target file, applies only
   the requested changes, re-runs §11 validation three consecutive
   times, sets `Status: draft` and adds `Revised: YYYY-MM-DD` to §1,
   and writes the file back.
4. The pipeline re-validates and re-locks.

Users MUST NOT hand-edit the target file to apply the change, even
when the change is a one-line typo. Every write to the target file
after step 15 above is skill-mediated so that the audit trail
(`Produced By`, `Revised`, and the pipeline's build log) stays
consistent.

---

## 10. Anti-Patterns (Reject on Sight)

- **Implementation creep.** Any line that names a Python class, a
  YAML key, a config path, or a prompt string. → Strip it; that
  belongs in `simulation-bases.md` or `explain.md`.
- **Hand-wavy ranges.** "α is small", "λ is moderate", "high
  volatility" (finance-appendix examples). → Replace with a numeric
  interval and a citation.
- **Free-text agents.** A §7 agent without a §4 theory anchor or
  without a §8 signal. → Either ground the agent or remove it.
- **Domain mixing.** A `Domain: finance` file with §7 agents whose
  real-world counterparts are exclusively from
  `02-root-documents-spec.md §4.1.2`'s sociology list (or vice
  versa). → Re-pick the domain or move the agent.
- **Stylized fact without metric.** "Bubbles get big" (finance-appendix
  example). → Replace with "peak/fundamental ∈ [1.4, 1.8] within 6 — 18
  rounds, F1 in §5" (finance-appendix example) or an equivalent
  domain-appropriate metric row.
- **Recycled history.** Using `1987 Black Monday` as the §6 anchor
  while it is already the primary anchor of `examples/AssetBubble/`.
  → Pick a less-used event or extend the existing scenario instead.
- **Phantom citations.** A DOI that does not resolve, an APA entry
  without the article title. → Replace with a verified citation.
- **Locked-without-validation.** Setting `Status: locked` manually
  without running §11. → Only the pipeline upgrades the status.
- **Hand-authored target file.** A `{domain}-{scenario}.md` whose §1
  Meta lacks a `Produced By` row, or whose sections show evidence of
  manual editing outside a skill invocation (e.g., mid-run partial
  writes, inconsistent numbering, formatting drift from the §8 worked
  example). → Reject and re-run this skill from scratch (fresh mode)
  or in revise mode, per §9.

---

## 11. Validation Checklist

Every item is a blocker. Run all items. Three consecutive PASS runs
are required, in the style of `agent-design-skill.md §6` and
`create-simulation-pipeline.md §6.4`.

**Structural completeness**

- [ ] All ten sections §1 — §10 are present in order.
- [ ] No top-level `## §N` heading exists outside §1 — §10 (no §0,
      no §11, no unnumbered `##` headings). Auxiliary content belongs
      in `simulation-build-log.md`.
- [ ] §1 Meta has every row filled, including both `Requested By` and
      `Produced By`; `Status` is `draft`.
- [ ] §2 has all four sub-headings (Trigger, Mechanism, Participants,
      Resolution), each with 3 — 6 sentences (minimum three, maximum
      six).
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
      a §8 environment sub-section.
- [ ] Every §5 stylized fact's `Acceptance metric` references a
      function name compatible with the §10.1 variants.
- [ ] §10.1 marks at least one deterministic-baseline variant `Yes`
      (finance-default: `Rule`).

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
invoking agent writes the target file to disk. After the third PASS,
the invoking agent writes the file with `Status: draft` and reports
the file path back to the user; only the pipeline may upgrade the
status thereafter.

---

## 12. Skill References

| Topic                                   | File                                                                     |
|-----------------------------------------|--------------------------------------------------------------------------|
| Top-level pipeline (consumes this file) | `masim/skills/create-simulation-pipeline.md`                             |
| Per-step methodology                    | `masim/skills/implement-simulation-skill/`                               |
| Universal Agent Design Handbook         | `masim/skills/agent-design-skill.md`                                     |
| Domain-instantiation rules (finance)    | `masim/skills/implement-simulation-skill/02-root-documents-spec.md §4.1` |
| Step 0 contract template                | `masim/skills/implement-simulation-skill/04-step0-load-target.md`        |
| AGENT_POOL directory                    | `examples/AGENT_POOL/`                                                   |
| Project structure overview              | `docs/structure.md`                                                      |

---

## 13. Status

| Field   | Content                                                                                                                                                                                                                                                                                                                                                                                             |
|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Version | 1.2.0                                                                                                                                                                                                                                                                                                                                                                                               |
| Created | 2026-06-29                                                                                                                                                                                                                                                                                                                                                                                          |
| Revised | 2026-07-01 (reframed as executable skill: user supplies minimal inputs; the invoking agent produces the target file end-to-end. See §0, §9).                                                                                                                                                                                                                                                        |
| Revised | 2026-07-01 (domain-neutralization pass: §7 column renamed 'Market / domain role' → 'Domain role'; §5, §9, §10.1 example rows marked as finance-appendix instantiations with parallel opinion / epidemics / sociology examples added in HTML comments; §10.1 variant scheme is now configurable per domain; §11 validation reworded to require a deterministic-baseline variant rather than 'Rule'.) |
| Status  | canonical                                                                                                                                                                                                                                                                                                                                                                                           |
