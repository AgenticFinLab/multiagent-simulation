# Root Document Specifications

## Purpose

This file defines the complete content specifications for the two root-level documents that every simulation must have:

1. **`simulation-bases.md`** — 9-section theoretical and design foundation
2. **`analysis-bases.md`** — 7-section analysis methodology foundation

These documents are the single source of truth for their respective domains. Every variant implementation built per target §10.1 (`explain.md`, `analysis.md`, `players.py`, `analysis.py`) traces back to these documents.

---

## Part I: `simulation-bases.md` — Theoretical and Design Foundation

**Location**: `examples/{SimulationName}/simulation-bases.md`

**Writing principle**: Write this document **before any code**. It drives all implementation decisions. Every agent type declared under target §7 (Agent Roster) must have a corresponding class in every built variant's agent-implementation module (the subset of the variant scheme — commonly `Rule / LLM / RuleLLM / Rag`, but the target file may declare any subset or extension — that is marked `Yes` in target §10.1). Every parameter value must have a source citation.

**Domain neutrality.** This specification governs simulations across any domain: financial markets, opinion dynamics, epidemics, sociology, organisational behaviour, ecology, or any future domain. The section spine (§1 – §9) is domain-neutral. Domain-specific vocabulary, palettes, and mechanisms are quarantined to the **domain-instantiation appendices** attached to §4.1 (see §4.1 for the active `Finance` appendix and instructions for adding sibling appendices such as `Opinion`, `Epidemics`, `Sociology`).

---

### §1 Phenomenon Definition

```markdown
# {SimulationName} — Simulation Design Basis

## 1. Phenomenon Definition

| Item               | Description                                                                                          |
|--------------------|------------------------------------------------------------------------------------------------------|
| Phenomenon Name    | [Full name, common name, brief one-sentence description]                                             |
| Category           | [Type: herding / bubble / crash / leverage / behavioral bias / manipulation / etc.]                  |
| Core Mechanism     | [2-3 sentences: the key self-reinforcing or dynamic that produces the phenomenon]                    |
| Real-World Origin  | [Historical event(s), dates, markets, and scale of impact]                                           |
| Research Relevance | [Why this phenomenon matters to financial stability, behavioral finance, market efficiency research] |

### 1.1 Origin and Source Analysis

This subsection provides a deep account of where the simulation phenomenon originates —
its roots in academic literature, its grounding in real-world finance, and the chain of
intellectual development that connects historical events to the theoretical models to this
simulation's design.

#### 1.1.1 Intellectual Lineage

[3–5 paragraphs tracing the origin of this phenomenon:]

Paragraph 1 — Foundational observation: Who first described or documented this phenomenon?
In what context — an empirical observation, a laboratory experiment, a market crisis post-mortem?
What was the original evidence?

Paragraph 2 — Theoretical formalisation: Which academic works first built a mathematical or
conceptual model of this phenomenon? What simplifying assumptions were made? What has been
preserved vs. modified in this simulation?

Paragraph 3 — Empirical confirmation: Which large-scale empirical studies confirmed the
phenomenon across multiple markets, time periods, or asset classes? What are the key stylised
facts established in this literature?

Paragraph 4 — Connection to agent-based modelling: How has this phenomenon been previously
modelled in the ABM / computational finance literature? Which prior ABM studies are closest to
this simulation? What does this simulation add or change?

Paragraph 5 — Simulation design choices: Which specific decisions in this simulation's design
(agent types, thresholds, market mechanism) derive directly from the above literature? Cite
the specific source for each major design choice.

#### 1.1.2 Real-World Event Catalogue

A comprehensive search of all documented real-world events that correspond to this simulation's
phenomenon. This table is the primary RAG knowledge base seed for the Rag variant.

| Event Name | Date(s) | Market / Asset | Trigger             | Magnitude                      | Duration             | Correspondence to Simulation                  | Primary Source                 |
|------------|---------|----------------|---------------------|--------------------------------|----------------------|-----------------------------------------------|--------------------------------|
| [Event 1]  | [Date]  | [Market]       | [What initiated it] | [Peak deviation / loss / drop] | [Time to resolution] | [Which agents, which mechanism — be specific] | [Author/Report, Year, DOI/URL] |
| [Event 2]  | [Date]  | [Market]       | [Trigger]           | [Magnitude]                    | [Duration]           | [Correspondence]                              | [Source]                       |
| [Event 3]  | ...     | ...            | ...                 | ...                            | ...                  | ...                                           | ...                            |

**Minimum**: 3 events. **Recommended**: 5–7 events spanning different time periods and geographic markets.

**Catalogue quality criteria**:
- Every event must have a verifiable primary source (academic paper, regulatory report, or reputable journalism with date and URL)
- Magnitude must be a quantitative figure (%, $, basis points) — not "large" or "significant"
- Correspondence column must name specific simulation agents and mechanisms — not "similar dynamics"
- Events should span multiple decades and geographies to demonstrate the phenomenon's generality

#### 1.1.3 Book and Practitioner Literature

| Title        | Author(s) | Year   | Publisher   | Relevance to This Simulation                                               |
|--------------|-----------|--------|-------------|----------------------------------------------------------------------------|
| [Book Title] | [Author]  | [Year] | [Publisher] | [Specific chapter(s) or concept(s) that directly inform simulation design] |
| [Book Title] | [Author]  | [Year] | [Publisher] | [Relevance]                                                                |

Minimum 2 entries. Include both academic textbooks and practitioner accounts (e.g., memoirs,
regulatory post-mortems) where they document behavioural mechanisms that the simulation models.
```

**Quality criteria**:
- The Core Mechanism must be specific enough that a reader unfamiliar with the phenomenon can understand what drives it. Avoid generic phrases like "positive feedback." State what specific agent behavior creates the feedback.
- §1.1.2 Real-World Event Catalogue is **mandatory** — not optional. A simulation with no documented real-world correspondence is not deployable.
- Every entry in the event catalogue must have a quantitative magnitude column.
- The Intellectual Lineage must trace the path from historical observation → theory → this simulation. It must not simply list references — it must narrate the chain of influence.

---

### §2 Theoretical Foundation

This section establishes the complete academic basis for the entire simulation. Every theory here is later referenced by investor entries in §4 and parameters in §6. The goal is to make this section a self-contained theoretical survey — a reader should be able to understand the intellectual foundation of the simulation without consulting outside sources.

**Minimum**: 3 theories. **Recommended**: 4–6. Each theory must have a full entry as specified below.

**For EACH theory:**

