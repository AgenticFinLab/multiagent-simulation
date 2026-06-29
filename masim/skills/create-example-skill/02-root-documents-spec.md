# Root Document Specifications

## Purpose

This file defines the complete content specifications for the two root-level documents that every simulation must have:

1. **`simulation-bases.md`** — 9-section theoretical and design foundation
2. **`analysis-bases.md`** — 7-section analysis methodology foundation

These documents are the single source of truth for their respective domains. Every variant implementation built per target §10.1 (`explain.md`, `analysis.md`, `players.py`, `analysis.py`) traces back to these documents.

---

## Part I: `simulation-bases.md` — Theoretical and Design Foundation

**Location**: `examples/{SimulationName}/simulation-bases.md`

**Writing principle**: Write this document **before any code**. It drives all implementation decisions. Every investor type defined here must have a corresponding class in every built variant's `players.py` (the subset of `Rule / LLM / RuleLLM / Rag` declared `Yes` in target §10.1). Every parameter value must have a source citation.

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

### §3 Market Design Principles

#### §3.1 Price Formation Model

```markdown
### 3.1 Price Formation Model

**Formula**:
```
P(t+1) = P(t) + λ · D(t) + γ · [F(t) − P(t)] + ε(t)
```

**Variable Definitions**:

| Symbol | Name                 | Definition                                              | Role in Phenomenon            |
|--------|----------------------|---------------------------------------------------------|-------------------------------|
| P(t)   | Current price        | Market price at start of round t                        | State variable                |
| D(t)   | Net demand           | Σ buy_quantity − Σ sell_quantity across all investors   | Drives price change           |
| F(t)   | Fundamental value    | Intrinsic value; [constant / grows at rate g per round] | Mean reversion anchor         |
| λ      | Price impact         | Sensitivity of price to net demand                      | [Calibrated value and source] |
| γ      | Mean reversion speed | Speed of correction toward F                            | [Calibrated value and source] |
| ε(t)   | Noise                | ~ N(0, σ²)                                              | Background randomness         |

**Calibration Rationale**:
For EACH parameter (λ, γ, σ):
- Typical empirical range: [from literature]
- Chosen value: [specific value]
- Source: [full citation]
- Sensitivity: [High/Medium/Low — what changes if this parameter is varied ±50%]

**Economic Rationale**:
[Why each term is included. Why this combination of λ and γ is chosen to produce the target phenomenon.
For example: "High λ + low γ creates bubble-prone dynamics because demand shocks are amplified
and mean reversion is too slow to correct them within the simulation time horizon."]

**Dynamic Properties**:
- When D(t) > 0: [what happens to price; which agents drive this]
- When D(t) < 0: [what happens; cascade implications if applicable]
- When P >> F: [mean reversion magnitude; which agents activate]
- When P << F: [recovery mechanics; which agents activate]
- Noise effect: [what it represents economically; how it prevents determinism]
```

#### §3.2 Additional Market Mechanisms

For EACH mechanism beyond the price formula:

```markdown
**[Mechanism Name]**:
- Trigger: [Precise condition — e.g., "equity_ratio < 0.70" or "deviation < −0.15"]
- Action: [What the market does — prevent, force, cap, add cost]
- Economic Rationale: [Why this mechanism exists in real markets; which institution enforces it]
- Source: [Citation for the real-world institution/regulation that motivates this]
- Simulation Implementation: [How it is encoded in `_clear_market()` or other Market method]
```

#### §3.3 Information Broadcast Design

```markdown
### 3.3 Information Broadcast Design

Each round, the Market broadcasts to all investors:

| Field         | Type   | Definition                                | Rationale for Inclusion                 |
|---------------|--------|-------------------------------------------|-----------------------------------------|
| `price`       | float  | Current market price after order clearing | Primary signal for all agents           |
| `fundamental` | float  | Intrinsic fundamental value               | Required by value-sensitive agents      |
| `deviation`   | float  | (price − fundamental) / fundamental       | Pre-computed; used by most agents       |
| `round`       | int    | Current round number                      | Needed for frequency-controlled traders |
| [field]       | [type] | [definition]                              | [why included, which agents use it]     |

**Design Notes**:
[Explain any deliberate exclusions — e.g., "return_pct is NOT broadcast; all agents reference deviation only — this is consistent with relative value framing." Explain any unusual inclusions.]
```