```markdown
### Theory N: [Full Theory Name]

#### N.1 Citation and Status

- **Primary Citation**: [Author(s), Year. "Full Title." *Journal Name*, Volume(Issue), Pages. https://doi.org/...]
- **Theory Status**: [Foundational / Contested / Widely-applied / Emerging — with 1-sentence justification]
- **Original Context**: [The phenomenon/market this theory was originally developed to explain; year of original formulation if different from first citation]

#### N.2 Core Theoretical Mechanism

[3–5 paragraphs. This is the heart of the theory entry:]

Paragraph 1 — Central claim: What does this theory assert about agent behaviour or market dynamics?
State it as a precise, falsifiable claim. Avoid hedged language like "suggests" — be direct.

Paragraph 2 — Mechanism: What is the causal chain the theory proposes? What specific decision
process or incentive structure produces the asserted outcome? Walk through the mechanism step
by step (e.g., "A rises → B responds → C adjusts → D results, which feeds back to A").

Paragraph 3 — Boundary conditions: Under what conditions does the theory hold? What assumptions
are required? Which real-world frictions does it abstract away? Are those abstractions appropriate
for this simulation?

Paragraph 4 — Theoretical debates: What are the main critiques of this theory in the literature?
Are there competing theories that predict different outcomes? How does this simulation resolve
that ambiguity in its design?

#### N.3 Mathematical Formulation

**Core Model**:
```
[Central equation(s) — write the full formal model, not just a sketch]
[Define every symbol inline or in the notation table below]
```

**Notation**:

| Symbol | Meaning                  | Units / Type    | Typical Range               | Source     |
|--------|--------------------------|-----------------|-----------------------------|------------|
| [sym]  | [Plain-language meaning] | [Units or type] | [From empirical literature] | [Citation] |

**Derivation sketch** (if non-trivial):
[The key steps that lead from primitives to the central equation, if the equation is not self-evident.
For well-known models, a 2-3 step sketch is sufficient. For novel combinations, be thorough.]

**Model variants or extensions**:
[Any important extensions of the base model that are relevant to this simulation. For example,
if the base model assumes rational agents but this simulation uses a bounded-rational version,
explain the modification and its source.]

#### N.4 Empirical Evidence

**Supporting Studies**:

| Study                                     | Finding                         | Market / Period      | Sample Size | Relevance                                   |
|-------------------------------------------|---------------------------------|----------------------|-------------|---------------------------------------------|
| [Author(s), Year — "Title," Journal, DOI] | [Specific quantitative finding] | [Where/when studied] | [N]         | [How this supports the theory as used here] |
| [Study 2]                                 | [Finding with numbers]          | [Market]             | [N]         | [Relevance]                                 |

**Key Stylised Facts** (as established by this literature):

1. [Fact 1 — quantitative, e.g., "Mean momentum return = 1.01% per month at 12-month horizon"]
2. [Fact 2]
3. [Fact 3]

**Contradicting Evidence** (if any):
[Studies that find weak or null effects; markets where the phenomenon does not hold; periods of
breakdown. Acknowledging contradicting evidence strengthens the theoretical grounding, not
weakens it.]

#### N.5 Relevance to This Simulation

**Agent mapping**: [Which investor type(s) in §4 embody this theory, and how specifically.]

**Mechanism mapping**: [Which part of the simulation's price formation or decision logic this
theory directly explains — cite §3.1 or §4.N references explicitly.]

**Parameter calibration implication**: [What this theory implies about specific parameter values,
thresholds, or ranges — be quantitative where possible. E.g., "Tversky & Kahneman (1992) estimate
loss aversion coefficient λ ≈ 2.25; this directly calibrates the loss_aversion parameter in §6."]

**Limitations in this context**: [What aspects of the full theory are not captured by this simulation,
and why the simplification is acceptable for the research question being addressed.]
```

**Quality criteria**:
- Every citation must include journal name, volume/issue, pages, and DOI where available.
- Mathematical Formulation §N.3 must be present for every theory — do not omit because "no closed form exists"; write the verbal model precisely and include the notation table.
- Empirical Evidence §N.4 must include a supporting studies table with quantitative findings, not just "has been documented."
- The Relevance §N.5 must name specific §4 investor numbers — "This theory is embodied by §4.2 MarketMaker" not "some agents."
- Theories must be ordered from most foundational to most specific to this simulation.

---

### §3 Environment Design

The environment is the shared substrate that agents perceive and act upon.
For a financial-market scenario the environment is the market and its price
formation mechanism; for an opinion-dynamics scenario it is the network
topology plus the opinion-update law; for an epidemics scenario it is the
contact graph plus the transmission model; for a sociology scenario it is
the institutional or normative context. The three subsections below are
domain-neutral: instantiate them using the domain appendix invoked in §4.1.

#### §3.1 State Dynamics Model

```markdown
### 3.1 State Dynamics Model

**Update law** (equation, algorithm, or transition rule):
[Write the full formal update rule for how the environment state evolves
between rounds as a function of agent actions and any exogenous drivers.
For finance this is a price formation formula; for opinion dynamics an
opinion-averaging or bounded-confidence rule; for epidemics an SIR-family
transition; for sociology a norm-update or role-transition rule. See the
domain appendix invoked in §4.1 for the canonical formulation.]

**Variable Definitions**:

| Symbol | Name           | Definition                                  | Role in Phenomenon            |
|--------|----------------|---------------------------------------------|-------------------------------|
| [sym]  | [State var]    | [What it represents]                        | State variable                |
| [sym]  | [Aggregate]    | [Aggregation of agent actions]              | Drives state change           |
| [sym]  | [Anchor]       | [Reference / equilibrium / target level]    | Reversion anchor              |
| [sym]  | [Sensitivity]  | [Coupling parameter]                        | [Calibrated value and source] |
| [sym]  | [Reversion]    | [Speed of return to anchor]                 | [Calibrated value and source] |
| [sym]  | [Noise]        | [Distribution]                              | Background randomness         |

**Calibration Rationale**:
For EACH parameter of the update law:
- Typical empirical range: [from literature]
- Chosen value: [specific value]
- Source: [full citation]
- Sensitivity: [High/Medium/Low — what changes if this parameter is varied ±50%]

**Rationale**:
[Why each term is included. Why this combination of parameters is chosen
to produce the target phenomenon. For example, in a finance scenario:
"High price impact + low mean reversion creates bubble-prone dynamics
because demand shocks are amplified and mean reversion is too slow to
correct them within the simulation time horizon."]

**Dynamic Properties**:
- When [aggregate action] > 0: [what happens to state; which agents drive this]
- When [aggregate action] < 0: [what happens; cascade implications if applicable]
- When state >> anchor: [reversion magnitude; which agents activate]
- When state << anchor: [recovery mechanics; which agents activate]
- Noise effect: [what it represents; how it prevents determinism]
```

#### §3.2 Additional Environment Mechanisms

For EACH mechanism beyond the core update law (institutional constraints,
regulatory caps, network rewiring rules, quarantine policies, norm
enforcement, etc.):

```markdown
**[Mechanism Name]**:
- Trigger: [Precise condition — e.g., "equity_ratio < 0.70" (finance),
  "opinion_variance < 0.05" (opinion dynamics), "prevalence > 0.20" (epidemics)]
- Action: [What the environment does — prevent, force, cap, rewire, add cost]
- Rationale: [Why this mechanism exists in the real system; which institution,
  norm, biological process, or authority enforces it]
- Source: [Citation for the real-world referent that motivates this]
- Simulation Implementation: [How it is encoded in the environment module —
  e.g., `_clear_market()` for finance, `_update_topology()` for opinion
  dynamics, `_apply_quarantine()` for epidemics]
```

#### §3.3 Information Broadcast Design

```markdown
### 3.3 Information Broadcast Design

Each round, the environment broadcasts to all agents:

| Field           | Type   | Definition                                       | Rationale for Inclusion               |
|-----------------|--------|--------------------------------------------------|---------------------------------------|
| [state]         | float  | [Primary state variable — e.g., price, mean opinion, prevalence] | Primary signal for all agents |
| [anchor]        | float  | [Reference / equilibrium / target — e.g., fundamental, prior belief] | Required by anchor-sensitive agents |
| [deviation]     | float  | (state − anchor) / anchor                        | Pre-computed; used by most agents     |
| `round`         | int    | Current round number                             | Needed for frequency-controlled agents |
| [field]         | [type] | [definition]                                     | [why included, which agents use it]   |

**Design Notes**:
[Explain any deliberate exclusions — e.g., "return_pct is NOT broadcast; all
agents reference deviation only — this is consistent with relative value
framing." Explain any unusual inclusions.]
```

---

### §4 Agent Taxonomy — Conformance to the Universal Agent Design Handbook