---

### §4 Investor Taxonomy — Conformance to the Universal Agent Design Handbook

**Authoritative standard.** Every investor entry in `simulation-bases.md §4`
MUST conform to the **Universal Agent Design Handbook** at
`masim/skills/agent-design-skill.md`. The handbook is the single source of
truth for the intrinsic specification of any participant agent, in any
scenario domain. This section therefore does NOT repeat the handbook's
section schema — it states only how the handbook is applied inside
`simulation-bases.md`.

**Critical exclusions.** Section §4 MUST NOT contain any of the following —
they belong to each variant's `explain.md §2`:

- `Rule-Based Behavior` (IF/THEN code logic, executable thresholds)
- `LLM Persona` (prompt personality text, signal-interpretation guidelines)
- `RuleLLM Hybrid Notes` (embedded rule text for prompts)

The §4 entry defines **what the investor IS** at the design layer. Each
variant's `explain.md §2` defines **how that variant encodes it**.

---

#### 4.0 How the Universal Handbook Applies Inside simulation-bases.md

Each investor entry occupies one block that conforms section-for-section to
the handbook's **11-section canonical order** (`agent-design-skill.md §2`),
plus one **financial-domain extension** — `Population and Heterogeneity` —
inserted at position `4.{N}.7` to capture how multiple instances of the same
archetype are calibrated and sampled. Header levels are **shifted down by
two** to fit the embedding context, so that the investor's Title (handbook
`#`) lands at `###` inside `simulation-bases.md §4`, the handbook's `##`
sections land at `####`, and the handbook's `####` sub-blocks land at
`######`. All other content — field schemas, table column names, validation
requirements, RFC-2119 modal verbs — applies unchanged.

| Inside this file (embedded)                           | Handbook canonical level (standalone)       | Handbook section name                 |
|-------------------------------------------------------|---------------------------------------------|---------------------------------------|
| `### Investor: {ClassName}`                           | `# <agent role description>`                | Title                                 |
| `#### 4.{N}.1 Summary`                                | `## Summary`                                | Summary (7 fixed rows)                |
| `#### 4.{N}.2 Definition and Goals`                   | `## Definition and Goals`                   | Definition and Goals (3 paragraphs)   |
| `#### 4.{N}.3 Theoretical Foundation`                 | `## Theoretical Foundation`                 | Theoretical Foundation (≥1 sub-block) |
| `#### 4.{N}.4 Design Purpose and Activation Triggers` | `## Design Purpose and Activation Triggers` | Activation / Deactivation / Regime    |
| `#### 4.{N}.5 Behavioral Framework`                   | `## Behavioral Framework`                   | 5 H4 sub-blocks (see below)           |
| `#### 4.{N}.6 Parameters`                             | `## Parameters`                             | 8-column parameter table              |
| `#### 4.{N}.7 Population and Heterogeneity`           | *(financial-domain extension — not in handbook §3 canonical order; see §4.0 below)* | 5-row population table                |
| `#### 4.{N}.8 Worked Numerical Examples`              | `## Worked Numerical Examples`              | ≥3 cases + 1 edge case                |
| `#### 4.{N}.9 Validation and Calibration`             | `## Behavioral Verification and Calibration` | Includes Ablation Hooks               |
| `#### 4.{N}.10 Academic References`                   | `## Academic References`                    | Numbered citation table               |
| `#### 4.{N}.11 Design Provenance and Versioning`      | `## Design Provenance and Versioning`       | 6-row provenance footer               |

The Behavioral Framework's five sub-blocks are placed at `######` in the
embedded form: `4.{N}.5.1 Decision Information Set`, `4.{N}.5.2 Core
Behavioral Mechanism`, `4.{N}.5.3 Action Space`, `4.{N}.5.4 Mathematical
Model`, `4.{N}.5.5 Behavioral Properties`. `{N}` is a 1-based index inside
`simulation-bases.md §4` (so `4.1.5.3 Action Space` is the Action Space of
the first investor).