**Authoritative standard.** Every agent entry in `simulation-bases.md §4`
MUST conform to the **Universal Agent Design Handbook** at
`masim/skills/agent-design-skill.md`. The handbook is the single source of
truth for the intrinsic specification of any participant agent, in any
scenario domain (finance, opinion dynamics, epidemics, sociology, and
future domains). This section therefore does NOT repeat the handbook's
section schema — it states only how the handbook is applied inside
`simulation-bases.md`, and how domain-specific vocabulary is instantiated
via the domain appendix invoked in §4.1.

**Critical exclusions.** Section §4 MUST NOT contain any of the following —
they belong to each variant's `explain.md §2` (where a "variant" is any
member of the variant scheme declared in target §10.1):

- Rule-Based Behavior (IF/THEN code logic, executable thresholds) — belongs
  in the rule-based variant's `explain.md §2`.
- LLM Persona (prompt personality text, signal-interpretation guidelines) —
  belongs in any LLM-based variant's `explain.md §2` and prompts module.
- Hybrid Rule-in-Prompt Notes (embedded rule text for prompts) — belongs in
  the rule-in-prompt variant's `explain.md §2` and prompts module.
- Retrieval Hooks (RAG index configuration, retriever prompts) — belongs in
  any retrieval-augmented variant's `explain.md §2` and retrieval module.

The §4 entry defines **what the agent IS** at the design layer. Each
variant's `explain.md §2` defines **how that variant encodes it**.

---

#### 4.0 How the Universal Handbook Applies Inside simulation-bases.md

Each agent entry occupies one block that conforms section-for-section to
the handbook's **11-section canonical order** (`agent-design-skill.md §2`),
plus one **domain-instantiation extension** — `Population and
Heterogeneity` — inserted at position `4.{N}.7` to capture how multiple
instances of the same archetype are calibrated and sampled. Header levels
are **shifted down by two** to fit the embedding context, so that the
agent's Title (handbook `#`) lands at `###` inside `simulation-bases.md
§4`, the handbook's `##` sections land at `####`, and the handbook's `####`
sub-blocks land at `######`. All other content — field schemas, table
column names, validation requirements, RFC-2119 modal verbs — applies
unchanged.

| Inside this file (embedded)                           | Handbook canonical level (standalone)       | Handbook section name                 |
|-------------------------------------------------------|---------------------------------------------|---------------------------------------|
| `### Agent: {ClassName}`                              | `# <agent role description>`                | Title                                 |
| `#### 4.{N}.1 Summary`                                | `## Summary`                                | Summary (7 fixed rows)                |
| `#### 4.{N}.2 Definition and Goals`                   | `## Definition and Goals`                   | Definition and Goals (3 paragraphs)   |
| `#### 4.{N}.3 Theoretical Foundation`                 | `## Theoretical Foundation`                 | Theoretical Foundation (≥1 sub-block) |
| `#### 4.{N}.4 Design Purpose and Activation Triggers` | `## Design Purpose and Activation Triggers` | Activation / Deactivation / Regime    |
| `#### 4.{N}.5 Behavioral Framework`                   | `## Behavioral Framework`                   | 5 H4 sub-blocks (see below)           |
| `#### 4.{N}.6 Parameters`                             | `## Parameters`                             | 8-column parameter table              |
| `#### 4.{N}.7 Population and Heterogeneity`           | *(domain-instantiation extension — not in handbook §3 canonical order; supplied by the domain appendix invoked in §4.1)* | 5-row population table |
| `#### 4.{N}.8 Worked Numerical Examples`              | `## Worked Numerical Examples`              | ≥3 cases + 1 edge case                |
| `#### 4.{N}.9 Validation and Calibration`             | `## Behavioral Verification and Calibration` | Includes Ablation Hooks               |
| `#### 4.{N}.10 Academic References`                   | `## Academic References`                    | Numbered citation table               |
| `#### 4.{N}.11 Design Provenance and Versioning`      | `## Design Provenance and Versioning`       | 6-row provenance footer               |

The Behavioral Framework's five sub-blocks are placed at `######` in the
embedded form: `4.{N}.5.1 Decision Information Set`, `4.{N}.5.2 Core
Behavioral Mechanism`, `4.{N}.5.3 Action Space`, `4.{N}.5.4 Mathematical
Model`, `4.{N}.5.5 Behavioral Properties`. `{N}` is a 1-based index inside
`simulation-bases.md §4` (so `4.1.5.3 Action Space` is the Action Space of
the first agent).

---

#### 4.1 Domain Instantiation Appendices

`simulation-bases.md` describes a scenario in a specific domain. Domain-
specific vocabulary, palettes, and label substitutions are quarantined into
**per-domain appendices** attached to this section. Each appendix is
identified by a suffix letter and MUST be named canonically:

| Appendix ID | Domain               | Status        |
|-------------|----------------------|---------------|
| §4.1.F      | Finance / market-trading | Complete (below) |
| §4.1.O      | Opinion Dynamics     | Sibling slot — add when first opinion-dynamics scenario is authored |
| §4.1.E      | Epidemics            | Sibling slot — add when first epidemics scenario is authored |
| §4.1.S      | Sociology / norms    | Sibling slot — add when first sociology scenario is authored |
| §4.1.X      | Any future domain    | Reserved for extension                                     |

**Selection rule.** Every scenario invokes exactly one appendix from the
list above (matching target §1 `Domain`). If no appendix exists for the
scenario's domain, the author MUST add one — as a **sibling appendix**
under §4.1 in this file — before proceeding, and populate at minimum the
five palettes / label sets given in the Finance appendix template (Theory
Family palette, real-world counterpart enumeration, stylised-fact
catalogue, regime palette + Summary-row relabel, Action Space row-label
substitutions). New sibling appendices MUST NOT edit the Finance appendix
below.

##### 4.1.F Finance Appendix — Domain Instantiation for Market-Trading Scenarios

For a scenario whose target §1 declares `Domain: finance`,
`simulation-bases.md` describes a **market-trading scenario**. The
handbook's domain-neutral row labels and value palettes are therefore
instantiated for the financial domain inline below. (Earlier drafts
referenced a separate `agent-design-finance.md` file — that file is
intentionally not maintained; the instantiation rules live here and are
the single source of truth.)

**4.1.F.0 Environment State Dynamics — canonical form.** Instantiate
`§3.1 State Dynamics Model` in the spine with the **price formation
formula** below:

```
P(t+1) = P(t) + λ · D(t) + γ · [F(t) − P(t)] + ε(t)
```

with `P(t)` the market price at start of round `t`, `D(t) = Σ buy_qty −
Σ sell_qty` across all agents, `F(t)` the fundamental value (constant or
grows at rate `g` per round), `λ` the price impact, `γ` the mean-reversion
speed, and `ε(t) ~ N(0, σ²)` the noise term. Follow §3.1's Variable
Definitions / Calibration Rationale / Rationale / Dynamic Properties
skeleton with these exact symbols.

**4.1.F.1 Theory Family palette (pick one per agent)**

- `Behavioral Finance` — anchoring, loss aversion, disposition effect,
  framing, herding, overconfidence, availability, representativeness.
- `Microstructure` — inventory management, adverse selection, price impact,
  market making, order flow, latency arbitrage.
- `Information Cascade / Herding` — rational/irrational imitation,
  informational cascade, social learning.
- `Quant / Statistical` — momentum, reversal, statistical arbitrage,
  pairs trading, factor exposure.
- `Fundamental / Value` — discounted cash flow, mean reversion to
  fundamental, value investing.