---

#### 4.1 Domain Instantiation for Financial Scenarios

`simulation-bases.md` describes a **market-trading scenario**. The handbook's
domain-neutral row labels and value palettes are therefore instantiated for
the financial domain inline below. (Earlier drafts referenced a separate
`agent-design-finance.md` file — that file is intentionally not maintained;
the instantiation rules live here and are the single source of truth.)

**4.1.1 Theory Family palette (pick one per investor)**

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

**4.1.2 Real-world counterpart enumeration (pick one per investor)**

`Retail investor` · `Active retail trader` · `Hedge fund (long/short)` ·
`Hedge fund (event-driven)` · `Quant fund / CTA` · `Mutual fund / pension` ·
`Asset manager (index)` · `Family office` · `Proprietary trading desk` ·
`Sell-side market maker` · `High-frequency market maker` ·
`Prime broker / dealer` · `Corporate / strategic buyer` ·
`Central bank / sovereign` · `Insurance / annuity` ·
`Crypto-native trader` · `Social-media-driven retail community`.

If no entry fits, an investor MAY supply a more specific counterpart, but
MUST cite at least one peer-reviewed paper or regulatory report that
documents that participant class.

**4.1.3 Stylized-fact catalogue (pick the ones this agent helps produce)**

Volatility clustering · Fat tails of returns · Leverage effect ·
Short-horizon momentum (3-12 month) · Long-horizon reversal (3-5 year) ·
Bid-ask bounce · Trade-size / volume autocorrelation ·
Price-impact concavity (square-root law) · Volume spikes around news ·
Liquidity black holes · Flash-crash signatures · Persistent bubble
deviation > fundamental · Capitulation tail · Co-movement in factor
returns · Cross-sectional herding patterns.

Stylized facts cited in §4.{N}.2 (Definition and Goals, paragraph 3)
MUST come from this catalogue or be supplied with a primary citation.

**4.1.4 Regime palette and relabel rules**

The handbook's `Behavioral Adaptation by Condition` table is **relabelled**
in the embedded form to `Market Contribution by Regime` (since the embedded
form is scoped to market scenarios). Use regime labels from the following
palette (4-8 per investor depending on scenario):

`Calm market` · `Trending market (up)` · `Trending market (down)` ·
`High-volatility regime` · `Liquidity stress / drought` ·
`Bubble inflation` · `Post-peak deflation` · `Crash / cascade` ·
`Post-shock recovery` · `News-driven regime` · `Earnings/macro window`.

Also: the handbook Summary row labelled `Behavioral Tendency` is
**relabelled** to `Market Role` with values `Stabilising` /
`Destabilising` / `Context-dependent` — a one-line rationale required.

**4.1.5 Action Space row labels (market-trading instantiation)**

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
belong to §3 Market Design.

**4.1.6 What stays unchanged from the handbook**

All other handbook fields apply verbatim, including the 8-column
Parameters table, the per-theory citation block (Calibration Source,
Falsification Conditions, Alternative Theories), the Mathematical
Model with State-Update Rule and Determinism Contract, and the
Behavioral Verification + Ablation Hooks section.

Authors MUST NOT introduce new top-level fields not specified in the
handbook, and MUST NOT omit any handbook section. If an investor
genuinely exposes zero tunable parameters, the Parameters section MUST
contain the literal phrase `_No tunable parameters._` per handbook §3.7.

---

#### 4.2 Per-Investor Block Skeleton (Embedded Form)

Use the handbook's section-by-section schema
(`agent-design-skill.md §3 Section-by-Section Requirements`) as the
structural skeleton for each investor entry, then re-level it from standalone
to embedded form per the table in §4.0 above. The minimum number of investor
entries is **4**; the maximum is **7**.

The block layout for one investor in `simulation-bases.md` is:

```markdown
### Investor: {ClassName}

#### 4.{N}.1 Summary

| Field                 | Content                                                                  |
|-----------------------|--------------------------------------------------------------------------|
| Archetype             | <one-line role phrase, matches the H3>                                   |
| Theory Family         | <Behavioral Finance / Microstructure / Information Cascade / Quant ...>  |
| Market Role           | **Destabilising** / **Stabilising** / **Context-dependent** — <one-line> |
| Time Horizon          | <short / medium / long>                                                  |
| Risk Tolerance        | <low / medium / high>                                                    |
| Information Asymmetry | <none / partial / full>                                                  |
| Determinism           | <deterministic / stochastic-given-seed / non-deterministic>              |

#### 4.{N}.2 Definition and Goals
<3 short paragraphs (8–14 sentences total) per handbook §3.3:
(1) what the investor models, with a named real-world counterpart;
(2) decision goal: action, sizing, price level, criterion;
(3) role inside the simulation, named stylized facts produced, explicit non-goals.>

#### 4.{N}.3 Theoretical Foundation
<≥1 theory sub-block per handbook §3.4. Each sub-block MUST include:
Theory / Study, Citation (with DOI), Core Insight, Mathematical
Formulation, Empirical Evidence, Relevance to This Agent, Calibration
Source, Falsification Conditions, Alternative Theories.>

#### 4.{N}.4 Design Purpose and Activation Triggers
<Per handbook §3.5: Purpose, Call Frequency, Prerequisite Signals,
Missing-Signal Policy, Activation Triggers (with `<Default>`),
Deactivation Conditions, Market Contribution by Regime (≥2 rows),
Interaction sentence.>

#### 4.{N}.5 Behavioral Framework

##### 4.{N}.5.1 Decision Information Set
<Signal table (Signal, Type, Memory Window, Rationale) + explicit
"Does NOT use" line — per handbook §3.6.1.>

##### 4.{N}.5.2 Core Behavioral Mechanism
<5–10 numbered steps in plain English mixed with formulas; no code in any
specific programming language — per handbook §3.6.2.>

##### 4.{N}.5.3 Action Space
<8-row aspect table using the market-trading labels listed in §4.1 above.
Environment-imposed limits (matching engine, tick grid, fees, latency,
regulator-imposed caps) MUST NOT appear here — per handbook §3.6.3.>

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
§4.{N}.3 Calibration Source or to the Source column. If the investor exposes
zero tunable parameters, write `_No tunable parameters._`.>

#### 4.{N}.7 Population and Heterogeneity
<5-row population table (financial-domain extension; not part of handbook §3
canonical order): Default population size, Parameter heterogeneity policy,
Heterogeneity per parameter, Cross-agent correlation, Identity persistence.>

#### 4.{N}.8 Worked Numerical Examples
<≥3 primary cases covering distinct trigger branches + ≥1 edge case
(cold-start, extreme deviation, deactivation condition, inventory clamp,
regime flip, or missing-signal fallback). Each case MUST show market state,
step-by-step calculation, decision, and state update — per handbook §3.8.>

#### 4.{N}.9 Validation and Calibration
<Per handbook §3.9 "Behavioral Verification and Calibration": Calibration
data sources (per parameter), Expected stylized facts when this agent
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

#### 4.3 Per-Investor Validation

For each investor entry, run the handbook's **Validation Checklist**
(`agent-design-skill.md §6`) against the entry. Every unchecked item is a
blocker. The same checklist applies regardless of whether the agent will
later be realised as a Rule, LLM, RuleLLM, or Rag variant.

Cross-investor diversity verification (different time horizons, conflicting
incentives, distinct information sets) is performed in §5 of this file and
is orthogonal to the per-investor handbook checklist.

---

### §5 Agent Diversity Verification

```markdown
## 5. Agent Diversity Verification

| Diversity Criterion              | Met? | Evidence                                                                                                    |
|----------------------------------|------|-------------------------------------------------------------------------------------------------------------|
| Different time horizons          | Yes  | [List: e.g., "ConcentratedFund: medium-term; PrimeBroker1: high-frequency; BlockTradeBuyer: opportunistic"] |
| Different information processing | Yes  | [Which agents use which signals differently]                                                                |
| Conflicting incentives           | Yes  | [Which agents buy when others sell; example scenario]                                                       |
| Mix of stabilizing/destabilizing | Yes  | [Count and names; ratio should be ≥1 stabilizing per 2 destabilizing]                                       |
| Different risk tolerances        | Yes  | [Range: from Low to Extreme; examples]                                                                      |
| Different decision frequencies   | Yes  | [Examples of high-frequency vs. low-frequency actors]                                                       |