- `Liquidity / Funding` — funding constraint, margin spiral, fire sale,
  liquidity provision.
- `Leverage / Risk-On-Risk-Off` — VaR-based deleveraging, forced
  liquidation, prime-broker dynamics.
- `Noise / Liquidity-providing noise` — uninformed flow, retail noise.

**4.1.F.2 Real-world counterpart enumeration (pick one per agent)**

`Retail investor` · `Active retail trader` · `Hedge fund (long/short)` ·
`Hedge fund (event-driven)` · `Quant fund / CTA` · `Mutual fund / pension` ·
`Asset manager (index)` · `Family office` · `Proprietary trading desk` ·
`Sell-side market maker` · `High-frequency market maker` ·
`Prime broker / dealer` · `Corporate / strategic buyer` ·
`Central bank / sovereign` · `Insurance / annuity` ·
`Crypto-native trader` · `Social-media-driven retail community`.

If no entry fits, an agent MAY supply a more specific counterpart, but
MUST cite at least one peer-reviewed paper or regulatory report that
documents that participant class.

**4.1.F.3 Stylized-fact catalogue (pick the ones this agent helps produce)**

Volatility clustering · Fat tails of returns · Leverage effect ·
Short-horizon momentum (3-12 month) · Long-horizon reversal (3-5 year) ·
Bid-ask bounce · Trade-size / volume autocorrelation ·
Price-impact concavity (square-root law) · Volume spikes around news ·
Liquidity black holes · Flash-crash signatures · Persistent bubble
deviation > fundamental · Capitulation tail · Co-movement in factor
returns · Cross-sectional herding patterns.

Stylized facts cited in §4.{N}.2 (Definition and Goals, paragraph 3)
MUST come from this catalogue or be supplied with a primary citation.

**4.1.F.4 Regime palette and relabel rules**

The handbook's `Behavioral Adaptation by Condition` table is **relabelled**
in the embedded form to `Market Contribution by Regime` (since the embedded
form under this appendix is scoped to market scenarios). Use regime labels
from the following palette (4-8 per agent depending on scenario):

`Calm market` · `Trending market (up)` · `Trending market (down)` ·
`High-volatility regime` · `Liquidity stress / drought` ·
`Bubble inflation` · `Post-peak deflation` · `Crash / cascade` ·
`Post-shock recovery` · `News-driven regime` · `Earnings/macro window`.

Also: the handbook Summary row labelled `Behavioral Tendency` is
**relabelled** to `Market Role` with values `Stabilising` /
`Destabilising` / `Context-dependent` — a one-line rationale required.
(Sibling appendices for other domains SHOULD relabel this row analogously
— e.g., `Opinion Role`, `Contagion Role`, `Norm Role`.)

**4.1.F.5 Action Space row labels (market-trading instantiation)**

The handbook §3.6.3 row labels are substituted as follows. Row order is
preserved; only the labels change:

| Handbook generic label   | Market-trading label         |
|--------------------------|------------------------------|
| Action types allowed     | Order types allowed          |
| Action parameter rule    | Price level rule             |
| Sizing rule              | Order quantity rule          |
| Action lifetime          | Order lifetime               |
| Revision policy          | Cancellation policy          |
| State constraint         | Inventory constraint         |
| Resource cap             | Wealth / leverage cap        |
| Exit rule                | Stop-loss / kill rule        |

Environment-imposed limits (matching engine, tick grid, fee schedule,
latency, regulator-imposed caps) MUST NOT appear in this table — they
belong to §3 Environment Design.

**4.1.F.6 What stays unchanged from the handbook**

All other handbook fields apply verbatim, including the 8-column
Parameters table, the per-theory citation block (Calibration Source,
Falsification Conditions, Alternative Theories), the Mathematical
Model with State-Update Rule and Determinism Contract, and the
Behavioral Verification + Ablation Hooks section.

Authors MUST NOT introduce new top-level fields not specified in the
handbook, and MUST NOT omit any handbook section. If an agent
genuinely exposes zero tunable parameters, the Parameters section MUST
contain the literal phrase `_No tunable parameters._` per handbook §3.7.

---

#### 4.2 Per-Agent Block Skeleton (Embedded Form)

Use the handbook's section-by-section schema
(`agent-design-skill.md §3 Section-by-Section Requirements`) as the
structural skeleton for each agent entry, then re-level it from standalone
to embedded form per the table in §4.0 above. The minimum number of agent
entries is **4**; the maximum is **7**.

The block layout for one agent in `simulation-bases.md` is:

```markdown
### Agent: {ClassName}

#### 4.{N}.1 Summary

| Field                 | Content                                                                  |
|-----------------------|--------------------------------------------------------------------------|
| Archetype             | <one-line role phrase, matches the H3>                                   |
| Theory Family         | <from the Theory Family palette in the domain appendix invoked in §4.1> |
| Domain Role           | **Destabilising** / **Stabilising** / **Context-dependent** — <one-line> (Finance appendix relabels this row to `Market Role`; sibling appendices relabel analogously — see §4.1.F.4 and its equivalents.) |
| Time Horizon          | <short / medium / long>                                                  |
| Risk Tolerance        | <low / medium / high>                                                    |
| Information Asymmetry | <none / partial / full>                                                  |
| Determinism           | <deterministic / stochastic-given-seed / non-deterministic>              |

#### 4.{N}.2 Definition and Goals
<3 short paragraphs (8–14 sentences total) per handbook §3.3:
(1) what the agent models, with a named real-world counterpart from the
    domain appendix's counterpart enumeration;
(2) decision goal: action, sizing, action-parameter level (finance: price
    level; opinion dynamics: opinion increment; epidemics: contact rate),
    criterion;
(3) role inside the simulation, named stylised facts produced (from the
    domain appendix's catalogue), explicit non-goals.>

#### 4.{N}.3 Theoretical Foundation
<≥1 theory sub-block per handbook §3.4. Each sub-block MUST include:
Theory / Study, Citation (with DOI), Core Insight, Mathematical
Formulation, Empirical Evidence, Relevance to This Agent, Calibration
Source, Falsification Conditions, Alternative Theories.>

#### 4.{N}.4 Design Purpose and Activation Triggers
<Per handbook §3.5: Purpose, Call Frequency, Prerequisite Signals,
Missing-Signal Policy, Activation Triggers (with `<Default>`),
Deactivation Conditions, Domain Contribution by Regime (≥2 rows —
finance appendix relabels this as "Market Contribution by Regime";
sibling appendices relabel analogously),
Interaction sentence.>

#### 4.{N}.5 Behavioral Framework

##### 4.{N}.5.1 Decision Information Set
<Signal table (Signal, Type, Memory Window, Rationale) + explicit
"Does NOT use" line — per handbook §3.6.1.>

##### 4.{N}.5.2 Core Behavioral Mechanism
<5–10 numbered steps in plain English mixed with formulas; no code in any
specific programming language — per handbook §3.6.2.>

##### 4.{N}.5.3 Action Space
<8-row aspect table using the row labels supplied by the domain appendix
invoked in §4.1 (finance: market-trading labels per §4.1.F.5; sibling
appendices supply their own label sets).
Environment-imposed limits (e.g., matching engine, tick grid, fees,
latency, regulator-imposed caps in finance; contact-network capacity or
quarantine rules in epidemics) MUST NOT appear here — per handbook §3.6.3.>

##### 4.{N}.5.4 Mathematical Model
<Per handbook §3.6.4: Decision variable, Trigger function (pseudo-code),
Sizing function, State variables, State-update rule with explicit ordering
(pre-decide / post-decide / post-fill), Determinism contract, Parameter
symbol table.>

##### 4.{N}.5.5 Behavioral Properties
<Per handbook §3.6.5: Time horizon, Risk tolerance, Information asymmetry,
Psychological profile (cite biases).>

#### 4.{N}.6 Parameters
<8-column table (Parameter, Type, Default, Valid Range, Sensitivity,
Description, Impact, Source) per handbook §3.7. Every Impact cell MUST
state direction of effect ("Higher → …"). Every Default MUST trace to
§4.{N}.3 Calibration Source or to the Source column. If the agent exposes
zero tunable parameters, write `_No tunable parameters._`.>

#### 4.{N}.7 Population and Heterogeneity
<5-row population table (domain-instantiation extension; not part of
handbook §3 canonical order): Default population size, Parameter
heterogeneity policy, Heterogeneity per parameter, Cross-agent
correlation, Identity persistence.>

#### 4.{N}.8 Worked Numerical Examples
<≥3 primary cases covering distinct trigger branches + ≥1 edge case
(cold-start, extreme deviation, deactivation condition, resource clamp,
regime flip, or missing-signal fallback). Each case MUST show environment
state, step-by-step calculation, decision, and state update — per
handbook §3.8.>

#### 4.{N}.9 Validation and Calibration
<Per handbook §3.9 "Behavioral Verification and Calibration": Calibration
data sources (per parameter), Expected stylised facts when this agent
dominates the population, Sanity bounds (red flags during simulation), and
at least one Ablation Hook with hypothesis.>

#### 4.{N}.10 Academic References
<Numbered citation table per handbook §3.10. Every paper cited anywhere in
the entry MUST appear here.>

#### 4.{N}.11 Design Provenance and Versioning
<6-row footer per handbook §3.11: Author, Reviewed by (optional), Created,
Version (semver), Change log, Status.>
```

---

#### 4.3 Per-Agent Validation

For each agent entry, run the handbook's **Validation Checklist**
(`agent-design-skill.md §6`) against the entry. Every unchecked item is a
blocker. The same checklist applies regardless of which variant (from the
variant scheme declared in target §10.1) will later realise the agent.

Cross-agent diversity verification (different time horizons, conflicting
incentives, distinct information sets) is performed in §5 of this file and
is orthogonal to the per-agent handbook checklist.

---

### §5 Agent Diversity Verification

```markdown
## 5. Agent Diversity Verification

| Diversity Criterion              | Met? | Evidence                                                                                                          |
|----------------------------------|------|-------------------------------------------------------------------------------------------------------------------|
| Different time horizons          | Yes  | [List of agents with distinct horizons — e.g., a fast responder, a medium-term participant, an opportunistic one] |
| Different information processing | Yes  | [Which agents use which signals differently]                                                                      |
| Conflicting incentives           | Yes  | [Which agents act one way when others act the opposite way; example scenario]                                     |
| Mix of stabilizing/destabilizing | Yes  | [Count and names; ratio should be ≥1 stabilizing per 2 destabilizing]                                             |
| Different risk tolerances        | Yes  | [Range: from Low to Extreme; examples]                                                                            |
| Different decision frequencies   | Yes  | [Examples of high-frequency vs. low-frequency actors]                                                             |

**Critical mass check**: [Explain why this agent set is sufficient to produce the target phenomenon.
What is the minimum subset of agents needed? What would break if one type were removed?]
```

---

### §6 Parameter Table

```markdown
## 6. Parameter Table

| Parameter         | Symbol | Value | Typical Range    | Source Citation | Description                                          | Sensitivity      |
|-------------------|--------|-------|------------------|-----------------|------------------------------------------------------|------------------|
| [state_init]      | [sym]  | [val] | [range]          | [Full citation] | Starting value of the primary state variable        | Low — scale only |
| [anchor]          | [sym]  | [val] | [range]          | [Full citation] | Reference / equilibrium level                       | Medium           |
| [coupling]        | [sym]  | [val] | [range from lit] | [Full citation] | Sensitivity of state to aggregate agent action      | High             |
| [reversion]       | [sym]  | [val] | [range from lit] | [Full citation] | Attraction speed toward the anchor                  | High             |
| [noise_std]       | [sym]  | [val] | [range]          | [Full citation] | Noise term standard deviation                       | Low              |
| [agent param]     | [sym]  | [val] | [range]          | [Full citation] | [Meaning]                                           | [High/Med/Low]   |

<!-- Finance-appendix example row set (from §4.1.F.0):
     initial_price P(0), fundamental_value F, price_impact λ,
     mean_reversion γ, noise_std σ. Sibling appendices supply their
     own row set (e.g., initial_opinion, opinion_confidence for
     opinion dynamics; R0, recovery_rate for epidemics). -->
```

**Quality criteria**:
- Every numeric value must have a source citation that is a real, published work (not "normalization" except for scale-only parameters).
- The Typical Range column must come from the literature, not be invented.
- The Sensitivity column must describe what happens quantitatively, not just say "important."
- Rows for the primary environment update law MUST match the symbol list published by the domain appendix invoked in §4.1 (finance: §4.1.F.0).

---

### §7 Communication and Round Structure

```markdown
## 7. Communication and Round Structure

```
Round N (t = 1, 2, ..., T):

  Phase 1 — Environment Broadcast:
    Environment → all agents: {state, anchor, deviation, round, [other fields]}
    This message triggers perceive() in all agents simultaneously.

  Phase 2 — Agent Decisions:
    For each agent i:
      perceive(): extract and store environment data in custom_state
      decide():   apply strategy (per the variant scheme declared in target §10.1)
      act():      construct action message

  Phase 3 — Action Submission:
    Each agent → Environment: {action_type, quantity: Q, action_parameter: p, ...}

  Phase 4 — Environment Update:
    Environment.perceive(): collect all agent actions
    Environment.decide():   compute aggregate D(t), apply update law (see §3.1)
    Environment.act():      broadcast updated state → triggers next round

  Phase 5 — Logging:
    Record environment state, all agent states, and action records to
    EXPERIMENT/.../records/
```

<!-- Finance-appendix instantiation (from §4.1.F): substitute Environment→Market,
     state→price, anchor→fundamental, action_type∈{buy,sell,hold},
     action_parameter→bid_price, Environment.decide()→_clear_market()
     applying P(t+1) = P(t) + λ·D(t) + γ·[F(t)−P(t)] + ε(t). Sibling
     appendices provide analogous substitutions. -->

**Round duration interpretation**: [What real-world time period does one round represent?
E.g., "Each round represents one trading day" (finance); "one social interaction"
(opinion dynamics); "one contact-tracing window" (epidemics). Justify this choice.]

**Synchronous vs. asynchronous**: [Are agents processing simultaneously? Any ordering dependencies?]
```

---

### §8 Historical Case Studies

**Purpose**: Section §8 is the empirical grounding of the simulation. It connects the abstract agent-based model to documented real-world episodes, establishes calibration targets derived from historical data, and populates the retrieval-augmented variant's knowledge base (if any variant declared in target §10.1 uses retrieval augmentation). A simulation without this section cannot be externally validated.

**Minimum**: 2 events. **Recommended**: 3–5, spanning different time periods, settings (markets, communities, populations, jurisdictions, etc.) and geographic regions to demonstrate the phenomenon's generality.

For EACH real-world event:

```markdown
## 8. Historical Case Studies

### Case N: [Full Event Name]

#### N.1 Event Profile

| Item             | Detail                                                                                                                                     |
|------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Date Range       | [Specific dates or period, e.g., "March 24–29, 2021"; "August–October 1987"]                                                               |
| Domain / Setting | [Domain-appropriate identifier — e.g., "US equity markets, NYSE + NASDAQ" (finance); "Twitter early 2020" (opinion); "Wuhan Dec 2019" (epidemics); "one US organisation" (sociology)] |
| Trigger          | [The specific catalyst — precise and verifiable, not generic]                                                                              |
| Duration         | [From onset to resolution; in hours, days, weeks, or months]                                                                               |
| Magnitude        | [Key quantitative data — units and dimensions vary by domain: peak decline % / opinion polarisation index / peak prevalence / adoption rate] |
| Resolution       | [How the episode ended: policy intervention, natural correction, bankruptcy, herd immunity, norm collapse, etc.]                            |
| Sources          | [Primary sources for this section: regulatory reports, academic papers, articles]                                                          |

#### N.2 Chronological Dynamics

| Date / Period | Event                                             | Environment Effect                    | Quantitative Measure           |
|---------------|---------------------------------------------------|---------------------------------------|--------------------------------|
| [Date]        | [What happened — specific action or announcement] | [State-variable effect for this domain] | [Number with units and source] |
| [Date]        | [Event]                                           | [Effect]                              | [Measure]                      |
| [Date]        | ...                                               | ...                                   | ...                            |

**Narrative**: [3–5 sentences describing the episode's progression in plain language, tying together the timeline entries above. What made this event escalate? What eventually halted it?]

#### N.3 Quantitative Evidence

[Specific data points with sources. Each bullet must include a number, a unit, and a full source citation.]

- [Metric]: [Value] ([Source: Author/Org, Year, report title or URL, page if applicable])
- [Metric]: [Value] ([Source])
- [Metric]: [Value] ([Source])

Minimum 4 quantitative data points per event.

#### N.4 Agent Mappings

| Simulation Agent | Real-World Counterpart              | Evidence for Mapping                                                       | Behavioural Correspondence                                                     |
|------------------|-------------------------------------|----------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| [ClassName §4.N] | [Real institution/participant type] | [Quote, regulatory filing, or academic analysis establishing this mapping] | [Specific behaviour in the real event that matches the agent's decision logic] |
| [ClassName §4.N] | [Real counterpart]                  | [Evidence]                                                                 | [Correspondence]                                                               |

#### N.5 Simulation Calibration Lessons

[What specific parameter values, timing, or behavioural patterns from this event should inform simulation calibration. Be precise: cite the quantitative evidence from §N.3 and connect it to specific parameters in §6.]

| Parameter (§6) | Historical Value from This Event | Source     | Calibration Implication              |
|----------------|----------------------------------|------------|--------------------------------------|
| [param_name]   | [Value from historical data]     | [Citation] | [How to set or bound this parameter] |

#### N.6 Distinguishing Features

[What makes this specific episode unique compared to other events in this catalogue? What aspect of the simulation does this event best validate? What is the most important lesson this event provides that is NOT captured by other events in the list?]

#### N.7 References for This Case

| # | Full Citation                                               | Content Referenced                          |
|---|-------------------------------------------------------------|---------------------------------------------|
| 1 | [Author(s)/Org, Year. "Title." Journal/Report. DOI or URL.] | [Which part of this case entry it supports] |
| 2 | ...                                                         | ...                                         |
```

**§8 Quality criteria**:
- §N.3 Quantitative Evidence: every data point must have a number, unit, and source. Vague phrases like "significant" or "notable" without a number are not acceptable.
- §N.4 Agent Mappings: every simulation agent must appear in at least one case's mapping table across the full §8. If an agent has no historical counterpart in any documented event, its design must be re-examined.
- §N.5 Calibration Lessons: must close the loop between historical data and §6 parameter values. This section makes §8 actionable, not merely illustrative.
- Events in the catalogue should collectively cover all agent types from §4 — i.e., each agent type should be mapped to at least one real-world counterpart across the full set of cases.

---

### §9 Variant Comparison Preview

Populate the columns of the table below with the variants declared `Yes`
in target §10.1 (in the target-file variant scheme's canonical order —
commonly `Rule / LLM / RuleLLM / Rag`, but the target file MAY declare
any subset or extension). The illustrative row content below assumes the
common `Rule / LLM / RuleLLM / Rag` scheme as an example; adapt to the
actual variants of the scenario.

```markdown
## 9. Variant Comparison Preview

| Aspect                        | {V1 — baseline}                                | {V2}                                | {V3}                             | {V4}                                          |
|-------------------------------|------------------------------------------------|-------------------------------------|----------------------------------|-----------------------------------------------|
| Decision Logic                | [e.g., Fixed formulas]                         | [e.g., Persona + LLM reasoning]     | [e.g., Formula-anchored LLM]     | [e.g., Retrieval-augmented LLM]               |
| Determinism                   | [Fully deterministic / Stochastic / Semi-...]  | [...]                               | [...]                            | [...]                                         |
| Expected Phenomenon Intensity | [Calibration target]                           | [Expected range; direction vs V1]   | [Direction vs V1]                | [Direction vs V3]                             |
| Key Behavioral Difference     | Baseline reference                             | [Specific behavioural difference]   | [Specific difference]            | [Specific difference]                         |
| Research Question             | Does the phenomenon emerge from V1 alone?      | [V2-specific question]              | [V3-specific question]           | [V4-specific question]                        |

**Predicted Ordering**: [E.g., "Expected phenomenon intensity: {V1} ≥ {V3} > {V2} > {V4} because ..."]
```

---

## Part II: `analysis-bases.md` — Analysis Methodology Foundation

**Location**: `examples/{SimulationName}/analysis-bases.md`

**Writing principle**: Write this document alongside `simulation-bases.md`, before implementing `analysis.py`. Every metric in §2 must be implemented in every variant's `analysis.py`. §6 calibration targets must cite specific literature values.

---

### §1 Analysis Objectives

```markdown
# {SimulationName} — Analysis Methodology Basis

## 1. Analysis Objectives

| Objective | Research Question                                         | Primary Metric(s)           | Expected Finding (from literature)       | Failure Indicator                           |
|-----------|-----------------------------------------------------------|-----------------------------|------------------------------------------|---------------------------------------------|
| O1        | [Specific question answerable by running this simulation] | [Which metric(s) answer it] | [What the literature predicts; citation] | [What would indicate a calibration failure] |
| O2        | ...                                                       | ...                         | ...                                      | ...                                         |
| O3        | ...                                                       | ...                         | ...                                      | ...                                         |
```

Minimum 3 objectives. Each must be answerable from simulation output — no vague objectives like "understand the phenomenon."

---

### §2 Core Metrics Catalogue

For EACH metric (minimum 6, including all mandatory types):

```markdown
### Metric: [Metric Name] ([Abbreviation])

#### Category
[State Dynamics / Volatility / Behavioral / Portfolio / Phenomenon-Specific / Agent Activity / Microstructure]

<!-- Domain-appendix instantiation — the "State Dynamics" category is renamed per the domain
     appendix invoked in `simulation-bases.md §4.1`. Finance appendix (§4.1.F): "Price Dynamics".
     Opinion appendix (§4.1.O): "Opinion Dynamics". Epidemics appendix (§4.1.E): "Prevalence
     Dynamics". Sociology appendix (§4.1.S): "Adoption Dynamics". Author picks the label and keeps
     it consistent across §2 and §3. -->

#### Definition
[Complete, unambiguous plain-language definition. No ambiguity allowed. State what is being
measured, over what time window, and with respect to what baseline or reference value.]

#### Formula
```
[Equation in precise, unambiguous notation — define every symbol]
where:
  [symbol] = [complete definition including units and computation method]
  [symbol] = [definition]