**Critical mass check**: [Explain why this investor set is sufficient to produce the target phenomenon.
What is the minimum subset of agents needed? What would break if one type were removed?]
```

---

### §6 Parameter Table

```markdown
## 6. Parameter Table

| Parameter         | Symbol | Value | Typical Range    | Source Citation | Description                      | Sensitivity      |
|-------------------|--------|-------|------------------|-----------------|----------------------------------|------------------|
| initial_price     | P(0)   | [val] | [range]          | [Full citation] | Starting asset price             | Low — scale only |
| fundamental_value | F      | [val] | [range]          | [Full citation] | Intrinsic value baseline         | Medium           |
| price_impact      | λ      | [val] | [range from lit] | [Full citation] | Price change per unit net demand | High             |
| mean_reversion    | γ      | [val] | [range from lit] | [Full citation] | Attraction speed toward F        | High             |
| noise_std         | σ      | [val] | [range]          | [Full citation] | Noise term standard deviation    | Low              |
| [agent param]     | [sym]  | [val] | [range]          | [Full citation] | [Meaning]                        | [High/Med/Low]   |
```

**Quality criteria**:
- Every numeric value must have a source citation that is a real, published work (not "normalization" except for scale-only parameters).
- The Typical Range column must come from the literature, not be invented.
- The Sensitivity column must describe what happens quantitatively, not just say "important."

---

### §7 Communication and Round Structure

```markdown
## 7. Communication and Round Structure

```
Round N (t = 1, 2, ..., T):

  Phase 1 — Market Broadcast:
    Market → all investors: {price, fundamental, deviation, round, [other fields]}
    This message triggers perceive() in all investors simultaneously.

  Phase 2 — Investor Decisions:
    For each investor i:
      perceive(): extract and store market data in custom_state
      decide():   apply strategy (deterministic rule / LLM call / RAG-augmented LLM call)
      act():      construct order message

  Phase 3 — Order Submission:
    Each investor → Market: {action: buy/sell/hold, quantity: Q, bid_price: P}

  Phase 4 — Market Clearing:
    Market.perceive(): collect all orders
    Market.decide():   compute D(t), apply price formula P(t+1) = ...
    Market.act():      broadcast updated state → triggers next round

  Phase 5 — Logging:
    Record market state, all investor states, and orders to EXPERIMENT/.../records/
```

**Round duration interpretation**: [What real-world time period does one round represent?
E.g., "Each round represents one trading day." Justify this choice.]

**Synchronous vs. asynchronous**: [Are agents processing simultaneously? Any ordering dependencies?]
```

---

### §8 Historical Case Studies

**Purpose**: Section §8 is the empirical grounding of the simulation. It connects the abstract agent-based model to documented real-world episodes, establishes calibration targets derived from historical data, and populates the RAG variant's knowledge base. A simulation without this section cannot be externally validated.

**Minimum**: 2 events. **Recommended**: 3–5, spanning different time periods, markets, and geographic regions to demonstrate the phenomenon's generality.

For EACH real-world event:

```markdown
## 8. Historical Case Studies

### Case N: [Full Event Name]

#### N.1 Event Profile

| Item       | Detail                                                                              |
|------------|-------------------------------------------------------------------------------------|
| Date Range | [Specific dates or period, e.g., "March 24–29, 2021"; "August–October 1987"]        |
| Market     | [Asset class, exchange, geographic scope, e.g., "US equity markets, NYSE + NASDAQ"] |
| Trigger    | [The specific catalyst — precise and verifiable, not generic]                       |
| Duration   | [From onset to resolution; in hours, days, weeks, or months]                        |
| Magnitude  | [Key quantitative data: peak decline %, total loss in $, volatility spike in bps]   |
| Resolution | [How the episode ended: policy intervention, natural correction, bankruptcy, etc.]  |
| Sources    | [Primary sources for this section: regulatory reports, academic papers, articles]   |