```

**Computation notes**: [How to compute this from raw simulation output. Which data files / fields
are inputs. Any edge cases — e.g., "If the reference anchor value is 0, return NaN" (finance
appendix instantiation: "If fundamental = 0, return NaN").]

#### Interpretation

| Range                           | Domain Meaning                                        | Simulation Interpretation                       |
|---------------------------------|-------------------------------------------------------|-------------------------------------------------|
| = 0                             | [What zero means theoretically]                       | [What it means in this simulation specifically] |
| (0, threshold_low)              | [Low value meaning]                                   | [Simulation meaning]                            |
| [threshold_low, threshold_high] | [Normal range meaning]                                | [Expected during normal phase]                  |
| > threshold_high                | [High value meaning — what phenomenon this indicates] | [Which phase; which agents active]              |

<!-- The "Domain Meaning" header is the domain-neutral term. Finance appendix (§4.1.F) may relabel
     it "Economic Meaning"; opinion / epidemics / sociology appendices use their own domain
     vocabulary (e.g., "Belief Meaning", "Epidemiological Meaning", "Adoption Meaning"). -->

#### Academic Basis

**Primary source**:
[Full citation: Author(s), Year. "Title." *Journal*, Vol(Issue), Pages. DOI.]

[2–3 sentences: How does this source establish this metric? Was it proposed here, validated here,
or applied in the same phenomenal context? Does the cited paper define the formula exactly as
written above, or is there an adaptation?]

**Supporting studies**:

| Study                                     | Context                     | Finding               | Relevance to This Metric                            |
|-------------------------------------------|-----------------------------|-----------------------|-----------------------------------------------------|
| [Author(s), Year. "Title." Journal. DOI.] | [Setting, period, geography] | [Quantitative result] | [Why this validates the metric for this simulation] |
| [Study 2]                                 | ...                         | ...                   | ...                                                 |

#### Normal Range (from literature)
[Typical values for this metric type in the relevant phenomenon literature. Be specific to the
domain of this simulation. Examples: finance — "Bubble duration in stock markets: 12–24 months
(Hong & Stein, 2003); in housing markets: 3–7 years (Glaeser et al., 2008)."; opinion dynamics —
"Consensus time in bounded-confidence models: 100–500 iterations for N=100 agents (Deffuant et al.,
2000)."; epidemics — "Peak prevalence for SIR with R₀=2.5: 15–25% of population (Kermack &
McKendrick, 1927; contemporary calibration Anderson & May, 1991)." Provide the range that would
indicate the simulation is producing realistic-scale output for this domain.]

#### Red Flag Threshold
- **Too high** (> [value]): [Diagnosis — which parameter is miscalibrated; direction to adjust]
- **Too low** (< [value]): [Diagnosis — adjustment direction]
- **Zero for all rounds**: [What this symptom indicates; immediate corrective action]

#### Relationship to Other Metrics
[How this metric relates to the others in §2. Does it correlate, diverge, or act as a leading
indicator of another metric? Example: "BAI typically peaks 3–5 rounds before BD crosses threshold;
if both peak simultaneously, the cascade is unusually fast and price_impact may be too high."]

#### Implementation Notes
[Which function in the analysis module of the baseline variant declared in target §10.1 (finance
default: `Rule/analysis.py`) computes this; input data source (state_history, agent_states,
action_history); return type and units.]
```