#### N.2 Chronological Dynamics

| Date / Period | Event                                             | Market Effect                | Quantitative Measure           |
|---------------|---------------------------------------------------|------------------------------|--------------------------------|
| [Date]        | [What happened — specific action or announcement] | [Price/volume/spread effect] | [Number with units and source] |
| [Date]        | [Event]                                           | [Effect]                     | [Measure]                      |
| [Date]        | ...                                               | ...                          | ...                            |

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
- §N.3 Quantitative Evidence: every data point must have a number, unit, and source. "Prices fell significantly" is not acceptable.
- §N.4 Agent Mappings: every simulation agent must appear in at least one case's mapping table across the full §8. If an agent has no historical counterpart in any documented event, its design must be re-examined.
- §N.5 Calibration Lessons: must close the loop between historical data and §6 parameter values. This section makes §8 actionable, not merely illustrative.
- Events in the catalogue should collectively cover all investor types from §4 — i.e., each investor type should be mapped to at least one real-world counterpart across the full set of cases.

---

### §9 Variant Comparison Preview

```markdown
## 9. Variant Comparison Preview

| Aspect                        | Rule                                         | LLM                                 | RuleLLM                          | Rag                                           |
|-------------------------------|----------------------------------------------|-------------------------------------|----------------------------------|-----------------------------------------------|
| Decision Logic                | Fixed formulas                               | Persona + LLM reasoning             | Formula-anchored LLM             | RAG-augmented LLM                             |
| Determinism                   | Fully deterministic                          | Stochastic                          | Semi-deterministic               | Stochastic                                    |
| Expected Phenomenon Intensity | [Calibration target]                         | [Expected range; direction vs Rule] | [Near-Rule; deviation from Rule] | [Modified by knowledge; direction vs RuleLLM] |
| Key Behavioral Difference     | Baseline reference                           | [Specific behavioral difference]    | [Specific difference]            | [Specific difference]                         |
| Research Question             | Does the phenomenon emerge from rules alone? | [LLM-specific question]             | [RuleLLM-specific question]      | [RAG-specific question]                       |

**Predicted Ordering**: [E.g., "Expected phenomenon intensity: Rule ≥ RuleLLM > LLM > Rag because ..."]
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
[Price Dynamics / Volatility / Behavioral / Portfolio / Phenomenon-Specific / Agent Activity / Microstructure]

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
are inputs. Any edge cases — e.g., "If fundamental = 0, return NaN."]

#### Interpretation

| Range                           | Economic Meaning                                      | Simulation Interpretation                       |
|---------------------------------|-------------------------------------------------------|-------------------------------------------------|
| = 0                             | [What zero means theoretically]                       | [What it means in this simulation specifically] |
| (0, threshold_low)              | [Low value meaning]                                   | [Simulation meaning]                            |
| [threshold_low, threshold_high] | [Normal range meaning]                                | [Expected during normal phase]                  |
| > threshold_high                | [High value meaning — what phenomenon this indicates] | [Which phase; which agents active]              |

#### Academic Basis

**Primary source**:
[Full citation: Author(s), Year. "Title." *Journal*, Vol(Issue), Pages. DOI.]

[2–3 sentences: How does this source establish this metric? Was it proposed here, validated here,
or applied in the same phenomenal context? Does the cited paper define the formula exactly as
written above, or is there an adaptation?]

**Supporting studies**:

| Study                                     | Context          | Finding               | Relevance to This Metric                            |
|-------------------------------------------|------------------|-----------------------|-----------------------------------------------------|
| [Author(s), Year. "Title." Journal. DOI.] | [Market, period] | [Quantitative result] | [Why this validates the metric for this simulation] |
| [Study 2]                                 | ...              | ...                   | ...                                                 |

#### Normal Range (from literature)
[Typical values for this metric type in the relevant phenomenon literature. Be specific:
e.g., "Bubble duration in stock markets: 12–24 months (Hong & Stein, 2003); in housing markets:
3–7 years (Glaeser et al., 2008)." Provide the range that would indicate the simulation is
producing realistic-scale output.]

#### Red Flag Threshold
- **Too high** (> [value]): [Diagnosis — which parameter is miscalibrated; direction to adjust]
- **Too low** (< [value]): [Diagnosis — adjustment direction]
- **Zero for all rounds**: [What this symptom indicates; immediate corrective action]

#### Relationship to Other Metrics
[How this metric relates to the others in §2. Does it correlate, diverge, or act as a leading
indicator of another metric? Example: "BAI typically peaks 3–5 rounds before BD crosses threshold;
if both peak simultaneously, the cascade is unusually fast and price_impact may be too high."]

#### Implementation Notes
[Which function in `Rule/analysis.py` computes this; input data source (price_history, agent_states,
trade_history); return type and units.]
```

**Mandatory metrics** (must appear in every simulation's `analysis-bases.md`):

| # | Metric Type                      | Rationale                                                             |
|---|----------------------------------|-----------------------------------------------------------------------|
| 1 | Price deviation from fundamental | Primary phenomenon detection metric                                   |
| 2 | Phenomenon intensity measure     | Phenomenon-specific (e.g., bubble ratio, crash depth, bias magnitude) |
| 3 | Volatility metric                | Rolling std of returns or similar; required for risk assessment       |
| 4 | Portfolio / wealth metric        | Tracks agent performance; enables cross-variant comparison            |
| 5 | Volume or activity metric        | Trading intensity proxy; detects silent periods                       |
| 6 | ≥1 phenomenon-specific metric    | Unique to this simulation — not present in generic bubble/crash sims  |

---

### §3 Analysis Dimensions

Minimum 3 dimensions. Typical simulations cover all four listed below:

```markdown
### Dimension [N]: [Descriptive Name — e.g., "Price Cascade Dynamics"]

**Purpose**: [One sentence: what specific question does this dimension answer?]

**Metrics Used**: [List from §2 — e.g., "Price deviation, max drawdown, cascade volatility"]

**Visualization**:
- Plot type: [Line / Bar / Scatter / Histogram / Heatmap]
- X-axis: [What is plotted on X]
- Y-axis: [What is plotted on Y]
- Overlays: [Threshold lines, reference curves, phase annotations]
- File name: [e.g., `price_dynamics.png`]

**Expected Pattern**:
[What the chart should look like if the simulation works correctly.
Be specific: "Price should cross the −15% deviation threshold by round 15–25 and remain
below it for 10–20 rounds before recovering."]

**Comparison Baseline**: [What to compare against — Rule variant as deterministic reference;
historical data from §8 of simulation-bases.md; theoretical prediction from §2 theory]

**Variant-Specific Interpretation Notes**:
- Rule: [What to expect specifically for Rule variant]
- LLM: [What LLM adds or changes in this dimension]
- RuleLLM: [Expected difference from Rule]
- Rag: [Expected difference from RuleLLM]
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
Example: "All metrics normalized using the same fundamental_value = 100.0 and initial_price = 100.0.
Use percentages not absolute values."]

**Statistical Test**:
[Which statistical test to use for cross-variant comparison; significance level.
Example: "Two-sample t-test on max_drawdown across 10 simulation runs; α = 0.05."]

**Primary Comparison Axes**:

| Axis                   | Measurement                       | Expected Ordering                                     | Research Implication                      |
|------------------------|-----------------------------------|-------------------------------------------------------|-------------------------------------------|
| Phenomenon onset speed | Round of first threshold crossing | [Which variant is faster/slower; why]                 | [What this tells us about LLM/RAG effect] |
| Phenomenon intensity   | Peak metric value                 | [Expected ordering]                                   | [Implication]                             |
| Behavioral realism     | Qualitative trace analysis        | [Criteria for assessment]                             | [What "more realistic" means]             |
| Decision quality       | Portfolio outcome distribution    | [Which variant performs better; for which agent type] | [Implication]                             |

**Reporting Table Format**:
[Define the exact table structure that cross-variant comparison reports must use.]
```

---

### §6 Expected Results and Validation

```markdown
## 6. Expected Results and Validation

### 6.1 Expected Stylised Facts

For each stylised fact that this simulation is designed to reproduce, provide the quantitative
target, the literature source, and the verification method.

| Fact                                                                           | Quantitative Target                                                         | Literature Source (full citation + DOI) | How to Verify in Simulation             | Failure Indicator                                 |
|--------------------------------------------------------------------------------|-----------------------------------------------------------------------------|-----------------------------------------|-----------------------------------------|---------------------------------------------------|
| [Fact 1 — a specific, measurable stylised fact from the phenomenon literature] | [Specific range or threshold — e.g., "bubble peak ≥ 20% above fundamental"] | [Author, Year, Journal, DOI]            | [Which metric, which phase, which plot] | [What would indicate this fact is NOT reproduced] |
| [Fact 2]                                                                       | ...                                                                         | ...                                     | ...                                     | ...                                               |
| [Fact 3]                                                                       | ...                                                                         | ...                                     | ...                                     | ...                                               |

Minimum 4 stylised facts. Each must be verifiable from simulation output within a single run.

### 6.2 Calibration Targets

| Metric     | Target Range | Lower Bound Source | Upper Bound Source | Adjustment if Below Range     | Adjustment if Above Range     |
|------------|--------------|--------------------|--------------------|-------------------------------|-------------------------------|
| [Metric A] | [Min, Max]   | [Full citation]    | [Full citation]    | [Which parameter + direction] | [Which parameter + direction] |
| [Metric B] | ...          | ...                | ...                | ...                           | ...                           |

**Calibration protocol**:
1. Run the Rule variant for 10 seeds with default parameters.
2. Compute the mean of each metric across runs.
3. Compare against target ranges above.
4. Adjust parameters using the guidance above.
5. Re-run and verify before proceeding to LLM/RuleLLM/Rag variants.

### 6.3 Cross-Variant Predictions

Based on the theoretical expectations from `simulation-bases.md §9`, state the expected direction
of metric change for each variant relative to the Rule baseline.

| Metric     | Rule (Baseline)           | LLM Expected                                    | RuleLLM Expected     | Rag Expected         | Theoretical Basis                       |
|------------|---------------------------|-------------------------------------------------|----------------------|----------------------|-----------------------------------------|
| [Metric A] | [Baseline value or range] | [Higher / Lower / Similar — with justification] | [Expected direction] | [Expected direction] | [§2 theory that predicts this ordering] |

### 6.4 Validation Failure Signs

| Symptom                                                                    | Diagnosis                    | Root Cause                                       | Corrective Action                                           |
|----------------------------------------------------------------------------|------------------------------|--------------------------------------------------|-------------------------------------------------------------|
| [Observable problem — e.g., "Price never deviates > 10% from fundamental"] | [What this symptom tells us] | [Which parameter or mechanism is the root cause] | [Specific adjustment: parameter name, direction, magnitude] |
| [Symptom 2]                                                                | [Diagnosis]                  | [Root cause]                                     | [Action]                                                    |
| [Symptom 3]                                                                | ...                          | ...                                              | ...                                                         |
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

0. **Investor Bid Curves** (`00_investor_bids.png`) — X = round, Y = price; one coloured line per investor showing their bid price each round, plus the market clearing price as a thick gold line and the fundamental value as a dashed green horizontal line. This is the headline chart that provides an immediate visual summary of all agent behaviour.
1. Price vs. Fundamental over time — shows phenomenon emergence
2. Phenomenon intensity metric over time — shows severity and lifecycle
3. Investor/portfolio performance comparison — agent-level analysis
4. Phase detection overlay on price chart — shows phase transitions
5. Cross-variant comparison summary — enables research conclusions

---

## Authorship and Update Policy

- Both `simulation-bases.md` and `analysis-bases.md` are written **before any code** and updated after all variants are complete (especially §9 of simulation-bases.md).
- When agent parameters change (e.g., threshold updated in `players.yml`), the corresponding entry in `simulation-bases.md §6` and any derived `explain.md` files must be updated immediately.
- When a new empirical finding contradicts a calibration value, update the citation AND the parameter value together — never update one without the other.