**Mandatory metrics** (must appear in every simulation's `analysis-bases.md`):

| # | Metric Type                                       | Rationale                                                             |
|---|---------------------------------------------------|-----------------------------------------------------------------------|
| 1 | State deviation from anchor / reference           | Primary phenomenon detection metric                                   |
| 2 | Phenomenon intensity measure                      | Phenomenon-specific (e.g., bubble ratio, crash depth, bias magnitude) |
| 3 | Volatility metric                                 | Rolling std of state changes or similar; required for risk assessment |
| 4 | Portfolio / wealth / outcome metric               | Tracks agent performance; enables cross-variant comparison            |
| 5 | Activity / volume metric                          | Interaction-intensity proxy; detects silent periods                   |
| 6 | ≥1 phenomenon-specific metric                     | Unique to this simulation — not present in generic phenomenon sims    |

<!-- Domain-appendix instantiation examples for Metric #1 and #5.
     Finance appendix (§4.1.F): #1 = "Price deviation from fundamental"; #5 = "Trading volume /
       intensity proxy".
     Opinion appendix (§4.1.O): #1 = "Opinion deviation from consensus / anchor"; #5 = "Number of
       pairwise interactions per round".
     Epidemics appendix (§4.1.E): #1 = "Prevalence deviation from steady-state / R₀ threshold";
       #5 = "New contact events per round".
     Sociology appendix (§4.1.S): #1 = "Adoption fraction deviation from equilibrium"; #5 =
       "Peer-to-peer transmission attempts per round". -->


---

### §3 Analysis Dimensions

Minimum 3 dimensions. Typical simulations cover all four listed below:

```markdown
### Dimension [N]: [Descriptive Name — e.g., "State Cascade Dynamics" (finance appendix: "Price
Cascade Dynamics"; opinion appendix: "Belief Polarization Dynamics"; epidemics appendix:
"Prevalence Rise/Fall Dynamics")]

**Purpose**: [One sentence: what specific question does this dimension answer?]

**Metrics Used**: [List from §2 — e.g., "State deviation, max drawdown, cascade volatility"]

**Visualization**:
- Plot type: [Line / Bar / Scatter / Histogram / Heatmap]
- X-axis: [What is plotted on X]
- Y-axis: [What is plotted on Y]
- Overlays: [Threshold lines, reference curves, phase annotations]
- File name: [e.g., `state_dynamics.png` — finance appendix instantiation `price_dynamics.png`]

**Expected Pattern**:
[What the chart should look like if the simulation works correctly.
Be specific: "State should cross the −15% deviation threshold by round 15–25 and remain
below it for 10–20 rounds before recovering." Finance instantiation: replace "State" with "Price".]

**Comparison Baseline**: [What to compare against — the baseline variant declared in target §10.1
(typically the deterministic / rule-based variant) as deterministic reference; historical data
from §8 of simulation-bases.md; theoretical prediction from §2 theory]

**Variant-Specific Interpretation Notes**:
Provide one bullet per variant declared under `target §10.1 Variant Build Matrix`. Use the exact
variant labels from that section. Template (adjust to your variant scheme):

- {V1 — baseline, e.g., Rule}: [What to expect specifically for the baseline variant]
- {V2, e.g., LLM}: [What this variant adds or changes in this dimension relative to {V1}]
- {V3, e.g., RuleLLM}: [Expected difference from {V1}]
- {V4, e.g., Rag}: [Expected difference from {V3}]
```

---

### §4 Phase Analysis Framework

```markdown
## 4. Phase Analysis Framework

**Overview**: [Describe the lifecycle of the phenomenon in terms of distinct phases.]

| Phase | Name                    | Entry Condition    | Exit Condition       | Key Indicators       | Expected Duration |
|-------|-------------------------|--------------------|----------------------|----------------------|-------------------|
| 1     | [Onset / Pre-phase]     | [Metric threshold] | [Next threshold]     | [Observable signals] | [Round range]     |
| 2     | [Escalation / Active]   | ...                | ...                  | ...                  | ...               |
| 3     | [Peak / Maximum]        | ...                | ...                  | ...                  | ...               |
| 4     | [Resolution / Recovery] | ...                | Exit condition = end | ...                  | ...               |

**Phase Detection Algorithm**:
[Precise rule for automatically classifying each round into a phase from simulation output.
Example: "Phase 2 (Cascade Onset): first round t where deviation(t) < −0.10 and remains
below −0.10 for at least 3 consecutive rounds."]

**Phase Transition Sensitivity**:
[Which parameters most affect phase transition timing. This is critical for calibration.]
```

---

### §5 Cross-Variant Comparison Framework

```markdown
## 5. Cross-Variant Comparison Framework

**Normalization Protocol**:
[How to make metrics comparable across variants with potentially different run configurations.
Give a domain-neutral rule and (optionally) a domain-appendix example. Example (finance appendix
§4.1.F): "All metrics normalized using the same fundamental_value = 100.0 and initial_price =
100.0. Use percentages not absolute values." Example (opinion appendix §4.1.O): "All opinions
initialized on a common [0, 1] scale; report deviations as absolute values, not raw opinion
positions." Provide the normalization rule that lets metrics from every variant declared in
target §10.1 be compared on equal footing.]

**Statistical Test**:
[Which statistical test to use for cross-variant comparison; significance level.
Example: "Two-sample t-test on the primary phenomenon-intensity metric across 10 simulation runs
per variant; α = 0.05."]

**Primary Comparison Axes**:

| Axis                   | Measurement                       | Expected Ordering                                     | Research Implication                                  |
|------------------------|-----------------------------------|-------------------------------------------------------|-------------------------------------------------------|
| Phenomenon onset speed | Round of first threshold crossing | [Which variant is faster/slower; why]                 | [What this tells us about each variant type's effect] |
| Phenomenon intensity   | Peak metric value                 | [Expected ordering across variants declared in §10.1] | [Implication]                                         |
| Behavioral realism     | Qualitative trace analysis        | [Criteria for assessment]                             | [What "more realistic" means]                         |
| Decision quality       | Outcome distribution              | [Which variant performs better; for which agent type] | [Implication]                                         |

**Reporting Table Format**:
[Define the exact table structure that cross-variant comparison reports must use. Columns MUST
match the variants declared in target §10.1.]
```

---

### §6 Expected Results and Validation

```markdown
## 6. Expected Results and Validation

### 6.1 Expected Stylised Facts

For each stylised fact that this simulation is designed to reproduce, provide the quantitative
target, the literature source, and the verification method.

| Fact                                                                           | Quantitative Target                                                                                                            | Literature Source (full citation + DOI) | How to Verify in Simulation             | Failure Indicator                                 |
|--------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|-----------------------------------------|---------------------------------------------------|
| [Fact 1 — a specific, measurable stylised fact from the phenomenon literature] | [Specific range or threshold — finance example: "bubble peak ≥ 20% above fundamental"; opinion example: "cluster count = 2±1"] | [Author, Year, Journal, DOI]            | [Which metric, which phase, which plot] | [What would indicate this fact is NOT reproduced] |
| [Fact 2]                                                                       | ...                                                                                                                            | ...                                     | ...                                     | ...                                               |
| [Fact 3]                                                                       | ...                                                                                                                            | ...                                     | ...                                     | ...                                               |

Minimum 4 stylised facts. Each must be verifiable from simulation output within a single run.

### 6.2 Calibration Targets

| Metric     | Target Range | Lower Bound Source | Upper Bound Source | Adjustment if Below Range     | Adjustment if Above Range     |
|------------|--------------|--------------------|--------------------|-------------------------------|-------------------------------|
| [Metric A] | [Min, Max]   | [Full citation]    | [Full citation]    | [Which parameter + direction] | [Which parameter + direction] |
| [Metric B] | ...          | ...                | ...                | ...                           | ...                           |

**Calibration protocol**:
1. Run the baseline variant declared in target §10.1 (typically the deterministic / rule-based
   variant; finance instantiation: `Rule`) for 10 seeds with default parameters.
2. Compute the mean of each metric across runs.
3. Compare against target ranges above.
4. Adjust parameters using the guidance above.
5. Re-run and verify before proceeding to the remaining variants declared in target §10.1
   (finance instantiation: `LLM`, `RuleLLM`, `Rag`).

### 6.3 Cross-Variant Predictions

Based on the theoretical expectations from `simulation-bases.md §9`, state the expected direction
of metric change for each variant relative to the baseline variant. Column headers below use
`{V1..Vk}` placeholders and MUST be replaced with the exact variant labels declared in target
§10.1 (finance default: Rule / LLM / RuleLLM / Rag).

| Metric     | {V1 — Baseline}           | {V2} Expected                                   | {V3} Expected        | {V4} Expected        | Theoretical Basis                       |
|------------|---------------------------|-------------------------------------------------|----------------------|----------------------|-----------------------------------------|
| [Metric A] | [Baseline value or range] | [Higher / Lower / Similar — with justification] | [Expected direction] | [Expected direction] | [§2 theory that predicts this ordering] |

### 6.4 Validation Failure Signs

| Symptom                                                                                                                             | Diagnosis                    | Root Cause                                       | Corrective Action                                           |
|-------------------------------------------------------------------------------------------------------------------------------------|------------------------------|--------------------------------------------------|-------------------------------------------------------------|
| [Observable problem — e.g., "State never deviates > 10% from anchor" (finance instantiation: "Price never deviates > 10% from fundamental")] | [What this symptom tells us] | [Which parameter or mechanism is the root cause] | [Specific adjustment: parameter name, direction, magnitude] |
| [Symptom 2]                                                                                                                         | [Diagnosis]                  | [Root cause]                                     | [Action]                                                    |
| [Symptom 3]                                                                                                                         | ...                          | ...                                              | ...                                                         |
```

---

### §7 Visualization Catalogue

```markdown
## 7. Visualization Catalogue

| Plot Name | Type                         | X-axis  | Y-axis  | Overlays             | Generated By      | Purpose           |
|-----------|------------------------------|---------|---------|----------------------|-------------------|-------------------|
| [name]    | [Line/Bar/Scatter/Histogram] | [Field] | [Field] | [Lines, annotations] | [function_name()] | [What it reveals] |
```

**Minimum required plots** (every simulation must produce all of these):

0. **Agent Action Curves** (`00_agent_actions.png`) — X = round, Y = the primary action variable
   for this domain (finance appendix: bid price; opinion appendix: opinion position; epidemics
   appendix: contact rate); one coloured line per agent showing their action each round, plus the
   environment-state summary as a thick gold line and the reference / anchor value as a dashed
   green horizontal line. This is the headline chart that provides an immediate visual summary of
   all agent behaviour.

   <!-- Finance appendix (§4.1.F) instantiation:
        - Filename: `00_investor_bids.png`
        - Y-axis: "price"
        - Per-agent line: bid price each round
        - Gold line: market clearing price
        - Dashed green horizontal line: fundamental value -->

1. State (or primary observable) vs. reference / anchor over time — shows phenomenon emergence.
   Finance appendix: Price vs. Fundamental over time.
2. Phenomenon intensity metric over time — shows severity and lifecycle.
3. Agent-level performance / outcome comparison — agent-level analysis. Finance appendix:
   Investor / portfolio performance comparison.
4. Phase detection overlay on the primary state chart — shows phase transitions.
5. Cross-variant comparison summary (columns matching variants declared in target §10.1) —
   enables research conclusions.

---

## Authorship and Update Policy

- Both `simulation-bases.md` and `analysis-bases.md` are written **before any code** and updated after all variants are complete (especially §9 of simulation-bases.md).
- When agent parameters change (e.g., threshold updated in the config file `players.yml`), the corresponding entry in `simulation-bases.md §6` and any derived `explain.md` files must be updated immediately.
- When a new empirical finding contradicts a calibration value, update the citation AND the parameter value together — never update one without the other.
